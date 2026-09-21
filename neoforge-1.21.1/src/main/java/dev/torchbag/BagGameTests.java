package dev.torchbag;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.inventory.ClickType;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("torch_bag")
@PrefixGameTestTemplate(false)
public final class BagGameTests {
    private static ServerPlayer player(GameTestHelper h) {
        return new net.neoforged.neoforge.common.util.FakePlayer(h.getLevel(), new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(), "TorchBagTest"));
    }
    private static void sealedRoom(GameTestHelper h, BlockPos center) {
        for (int x = -2; x <= 2; x++) for (int y = -1; y <= 3; y++) for (int z = -2; z <= 2; z++) {
            boolean shell = x == -2 || x == 2 || z == -2 || z == 2 || y == -1 || y == 3;
            h.getLevel().setBlock(center.offset(x, y, z), shell ? Blocks.STONE.defaultBlockState() : Blocks.AIR.defaultBlockState(), 3);
        }
    }
    @GameTest(template = "empty")
    public static void storage(GameTestHelper h) {
        ItemStack bag = new ItemStack(TorchBagMod.item(BagTier.LEATHER));
        bag.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, Component.literal("Saved name"));
        BagInventory inv = new BagInventory(bag);
        h.assertTrue(inv.getContainerSize() == 54, "Expected one large-chest capacity");
        inv.setItem(0, new ItemStack(Items.DIAMOND));
        h.assertTrue(inv.isEmpty(), "Non-torch accepted");
        for (int i = 0; i < 54; i++) inv.setItem(i, new ItemStack(Items.TORCH, 64));
        h.assertTrue(new BagInventory(bag.copy()).count() == 3456, "Contents did not survive copy/serialization");
        inv.removeItem(0, 1);
        h.assertTrue(new BagInventory(bag).count() == 3455 && bag.getHoverName().getString().equals("Saved name"), "Storage or name did not persist");
        h.assertTrue(BagData.radius(bag) == 16, "Wrong default radius");
        BagData.setRadius(bag, 64);
        h.assertTrue(BagData.radius(bag.copy()) == 64, "Radius setting did not persist");
        h.succeed();
    }
    @GameTest(template = "empty")
    public static void capacityAndSourcePriority(GameTestHelper h) {
        ServerPlayer p = player(h);
        ItemStack bag = new ItemStack(TorchBagMod.item(BagTier.LEATHER));
        p.getInventory().setItem(1, bag);
        p.getInventory().setItem(0, new ItemStack(Items.TORCH, 64));
        BagMenu menu = new BagMenu(1, p.getInventory(), BagTier.LEATHER, 1, bag);
        p.containerMenu = menu;
        h.assertTrue(menu.clickMenuButton(p, 103) && BagData.radius(bag) == 64, "Radius menu setting was not saved");
        for (int i = 0; i < 53; i++) menu.inventory.setItem(i, new ItemStack(Items.TORCH, 64));
        menu.quickMoveStack(p, menu.visibleSlots + 27);
        h.assertTrue(menu.inventory.count() == 3456 && p.getInventory().getItem(0).isEmpty(), "Shift insert missed final slot");
        menu.clicked(menu.visibleSlots + 28, 0, ClickType.PICKUP, p);
        h.assertTrue(p.getInventory().getItem(1) == bag && menu.getCarried().isEmpty(), "Open bag can be moved");
        p.getInventory().setItem(0, new ItemStack(Items.TORCH, 11));
        TorchSupply.Source supply = TorchSupply.find(p, bag);
        ItemStack reserved = supply.take();
        h.assertTrue(menu.inventory.count() == 3455 && p.getInventory().getItem(0).getCount() == 11, "Bag did not supply first");
        supply.restore(reserved);
        h.assertTrue(menu.inventory.count() == 3456, "Failed-placement refund lost a torch");
        menu.inventory.clearContent();
        TorchSupply.find(p, bag).take();
        h.assertTrue(p.getInventory().getItem(0).getCount() == 10, "Player fallback failed");
        p.getInventory().setItem(1, ItemStack.EMPTY);
        h.assertTrue(!menu.stillValid(p), "Removed bag leaves menu valid");
        p.containerMenu = p.inventoryMenu;
        h.succeed();
    }
    @GameTest(template = "empty")
    public static void curiosSlotAndActivation(GameTestHelper h) {
        if (!ModList.get().isLoaded("curios")) { h.succeed(); return; }
        ServerPlayer p = player(h);
        var handler = top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(p).orElse(null);
        h.assertTrue(handler != null, "Curios player capability missing");
        var slot = handler.getCurios().get("belt");
        h.assertTrue(slot != null && slot.getSlots() == 1, "Expected exactly one automatic belt slot");
        h.assertTrue(!slot.getStacks().isItemValid(0, new ItemStack(Items.DIAMOND)), "Slot accepts unrelated items");
        ItemStack worn = new ItemStack(TorchBagMod.item(BagTier.LEATHER));
        slot.getStacks().setStackInSlot(0, worn);
        h.assertTrue(BagAccess.active(p) == worn, "Worn bag does not activate");
        ItemStack held = new ItemStack(TorchBagMod.item(BagTier.LEATHER));
        p.getInventory().setItem(p.getInventory().selected, held);
        h.assertTrue(BagAccess.active(p) == worn, "Worn bag must take priority");
        slot.getStacks().setStackInSlot(0, ItemStack.EMPTY);
        p.getInventory().setItem(p.getInventory().selected, ItemStack.EMPTY);
        h.assertTrue(BagAccess.active(p).isEmpty(), "Unequipping failed to stop activation");
        h.succeed();
    }
    @GameTest(template = "empty", timeoutTicks = 100)
    public static void daylightPlacementAndDensity(GameTestHelper h) {
        // Small isolated floor: one ordinary torch is enough, sunlight must not suppress it.
        ServerPlayer p = player(h);
        p.getAbilities().mayBuild = true;
        BlockPos center = h.absolutePos(new BlockPos(15, 10, 15));
        for (int x = -2; x <= 2; x++) for (int z = -2; z <= 2; z++) h.getLevel().setBlock(center.offset(x,-1,z), Blocks.STONE.defaultBlockState(), 3);
        p.setPos(center.getX() + 0.5, center.getY(), center.getZ() + 0.5);
        ItemStack bag = new ItemStack(TorchBagMod.item(BagTier.LEATHER));
        new BagInventory(bag).setItem(0, new ItemStack(Items.TORCH, 16));
        p.getInventory().setItem(p.getInventory().selected, bag);
        h.runAtTickTime(1, () -> { p.tickCount++; AutoPlacer.tick(p); });
        h.runAtTickTime(2, () -> {
            p.getInventory().setItem(p.getInventory().selected, ItemStack.EMPTY);
            AutoPlacer.forget(p);
        });
        h.runAtTickTime(3, () -> h.succeedWhen(() -> {
            int count = 0;
            for (int x = -2; x <= 2; x++) for (int z = -2; z <= 2; z++)
                if (h.getLevel().getBlockState(center.offset(x, 0, z)).is(Blocks.TORCH)) count++;
            int remaining = new BagInventory(bag).count();
            h.assertTrue(count == 1, "Expected one torch on 5x5 floor, got " + count);
            h.assertTrue(remaining <= 15, "The local torch was not consumed: " + remaining);
            for (int x = -2; x <= 2; x++) for (int z = -2; z <= 2; z++)
                h.assertTrue(h.getLevel().getBrightness(net.minecraft.world.level.LightLayer.BLOCK, center.offset(x,0,z)) > 0, "Unlit floor remains");
        }));
    }
    @GameTest(template = "empty", timeoutTicks = 100)
    public static void multipleDarkAreasAreLitWithoutVisibleDelay(GameTestHelper h) {
        ServerPlayer p = player(h);
        p.getAbilities().mayBuild = true;
        BlockPos center = h.absolutePos(new BlockPos(30, 10, 30));
        BlockPos left = center.offset(-7, 0, 0);
        BlockPos right = center.offset(7, 0, 0);
        for (BlockPos island : new BlockPos[]{left, right})
            h.getLevel().setBlock(island.below(), Blocks.STONE.defaultBlockState(), 3);
        p.setPos(center.getX() + 0.5, center.getY(), center.getZ() + 0.5);
        ItemStack bag = new ItemStack(TorchBagMod.item(BagTier.LEATHER));
        new BagInventory(bag).setItem(0, new ItemStack(Items.TORCH, 16));
        p.getInventory().setItem(p.getInventory().selected, bag);
        h.runAtTickTime(1, () -> { p.tickCount++; AutoPlacer.tick(p); });
        h.runAtTickTime(2, () -> { p.tickCount++; AutoPlacer.tick(p); });
        h.runAtTickTime(3, () -> {
            int count = 0;
            for (BlockPos island : new BlockPos[]{left, right})
                if (h.getLevel().getBlockState(island).is(Blocks.TORCH)) count++;
            h.assertTrue(count == 2, "Expected both distant dark areas to be lit without a visible delay, got " + count);
            h.assertTrue(new BagInventory(bag).count() <= 14, "The immediate placement pass did not consume both torches");
            AutoPlacer.forget(p);
            h.succeed();
        });
    }
    @GameTest(template = "empty")
    public static void backpackFallback(GameTestHelper h) {
        if (!ModList.get().isLoaded("sophisticatedbackpacks")) { h.succeed(); return; }
        ServerPlayer p = player(h);
        ItemStack bag = new ItemStack(TorchBagMod.item(BagTier.LEATHER));
        ItemStack backpack = new ItemStack(net.minecraft.core.registries.BuiltInRegistries.ITEM.get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("sophisticatedbackpacks", "backpack")));
        h.assertTrue(!backpack.isEmpty(), "Backpack registry item missing");
        var storage = net.p3pp3rf1y.sophisticatedbackpacks.backpack.wrapper.BackpackWrapper.fromStack(backpack).getInventoryHandler();
        storage.insertItem(0, new ItemStack(Items.TORCH, 23), false);
        p.getInventory().setItem(9, backpack);
        TorchSupply.Source source = TorchSupply.find(p, bag);
        h.assertTrue(source != null, "Backpack not discovered");
        ItemStack taken = source.take();
        h.assertTrue(taken.is(Items.TORCH) && taken.getCount() == 1 && storage.getStackInSlot(0).getCount() == 22, "Backpack extraction failed");
        source.restore(taken);
        h.assertTrue(storage.getStackInSlot(0).getCount() == 23, "Backpack refund failed");
        p.getInventory().setItem(9, ItemStack.EMPTY);
        h.assertTrue(TorchSupply.find(p, bag) == null, "Detached backpack still supplies torches");
        h.succeed();
    }
    @GameTest(template = "empty", timeoutTicks = 120)
    public static void bagWorksWhileWalking(GameTestHelper h) {
        ServerPlayer p = player(h);
        p.getAbilities().mayBuild = true;
        BlockPos origin=h.absolutePos(new BlockPos(10,10,15));
        for(int x=-3;x<=24;x++) for(int z=-3;z<=3;z++) h.getLevel().setBlock(origin.offset(x,-1,z),Blocks.STONE.defaultBlockState(),3);
        ItemStack bag=new ItemStack(TorchBagMod.item(BagTier.LEATHER));
        new BagInventory(bag).setItem(0,new ItemStack(Items.TORCH,32));
        p.getInventory().setItem(p.getInventory().selected,bag);
        for(int tick=1;tick<100;tick++) {
            final int t=tick;
            h.runAtTickTime(tick,()->{p.setPos(origin.getX()+0.5+t/5.0,origin.getY(),origin.getZ()+0.5);p.tickCount++;AutoPlacer.tick(p);});
        }
        h.runAtTickTime(100,()->{
            AutoPlacer.forget(p);
            h.assertTrue(new BagInventory(bag).count()<32,"Configurable-radius scan never finishes during normal walking");
            h.succeed();
        });
    }
    @GameTest(template = "empty", timeoutTicks = 120)
    public static void cancelledPlacementKeepsTorches(GameTestHelper h) {
        ServerPlayer p = player(h);
        p.getAbilities().mayBuild = true;
        BlockPos pos = h.absolutePos(new BlockPos(15,10,15));
        h.getLevel().setBlock(pos.below(),Blocks.STONE.defaultBlockState(),3);
        p.setPos(pos.getX()+0.5,pos.getY(),pos.getZ()+0.5);
        ItemStack bag = new ItemStack(TorchBagMod.item(BagTier.LEATHER));
        new BagInventory(bag).setItem(0,new ItemStack(Items.TORCH,8));
        p.getInventory().setItem(p.getInventory().selected,bag);
        int[] cancelled = {0};
        java.util.function.Consumer<net.neoforged.neoforge.event.level.BlockEvent.EntityPlaceEvent> deny = event -> {
            if (event.getEntity() == p) { event.setCanceled(true); cancelled[0]++; }
        };
        net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(deny);
        for (int tick=1;tick<90;tick++) h.runAtTickTime(tick,() -> {p.tickCount++;AutoPlacer.tick(p);});
        h.runAtTickTime(90,() -> {
            net.neoforged.neoforge.common.NeoForge.EVENT_BUS.unregister(deny);
            AutoPlacer.forget(p);
            h.assertTrue(cancelled[0] > 0,"No cancellable placement event fired");
            h.assertTrue(h.getLevel().getBlockState(pos).isAir(),"Cancelled block was not rolled back");
            h.assertTrue(new BagInventory(bag).count()==8,"Cancelled placement consumed torches");
            h.succeed();
        });
    }
    @GameTest(template = "empty")
    public static void sphereAndPlacementRules(GameTestHelper h) {
        var points = AutoPlacer.offsets(16);
        h.assertTrue(points.contains(new BlockPos(16,0,0)) && points.contains(new BlockPos(0,-16,0)), "Sphere misses boundary");
        h.assertTrue(!points.contains(new BlockPos(16,1,0)), "Sphere extends beyond radius");
        BlockPos pos = h.absolutePos(new BlockPos(3,3,3));
        h.assertTrue(AutoPlacer.placementState(h.getLevel(),pos) == null, "Torch floats without support");
        h.getLevel().setBlock(pos.below(), Blocks.STONE.defaultBlockState(),3);
        h.assertTrue(AutoPlacer.placementState(h.getLevel(),pos) != null, "Valid ground rejected");
        h.getLevel().setBlock(pos, Blocks.WATER.defaultBlockState(),3);
        h.assertTrue(AutoPlacer.placementState(h.getLevel(),pos) == null, "Water replaced");
        h.succeed();
    }
    @GameTest(template = "empty", timeoutTicks = 300)
    public static void torchBombSpiralAndLighting(GameTestHelper h) {
        ServerPlayer p = player(h);
        p.getAbilities().mayBuild = true;
        BlockPos marker = h.absolutePos(new BlockPos(15, 12, 15));
        h.assertTrue(BombPlacer.sampledColumnsForTest() <= 36, "Coarse bomb scan uses too many columns per chunk");
        var markerChunk = new net.minecraft.world.level.ChunkPos(marker);
        h.assertTrue(BombPlacer.sampledColumnsForTest(marker, new net.minecraft.world.level.ChunkPos(markerChunk.x + 1, markerChunk.z)) == 25,
            "A normal chunk should use exactly 25 representative columns");
        for (int radius : new int[]{4, 8, 16}) {
            var chunks = BombPlacer.chunkSpiral(marker, radius);
            var unique = new java.util.HashSet<>(chunks);
            var originChunk = new net.minecraft.world.level.ChunkPos(marker);
            h.assertTrue(!chunks.isEmpty() && chunks.get(0).equals(originChunk), "Bomb spiral does not start in the release chunk");
            h.assertTrue(unique.size() == chunks.size(), "Bomb spiral contains duplicate chunks at radius " + radius);
            int side = radius * 2 + 1;
            h.assertTrue(chunks.size() == side * side, "Wrong chunk count at radius " + radius + ": " + chunks.size());
            for (int dx : new int[]{-radius, radius}) for (int dz : new int[]{-radius, radius})
                h.assertTrue(unique.contains(new net.minecraft.world.level.ChunkPos(originChunk.x + dx, originChunk.z + dz)), "Bomb spiral misses an outer corner");
            int previousRing = 0;
            for (int i = 1; i < chunks.size(); i++) {
                var before = chunks.get(i - 1); var current = chunks.get(i);
                h.assertTrue(Math.abs(current.x - before.x) + Math.abs(current.z - before.z) == 1, "Bomb spiral jumps over a chunk at index " + i);
                int ring = Math.max(Math.abs(current.x - originChunk.x), Math.abs(current.z - originChunk.z));
                h.assertTrue(ring >= previousRing && ring <= radius, "Bomb spiral ring order is wrong at index " + i);
                previousRing = ring;
            }
        }
        var negative = BombPlacer.chunkSpiral(new BlockPos(-33, marker.getY(), -17), 2);
        h.assertTrue(negative.get(0).equals(new net.minecraft.world.level.ChunkPos(new BlockPos(-33, marker.getY(), -17))), "Negative chunk center is wrong");
        var origin = new net.minecraft.world.level.ChunkPos(marker);
        BlockPos connected = new BlockPos(origin.getMinBlockX() + 4, marker.getY(), origin.getMinBlockZ() + 4);
        BlockPos sealed = new BlockPos(origin.getMinBlockX() + 11, marker.getY(), origin.getMinBlockZ() + 11);
        sealedRoom(h, connected); sealedRoom(h, sealed);
        p.setPos(connected.getX() + 0.5, connected.getY(), connected.getZ() + 0.5);
        ItemStack bomb = new ItemStack(TorchBagMod.bomb(BombTier.I), 2);
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, bomb);
        h.runAtTickTime(1, () -> {
            TorchBagMod.bomb(BombTier.I).use(h.getLevel(), p, net.minecraft.world.InteractionHand.MAIN_HAND);
            h.assertTrue(bomb.getCount() == 1, "Using a bomb did not consume exactly one item");
            h.assertTrue(BombPlacer.pending() == 1, "Using a bomb did not queue its chunk-radius job");
            h.assertTrue(BombPlacer.progress(p.getUUID()) < 100, "Bomb progress completed before work began");
            TorchBagMod.bomb(BombTier.I).use(h.getLevel(), p, net.minecraft.world.InteractionHand.MAIN_HAND);
            h.assertTrue(bomb.getCount() == 1, "A second bomb was consumed before the first reached 100%");
            BombPlacer.clear();
            ServerPlayer second = player(h); second.getAbilities().mayBuild = true;
            second.setPos(connected.getX() + 0.5, connected.getY(), connected.getZ() + 0.5);
            h.assertTrue(BombPlacer.releaseForTest(p, 0) && BombPlacer.releaseForTest(second, 0), "Independent player bomb jobs were rejected");
        });
        h.runAtTickTime(2, () -> h.succeedWhen(() -> {
            h.assertTrue(BombPlacer.pending() == 0, "Bomb job did not finish");
            int connectedTorches = 0, sealedTorches = 0;
            for (int x = -1; x <= 1; x++) for (int z = -1; z <= 1; z++) {
                if (h.getLevel().getBlockState(connected.offset(x, 0, z)).is(Blocks.TORCH)) connectedTorches++;
                if (h.getLevel().getBlockState(sealed.offset(x, 0, z)).is(Blocks.TORCH)) sealedTorches++;
            }
            h.assertTrue(connectedTorches > 0 && connectedTorches < 4, "Overlapping player jobs produced unreasonable density: " + connectedTorches);
            h.assertTrue(sealedTorches == 0, "Bomb crossed into a sealed disconnected room");
            h.assertTrue(BombPlacer.progress(p.getUUID()) == 100, "Completed bomb did not report 100%");
        }));
    }
}
