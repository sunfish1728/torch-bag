package dev.torchbag;

import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;

/** Time-sliced coarse connected-space torch placement. All world access stays on the server thread. */
public final class BombPlacer {
    private static final int CANDIDATES_PER_SLICE = 4096;
    private static final int PLACEMENTS_PER_SLICE = 16;
    private static final int MAX_QUEUE = 8;
    private static final long SLICE_NANOS = 2_000_000L;
    private static final Deque<Work> QUEUE = new ArrayDeque<>();
    private static final Map<UUID, Work> ACTIVE = new HashMap<>();
    private static final Deque<Recent> RECENT = new ArrayDeque<>();
    private static final Map<net.minecraft.resources.ResourceKey<Level>, Map<Long, List<Recent>>> RECENT_BY_DIMENSION = new HashMap<>();
    private static long clock;

    public static boolean release(ServerPlayer player, BombTier tier) {
        Work current = ACTIVE.get(player.getUUID());
        if (current != null) {
            player.displayClientMessage(Component.translatable("message.torch_bag.bomb_busy", current.percent()), true);
            return false;
        }
        if (ACTIVE.size() >= MAX_QUEUE) {
            player.displayClientMessage(Component.translatable("message.torch_bag.bomb_server_busy"), true);
            return false;
        }
        add(new Work(player, BlockPos.containing(player.getEyePosition()), tier.chunkRadius));
        return true;
    }
    static boolean releaseForTest(ServerPlayer player, int chunkRadius) {
        if (ACTIVE.containsKey(player.getUUID())) return false;
        add(new Work(player, BlockPos.containing(player.getEyePosition()), chunkRadius));
        return true;
    }
    private static void add(Work work) {
        ACTIVE.put(work.ownerId, work);
        QUEUE.addLast(work);
    }
    public static void tick(MinecraftServer server) {
        clock++;
        pruneRecent();
        Work work = QUEUE.pollFirst();
        if (work == null) return;
        if (work.step(server)) {
            QUEUE.addLast(work);
        } else {
            ACTIVE.remove(work.ownerId, work);
            work.closeBar();

        }
    }
    public static void cancel(UUID ownerId) {
        Work work = ACTIVE.remove(ownerId);
        if (work != null) { QUEUE.remove(work); work.closeBar(); }

    }
    public static void clear() {
        for (Work work : QUEUE) work.closeBar();
        QUEUE.clear(); ACTIVE.clear(); clearRecent();
    }
    static int pending() { return QUEUE.size(); }
    static int progress(UUID ownerId) { Work work = ACTIVE.get(ownerId); return work == null ? 100 : work.percent(); }

    static List<ChunkPos> chunkSpiral(BlockPos center, int chunkRadius) {
        ChunkPos origin = new ChunkPos(center);
        int side = chunkRadius * 2 + 1;
        List<ChunkPos> result = new ArrayList<>(side * side);
        int x = 0, z = 0, dx = 0, dz = -1;
        for (int i = 0; i < side * side; i++) {
            result.add(new ChunkPos(origin.x + x, origin.z + z));
            if (x == z || (x < 0 && x == -z) || (x > 0 && x == 1 - z)) {
                int oldDx = dx; dx = -dz; dz = oldDx;
            }
            x += dx; z += dz;
        }
        return List.copyOf(result);
    }

    private static boolean passable(BlockState state) {
        // Conservative whole-cell connectivity: never infer a gap through a solid cell.
        return state.getFluidState().isEmpty() && !state.blocksMotion();
    }
    private static boolean intersectsBorder(ServerLevel level, ChunkPos chunk) {
        var border = level.getWorldBorder();
        int minX = (int)Math.ceil(border.getMinX()), maxX = (int)Math.ceil(border.getMaxX()) - 1;
        int minZ = (int)Math.ceil(border.getMinZ()), maxZ = (int)Math.ceil(border.getMaxZ()) - 1;
        return chunk.getMaxBlockX() >= minX && chunk.getMinBlockX() <= maxX &&
            chunk.getMaxBlockZ() >= minZ && chunk.getMinBlockZ() <= maxZ;
    }

    /** Fixed coarse grid, plus the release column in the origin chunk. */
    private static final int[] SAMPLE_AXIS = {0, 4, 8, 12, 15};
    static int sampledColumnsForTest() { return 36; }
    static int sampledColumnsForTest(BlockPos center, ChunkPos chunk) {
        return sampleAxis(center.getX() & 15, new ChunkPos(center).equals(chunk)).length *
            sampleAxis(center.getZ() & 15, new ChunkPos(center).equals(chunk)).length;
    }
    private static int[] sampleAxis(int release, boolean origin) {
        if (!origin || Arrays.binarySearch(SAMPLE_AXIS, release) >= 0) return SAMPLE_AXIS;
        int[] result = Arrays.copyOf(SAMPLE_AXIS, SAMPLE_AXIS.length + 1);
        result[result.length - 1] = release; Arrays.sort(result); return result;
    }

    private static final class Work {
        final UUID ownerId;
        final java.lang.ref.WeakReference<ServerPlayer> testOwner;
        final net.minecraft.resources.ResourceKey<Level> dimension;
        final BlockPos center;
        final List<ChunkPos> chunks;
        // Only reachable boundaries remain after a chunk is placed. No world-sized
        // candidate collection or global connectivity graph is retained.
        final Map<Long, Boundary> boundaries = new HashMap<>();
        final ServerBossEvent bar;
        Analyzer analyzer;
        int chunkIndex, lastPercent = -1, storedPortals;
        boolean completed;

        Work(ServerPlayer owner, BlockPos center, int chunkRadius) {
            ownerId = owner.getUUID();
            testOwner = owner.connection == null || owner.getClass().getSimpleName().equals("FakePlayer")
                ? new java.lang.ref.WeakReference<>(owner) : null;
            dimension = owner.serverLevel().dimension();
            this.center = center.immutable();
            chunks = chunkSpiral(center, chunkRadius);
            bar = new ServerBossEvent(Component.translatable("message.torch_bag.bomb_progress", 0), BossEvent.BossBarColor.YELLOW, BossEvent.BossBarOverlay.PROGRESS);
            if (owner.connection != null) bar.addPlayer(owner);
            bar.setProgress(0F);
            owner.displayClientMessage(Component.translatable("message.torch_bag.bomb_started"), true);
        }
        ServerPlayer owner(MinecraftServer server) {
            ServerPlayer owner = server.getPlayerList().getPlayer(ownerId);
            if (owner == null && testOwner != null) owner = testOwner.get();
            return owner;
        }
        boolean step(MinecraftServer server) {
            ServerLevel level = server.getLevel(dimension);
            ServerPlayer owner = owner(server);
            if (level == null || owner == null || !owner.isAlive() || owner.serverLevel() != level) return false;
            long deadline = System.nanoTime() + SLICE_NANOS;
            int placed = 0, candidates = 0;
            boolean loadedMissing = false;
            // Already loaded chunks can share this slice. Any missing chunk may
            // require synchronous generation, so at most one is requested per slice.
            while (chunkIndex < chunks.size() && System.nanoTime() < deadline) {
                ChunkPos next = chunks.get(chunkIndex);
                if (!intersectsBorder(level, next)) {
                    analyzer = null; chunkIndex++; updateProgress(); continue;
                }
                boolean present = level.hasChunk(next.x, next.z);
                if (!present && loadedMissing) break;
                if (!present) loadedMissing = true;
                var loaded = level.getChunk(next.x, next.z);
                if (analyzer == null) analyzer = new Analyzer(level, loaded, center);
                else analyzer.loaded = loaded;
                if (!analyzer.prepare(level, this, deadline)) break;
                while (analyzer.placeIndex < analyzer.runs.size() && System.nanoTime() < deadline &&
                    placed < PLACEMENTS_PER_SLICE && candidates < CANDIDATES_PER_SLICE) {
                    Run run = analyzer.runs.get(analyzer.placeIndex++); candidates++;
                    if (!analyzer.reachable[analyzer.find(run.id)] || run.maxY <= run.minY || run.minY <= analyzer.minY) continue;
                    BlockPos pos = analyzer.position(run, run.minY);
                    if (!level.getWorldBorder().isWithinBounds(pos) || nearRecent(level, pos) || !AutoPlacer.darkFloor(level, pos)) continue;
                    BlockState state = AutoPlacer.placementState(level, pos);
                    if (state != null && Platform.place(owner, pos, state)) {
                        remember(level, pos);
                        level.playSound(null, pos, SoundEvents.WOOD_PLACE, SoundSource.BLOCKS, 0.5F, 1F);
                        level.gameEvent(owner, GameEvent.BLOCK_PLACE, pos);
                        placed++;
                    }
                }
                if (analyzer.placeIndex < analyzer.runs.size()) break;
                Boundary finished = analyzer.boundary;
                storedPortals += finished.count;
                int allPortals = 0;
                for (Work active : ACTIVE.values()) allPortals += active.storedPortals;
                if (storedPortals > 1_000_000 || allPortals > 4_000_000) {
                    owner.displayClientMessage(Component.translatable("message.torch_bag.bomb_too_complex"), false);
                    return false;
                }
                boundaries.put(next.toLong(), finished);
                analyzer = null; chunkIndex++; updateProgress();
                if (loadedMissing || placed >= PLACEMENTS_PER_SLICE || candidates >= CANDIDATES_PER_SLICE) break;
            }
            updateProgress();
            if (chunkIndex < chunks.size()) return true;
            completed = true;
            bar.setName(Component.translatable("message.torch_bag.bomb_progress", 100));
            bar.setProgress(1F);
            owner.displayClientMessage(Component.translatable("message.torch_bag.bomb_complete"), true);
            return false;
        }
        List<Portal> portals(int x, int z, int side, int offset) {
            Boundary adjacent = boundaries.get(ChunkPos.asLong(x, z));
            return adjacent == null ? List.of() : adjacent.sides[side][offset];
        }
        int percent() { return completed ? 100 : Math.min(99, (int)(100L * chunkIndex / chunks.size())); }
        void updateProgress() {
            int percent = percent();
            if (percent == lastPercent) return;
            lastPercent = percent;
            bar.setProgress(percent / 100F);
            bar.setName(Component.translatable("message.torch_bag.bomb_progress", percent));
        }
        void closeBar() { bar.removeAllPlayers(); }
    }

    /** Coarse conservative connectivity inside one currently loaded chunk. */
    private static final class Analyzer {
        final ChunkPos chunk;
        net.minecraft.world.level.chunk.LevelChunk loaded;
        final BlockPos release;
        final int[] xs, zs;
        final ArrayList<Run> runs = new ArrayList<>();
        final ArrayList<Integer>[] columns;
        final int minY, maxY, minX, maxX, minZ, maxZ;
        final int[] sectionModes;
        final int minSectionY;
        int nextColumn, nextEdge, seedIndex, emitIndex, placeIndex;
        int[] parent;
        byte[] rank;
        boolean[] reachable;
        boolean ready;
        final Boundary boundary = new Boundary();

        @SuppressWarnings("unchecked")
        Analyzer(ServerLevel level, net.minecraft.world.level.chunk.LevelChunk loaded, BlockPos release) {
            this.loaded = loaded; this.chunk = loaded.getPos(); this.release = release;
            boolean origin = new ChunkPos(release).equals(chunk);
            xs = sampleAxis(release.getX() & 15, origin); zs = sampleAxis(release.getZ() & 15, origin);
            var border = level.getWorldBorder();
            minX = Math.max(chunk.getMinBlockX(), (int)Math.ceil(border.getMinX()));
            maxX = Math.min(chunk.getMaxBlockX(), (int)Math.ceil(border.getMaxX()) - 1);
            minZ = Math.max(chunk.getMinBlockZ(), (int)Math.ceil(border.getMinZ()));
            maxZ = Math.min(chunk.getMaxBlockZ(), (int)Math.ceil(border.getMaxZ()) - 1);
            minY = level.getMinBuildHeight(); maxY = level.getMaxBuildHeight() - 1;
            columns = (ArrayList<Integer>[])new ArrayList<?>[xs.length * zs.length];
            for (int i = 0; i < columns.length; i++) columns[i] = new ArrayList<>();
            minSectionY = Math.floorDiv(minY, 16);
            int maxSectionY = Math.floorDiv(maxY, 16);
            sectionModes = new int[maxSectionY - minSectionY + 1];
            for (int sy = minSectionY; sy <= maxSectionY; sy++) {
                var section = loaded.getSection(level.getSectionIndex(sy * 16));
                sectionModes[sy - minSectionY] = section.hasOnlyAir() ? 1 :
                    (section.maybeHas(BombPlacer::passable) ? 2 : 0);
            }
        }
        boolean prepare(ServerLevel level, Work work, long deadline) {
            if (ready) return true;
            while (nextColumn < columns.length && System.nanoTime() < deadline) scanColumn(level, nextColumn++);
            if (nextColumn < columns.length) return false;
            if (parent == null) {
                parent = new int[runs.size()]; rank = new byte[runs.size()]; reachable = new boolean[runs.size()];
                for (int i = 0; i < parent.length; i++) parent[i] = i;
            }
            // One x-edge and one z-edge per sampled column; only tested clear
            // straight segments can join the coarse nodes across intervening cells.
            while (nextEdge < columns.length * 2 && System.nanoTime() < deadline) {
                int column = nextEdge / 2, axis = nextEdge++ & 1;
                if (axis == 0 && column % xs.length > 0) joinColumns(level, columns[column], columns[column - 1]);
                if (axis == 1 && column >= xs.length) joinColumns(level, columns[column], columns[column - xs.length]);
            }
            if (nextEdge < columns.length * 2) return false;
            while (seedIndex < runs.size() && System.nanoTime() < deadline) {
                Run run = runs.get(seedIndex++);
                int x = xs[run.column % xs.length], z = zs[run.column / xs.length];
                boolean seed = new ChunkPos(release).equals(chunk) && x == (release.getX() & 15) && z == (release.getZ() & 15) &&
                    release.getY() >= run.minY && release.getY() <= run.maxY;
                if (x == 0) seed |= overlaps(run, work.portals(chunk.x - 1, chunk.z, 1, z));
                if (x == 15) seed |= overlaps(run, work.portals(chunk.x + 1, chunk.z, 0, z));
                if (z == 0) seed |= overlaps(run, work.portals(chunk.x, chunk.z - 1, 3, x));
                if (z == 15) seed |= overlaps(run, work.portals(chunk.x, chunk.z + 1, 2, x));
                if (seed) reachable[find(run.id)] = true;
            }
            if (seedIndex < runs.size()) return false;
            while (emitIndex < runs.size() && System.nanoTime() < deadline) {
                Run run = runs.get(emitIndex++);
                if (!reachable[find(run.id)]) continue;
                int x = xs[run.column % xs.length], z = zs[run.column / xs.length];
                if (x == 0) boundary.add(0, z, run);
                if (x == 15) boundary.add(1, z, run);
                if (z == 0) boundary.add(2, x, run);
                if (z == 15) boundary.add(3, x, run);
            }
            if (emitIndex < runs.size()) return false;
            ready = true; return true;
        }
        boolean overlaps(Run run, List<Portal> portals) {
            for (Portal portal : portals) {
                if (portal.minY > run.maxY) break;
                if (portal.maxY >= run.minY) return true;
            }
            return false;
        }
        BlockPos position(Run run, int y) {
            return new BlockPos(chunk.getMinBlockX() + xs[run.column % xs.length], y,
                chunk.getMinBlockZ() + zs[run.column / xs.length]);
        }
        void scanColumn(ServerLevel level, int column) {
            int lx = xs[column % xs.length], lz = zs[column / xs.length];
            int worldX = chunk.getMinBlockX() + lx, worldZ = chunk.getMinBlockZ() + lz;
            if (worldX < minX || worldX > maxX || worldZ < minZ || worldZ > maxZ) return;
            int open = Integer.MIN_VALUE;
            for (int sy = minSectionY; sy < minSectionY + sectionModes.length; sy++) {
                int start = Math.max(minY, sy * 16), end = Math.min(maxY, sy * 16 + 15);
                int mode = sectionModes[sy - minSectionY];
                if (mode == 1) { if (open == Integer.MIN_VALUE) open = start; continue; }
                if (mode == 0) {
                    if (open != Integer.MIN_VALUE) { addRun(column, open, start - 1); open = Integer.MIN_VALUE; }
                    continue;
                }
                var section = loaded.getSection(level.getSectionIndex(start));
                for (int y = start; y <= end; y++) {
                    boolean air = passable(section.getBlockState(lx, y & 15, lz));
                    if (air && open == Integer.MIN_VALUE) open = y;
                    else if (!air && open != Integer.MIN_VALUE) { addRun(column, open, y - 1); open = Integer.MIN_VALUE; }
                }
            }
            if (open != Integer.MIN_VALUE) addRun(column, open, maxY);
        }
        void addRun(int column, int min, int max) {
            int id = runs.size(); runs.add(new Run(column, min, max, id)); columns[column].add(id);
        }
        void joinColumns(ServerLevel level, List<Integer> a, List<Integer> b) {
            int i = 0, j = 0;
            while (i < a.size() && j < b.size()) {
                Run left = runs.get(a.get(i)), right = runs.get(b.get(j));
                int low = Math.max(left.minY, right.minY), high = Math.min(left.maxY, right.maxY);
                if (low <= high && find(left.id) != find(right.id) &&
                    (clearLine(level, left, right, low) ||
                     (low < high && clearLine(level, left, right, low + 1)) ||
                     (high - low > 2 && clearLine(level, left, right, low + (high - low) / 2)) ||
                     (low < high && clearLine(level, left, right, high)))) union(left.id, right.id);
                if (left.maxY < right.maxY) i++; else j++;
            }
        }
        boolean clearLine(ServerLevel level, Run a, Run b, int y) {
            int x = xs[a.column % xs.length], z = zs[a.column / xs.length];
            int targetX = xs[b.column % xs.length], targetZ = zs[b.column / xs.length];
            int dx = Integer.compare(targetX, x), dz = Integer.compare(targetZ, z);
            while (x != targetX || z != targetZ) {
                x += dx; z += dz;
                if (!passable(loaded.getBlockState(new BlockPos(chunk.getMinBlockX() + x, y, chunk.getMinBlockZ() + z)))) return false;
            }
            return true;
        }
        int find(int x) { while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; }
        void union(int a, int b) {
            a = find(a); b = find(b); if (a == b) return;
            if (rank[a] < rank[b]) { int t = a; a = b; b = t; }
            parent[b] = a; if (rank[a] == rank[b]) rank[a]++;
        }
    }

    private static final class Run {
        final int column, minY, maxY, id;
        Run(int column, int minY, int maxY, int id) { this.column = column; this.minY = minY; this.maxY = maxY; this.id = id; }
    }
    private record Portal(int minY, int maxY) {}
    private static final class Boundary {
        final List<Portal>[][] sides;
        int count;
        @SuppressWarnings("unchecked") Boundary() {
            sides = (List<Portal>[][])new List<?>[4][16];
            for (int side = 0; side < 4; side++) for (int offset = 0; offset < 16; offset++) sides[side][offset] = List.of();
        }
        void add(int side, int offset, Run run) {
            if (sides[side][offset].isEmpty()) sides[side][offset] = new ArrayList<>();
            sides[side][offset].add(new Portal(run.minY, run.maxY)); count++;
        }
    }

    private record Recent(net.minecraft.resources.ResourceKey<Level> dimension, BlockPos pos, long bucket, long expires) {}
    private static boolean nearRecent(ServerLevel level, BlockPos pos) {
        Map<Long,List<Recent>> buckets = RECENT_BY_DIMENSION.get(level.dimension());
        if (buckets == null) return false;
        int cx=pos.getX()>>4, cz=pos.getZ()>>4;
        for(int x=cx-1;x<=cx+1;x++) for(int z=cz-1;z<=cz+1;z++)
            for(Recent recent:buckets.getOrDefault(ChunkPos.asLong(x,z),List.of()))
                if (recent.pos.distManhattan(pos) <= 13 && level.hasChunkAt(recent.pos) &&
                    level.getBlockState(recent.pos).is(net.minecraft.world.level.block.Blocks.TORCH) && clearManhattanPath(level, recent.pos, pos)) return true;
        return false;
    }
    private static final int[][] AXIS_ORDERS = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
    /** A short, unobstructed Manhattan route is a conservative prediction of new torch light. */
    private static boolean clearManhattanPath(ServerLevel level, BlockPos from, BlockPos to) {
        BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();
        for (int[] order : AXIS_ORDERS) {
            cursor.set(from);
            boolean clear = true;
            for (int axis : order) {
                int target = axis == 0 ? to.getX() : axis == 1 ? to.getY() : to.getZ();
                int current = axis == 0 ? cursor.getX() : axis == 1 ? cursor.getY() : cursor.getZ();
                int step = Integer.compare(target, current);
                while (current != target) {
                    cursor.move(axis == 0 ? step : 0, axis == 1 ? step : 0, axis == 2 ? step : 0);
                    current += step;
                    if (!level.hasChunkAt(cursor) || !level.getBlockState(cursor).getCollisionShape(level, cursor).isEmpty() ||
                        !level.getBlockState(cursor).getFluidState().isEmpty()) { clear = false; break; }
                }
                if (!clear) break;
            }
            if (clear) return true;
        }
        return false;
    }
    private static void remember(ServerLevel level, BlockPos pos) {
        long bucket=ChunkPos.asLong(pos); Recent recent=new Recent(level.dimension(),pos.immutable(),bucket,clock+40);
        RECENT.addLast(recent); RECENT_BY_DIMENSION.computeIfAbsent(level.dimension(), ignored->new HashMap<>())
            .computeIfAbsent(bucket,ignored->new ArrayList<>()).add(recent);
    }
    private static void pruneRecent() {
        while(!RECENT.isEmpty()&&RECENT.peekFirst().expires<=clock){
            Recent old=RECENT.removeFirst(); Map<Long,List<Recent>> byChunk=RECENT_BY_DIMENSION.get(old.dimension);
            if(byChunk!=null){List<Recent> list=byChunk.get(old.bucket);if(list!=null){list.remove(old);if(list.isEmpty())byChunk.remove(old.bucket);}if(byChunk.isEmpty())RECENT_BY_DIMENSION.remove(old.dimension);}
        }
    }
    private static void clearRecent(){RECENT.clear();RECENT_BY_DIMENSION.clear();}
}
