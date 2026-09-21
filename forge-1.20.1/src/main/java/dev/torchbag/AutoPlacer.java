package dev.torchbag;

import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.WallTorchBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.phys.shapes.Shapes;

/** Server-only, budgeted scanner. No chunk loads, client decisions, or parallel world access. */
public final class AutoPlacer {
    private static final Map<UUID, Work> WORK = new HashMap<>();
    private static final Map<Integer, List<BlockPos>> OFFSETS = new HashMap<>();
    // No simulated light flood-fill is needed. Minecraft's light engine is the
    // authority; scanning only dark, standable cells keeps the configurable ranges practical.
    private static final int SCAN_BUDGET = 65536;
    private static final int MAX_PLACEMENTS_PER_TICK = 16;
    public static void forget(ServerPlayer player) { WORK.remove(player.getUUID()); }
    public static void clear() { WORK.clear(); }
    public static void tick(ServerPlayer player) {
        ItemStack bag = BagAccess.active(player);
        if (!player.isAlive() || player.isSpectator() || !player.getAbilities().mayBuild || !(bag.getItem() instanceof TorchBagItem item)) {
            forget(player); return;
        }
        ServerLevel level = player.serverLevel();
        BlockPos center = player.blockPosition();
        Work work = WORK.get(player.getUUID());
        // Let an in-progress scan finish while walking; all placements recheck the current sphere.
        // Large moves and dimension changes discard old work immediately.
        int radius = BagData.radius(bag);
        int density = BagData.density(bag);
        if (work == null || work.bag != bag || work.level != level || work.radius != radius || work.density != density || work.center.distSqr(center) > 16) {
            work = new Work(level, center, bag, radius, density);
            WORK.put(player.getUUID(), work);
        }
        if (level.getGameTime() < work.nextTime) return;
        if (player.tickCount % 10 == 0 && TorchSupply.find(player, bag) == null) {
            work.nextTime = level.getGameTime() + 10; return;
        }
        work.step(player);
    }
    static List<BlockPos> offsets(int radius) {
        return OFFSETS.computeIfAbsent(radius, r -> {
            List<BlockPos> result = new ArrayList<>();
            for (int x = -r; x <= r; x++) for (int y = -r; y <= r; y++) for (int z = -r; z <= r; z++)
                if (x*x + y*y + z*z <= r*r) result.add(new BlockPos(x,y,z));
            result.sort(Comparator.comparingDouble(p -> p.distSqr(BlockPos.ZERO)));
            return List.copyOf(result);
        });
    }
    static boolean darkFloor(ServerLevel level, BlockPos pos) {
        return needsTorch(level, pos, BagData.DENSITY_LOW);
    }
    static boolean needsTorch(ServerLevel level, BlockPos pos, int density) {
        int lightThreshold = density == BagData.DENSITY_HIGH ? 5 : density == BagData.DENSITY_MEDIUM ? 4 : 0;
        return level.hasChunkAt(pos) && level.hasChunkAt(pos.below()) &&
            level.getBlockState(pos).isAir() && level.getBlockState(pos.above()).isAir() &&
            level.getBlockState(pos.below()).isFaceSturdy(level, pos.below(), Direction.UP) &&
            level.getBrightness(LightLayer.BLOCK, pos) <= lightThreshold;
    }
    static int densitySpacing(int density) {
        return density == BagData.DENSITY_HIGH ? 8 : density == BagData.DENSITY_MEDIUM ? 9 : 13;
    }
    static BlockState placementState(ServerLevel level, BlockPos pos) {
        if (!level.hasChunkAt(pos) || !level.getBlockState(pos).isAir() || !level.getWorldBorder().isWithinBounds(pos)) return null;
        BlockState floor = Blocks.TORCH.defaultBlockState();
        if (level.hasChunkAt(pos.below()) && floor.canSurvive(level, pos)) return floor;
        for (Direction dir : Direction.Plane.HORIZONTAL) {
            if (!level.hasChunkAt(pos.relative(dir.getOpposite()))) continue;
            BlockState wall = Blocks.WALL_TORCH.defaultBlockState().setValue(WallTorchBlock.FACING, dir);
            if (wall.canSurvive(level, pos)) return wall;
        }
        return null;
    }
    private static final class Work {
        final ServerLevel level;
        final BlockPos center;
        final ItemStack bag;
        final int radius, density;
        final List<BlockPos> offsets;
        final Map<BlockPos, Long> rejected = new HashMap<>();
        int cursor;
        long nextTime;
        Work(ServerLevel level, BlockPos center, ItemStack bag, int radius, int density) {
            this.level = level; this.center = center; this.bag = bag; this.radius = radius; this.density = density; offsets = offsets(radius);
        }
        void step(ServerPlayer player) {
            int budget = SCAN_BUDGET;
            int placed = 0;
            List<BlockPos> placedThisTick = new ArrayList<>();
            while (cursor < offsets.size() && budget-- > 0) {
                BlockPos pos = center.offset(offsets.get(cursor++));
                if (!level.isInWorldBounds(pos) || !level.hasChunkAt(pos) || rejected.getOrDefault(pos, 0L) > level.getGameTime()) continue;
                if (!needsTorch(level, pos, density)) continue;
                // The vanilla light engine applies the world update asynchronously.
                // Approximate only torches placed by this batch so nearby cells are
                // not filled before vanilla light becomes visible on the next tick.
                boolean batchLit = false;
                for (BlockPos torch : placedThisTick) {
                    int distance = Math.abs(torch.getX() - pos.getX()) + Math.abs(torch.getY() - pos.getY()) + Math.abs(torch.getZ() - pos.getZ());
                    if (distance <= densitySpacing(density)) { batchLit = true; break; }
                }
                if (batchLit) continue;
                BlockState state = placementState(level, pos);
                TorchSupply.Source source = TorchSupply.find(player, bag);
                if (state == null || source == null) break;
                ItemStack reserved = source.take();
                if (reserved.isEmpty()) break;
                if (!Platform.place(player, pos, state)) {
                    source.restore(reserved);
                    rejected.put(pos, level.getGameTime() + 100);
                    continue;
                }
                level.playSound(null, pos, SoundEvents.WOOD_PLACE, SoundSource.BLOCKS, 0.7F, 1F);
                level.gameEvent(player, GameEvent.BLOCK_PLACE, pos);
                player.getInventory().setChanged();
                placedThisTick.add(pos.immutable());
                if (++placed >= MAX_PLACEMENTS_PER_TICK) { reset(player, 1); return; }
            }
            reset(player, placed > 0 ? 1 : 10);
        }
        void reset(ServerPlayer player, int delay) {
            Work replacement = new Work(level, player.blockPosition(), bag, radius, density);
            rejected.entrySet().removeIf(e -> e.getValue() <= level.getGameTime());
            replacement.rejected.putAll(rejected);
            replacement.nextTime = level.getGameTime() + delay;
            WORK.put(player.getUUID(), replacement);
        }
    }
}
