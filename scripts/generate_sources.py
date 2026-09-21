"""Keep the equivalent Minecraft implementations together; generated Java is checked in."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def write(name, content, version=None):
    versions = [version] if version else ['forge-1.20.1', 'neoforge-1.21.1']
    for v in versions:
        code = content
        if v.startswith('neoforge'):
            code = code.replace('net.minecraftforge.items', 'net.neoforged.neoforge.items')
            code = code.replace('net.minecraftforge.fml.ModList', 'net.neoforged.fml.ModList')
            code = code.replace('snapshot.restore(true, false)', 'snapshot.restore()')
            code = code.replace('RegistryAccess registry', 'net.minecraft.core.HolderLookup.Provider registry')
        path = ROOT / v / 'src/main/java/dev/torchbag' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code.strip() + '\n', encoding='utf-8')

write('BagTier.java', '''
package dev.torchbag;

public enum BagTier {
    LEATHER("leather", 6, 16);
    public final String id;
    public final int rows, radius;
    BagTier(String id, int rows, int radius) { this.id = id; this.rows = rows; this.radius = radius; }
    public int slots() { return rows * 9; }
    public static BagTier of(int index) { return LEATHER; }
}
''')

write('BagInventory.java', '''
package dev.torchbag;

import net.minecraft.core.NonNullList;
import net.minecraft.world.Container;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/** A menu and the automatic placer must share this instance while that menu is open. */
public final class BagInventory implements Container {
    public final ItemStack bag;
    private final NonNullList<ItemStack> contents;
    public BagInventory(ItemStack bag) {
        this.bag = bag;
        contents = BagData.load(bag, ((TorchBagItem) bag.getItem()).tier.slots());
    }
    public static BagInventory access(Player player, ItemStack bag) {
        if (player.containerMenu instanceof BagMenu menu && menu.bag == bag) return menu.inventory;
        return new BagInventory(bag);
    }
    public int getContainerSize() { return contents.size(); }
    public boolean isEmpty() { return contents.stream().allMatch(ItemStack::isEmpty); }
    public ItemStack getItem(int slot) { return contents.get(slot); }
    public ItemStack removeItem(int slot, int amount) {
        ItemStack result = ContainerHelper.removeItem(contents, slot, amount);
        if (!result.isEmpty()) setChanged();
        return result;
    }
    public ItemStack removeItemNoUpdate(int slot) {
        ItemStack result = ContainerHelper.takeItem(contents, slot);
        setChanged();
        return result;
    }
    public void setItem(int slot, ItemStack stack) {
        if (!stack.isEmpty() && !stack.is(Items.TORCH)) return;
        contents.set(slot, stack);
        if (stack.getCount() > 64) stack.setCount(64);
        setChanged();
    }
    public void setChanged() { BagData.save(bag, contents); }
    public boolean stillValid(Player player) { return !bag.isEmpty(); }
    public boolean canPlaceItem(int slot, ItemStack stack) { return stack.is(Items.TORCH); }
    public void clearContent() { contents.clear(); setChanged(); }
    public int count() { return contents.stream().filter(s -> s.is(Items.TORCH)).mapToInt(ItemStack::getCount).sum(); }
}
''')

write('BagData.java', '''
package dev.torchbag;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.item.ItemStack;

public final class BagData {
    public static final int DEFAULT_RADIUS = 16;
    public static final int DENSITY_LOW = 0, DENSITY_MEDIUM = 1, DENSITY_HIGH = 2;
    public static NonNullList<ItemStack> load(ItemStack bag, int size) {
        NonNullList<ItemStack> items = NonNullList.withSize(size, ItemStack.EMPTY);
        if (bag.hasTag()) ContainerHelper.loadAllItems(bag.getTag().getCompound("TorchBag"), items);
        return items;
    }
    public static void save(ItemStack bag, NonNullList<ItemStack> items) {
        CompoundTag data = new CompoundTag();
        ContainerHelper.saveAllItems(data, items);
        bag.getOrCreateTag().put("TorchBag", data);
    }
    public static void copy(ItemStack source, ItemStack target) {
        if (source.hasTag()) target.setTag(source.getTag().copy());
    }
    public static int radius(ItemStack bag) {
        int value = bag.hasTag() ? bag.getTag().getInt("TorchBagRadius") : 0;
        return validRadius(value) ? value : DEFAULT_RADIUS;
    }
    public static void setRadius(ItemStack bag, int radius) {
        if (validRadius(radius)) bag.getOrCreateTag().putInt("TorchBagRadius", radius);
    }
    public static int density(ItemStack bag) {
        int value = bag.hasTag() ? bag.getTag().getInt("TorchBagDensity") : DENSITY_LOW;
        return validDensity(value) ? value : DENSITY_LOW;
    }
    public static void setDensity(ItemStack bag, int density) {
        if (validDensity(density)) bag.getOrCreateTag().putInt("TorchBagDensity", density);
    }
    private static boolean validRadius(int value) { return value == 8 || value == 16 || value == 32 || value == 64; }
    private static boolean validDensity(int value) { return value >= DENSITY_LOW && value <= DENSITY_HIGH; }
}
''', 'forge-1.20.1')

write('BagData.java', '''
package dev.torchbag;
import net.minecraft.core.NonNullList;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemContainerContents;

public final class BagData {
    public static final int DEFAULT_RADIUS = 16;
    public static final int DENSITY_LOW = 0, DENSITY_MEDIUM = 1, DENSITY_HIGH = 2;
    public static NonNullList<ItemStack> load(ItemStack bag, int size) {
        NonNullList<ItemStack> items = NonNullList.withSize(size, ItemStack.EMPTY);
        bag.getOrDefault(DataComponents.CONTAINER, ItemContainerContents.EMPTY).copyInto(items);
        return items;
    }
    public static void save(ItemStack bag, NonNullList<ItemStack> items) {
        bag.set(DataComponents.CONTAINER, ItemContainerContents.fromItems(items));
    }
    public static void copy(ItemStack source, ItemStack target) { target.applyComponents(source.getComponentsPatch()); }
    public static int radius(ItemStack bag) {
        int value = bag.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().getInt("TorchBagRadius");
        return validRadius(value) ? value : DEFAULT_RADIUS;
    }
    public static void setRadius(ItemStack bag, int radius) {
        if (!validRadius(radius)) return;
        CompoundTag tag = bag.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        tag.putInt("TorchBagRadius", radius);
        bag.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
    }
    public static int density(ItemStack bag) {
        int value = bag.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().getInt("TorchBagDensity");
        return validDensity(value) ? value : DENSITY_LOW;
    }
    public static void setDensity(ItemStack bag, int density) {
        if (!validDensity(density)) return;
        CompoundTag tag = bag.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        tag.putInt("TorchBagDensity", density);
        bag.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
    }
    private static boolean validRadius(int value) { return value == 8 || value == 16 || value == 32 || value == 64; }
    private static boolean validDensity(int value) { return value >= DENSITY_LOW && value <= DENSITY_HIGH; }
}
''', 'neoforge-1.21.1')

# These tests run inside Minecraft's real server, not against a simulated inventory.
for version in ['forge-1.20.1', 'neoforge-1.21.1']:
    old = version.startswith('forge')
    write('BagGameTests.java', '''
package dev.torchbag;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.inventory.ClickType;
import net.minecraftforge.fml.ModList;
import GAMETEST_PACKAGE.GameTestHolder;
import GAMETEST_PACKAGE.PrefixGameTestTemplate;

@GameTestHolder("torch_bag")
@PrefixGameTestTemplate(false)
public final class BagGameTests {
    private static ServerPlayer player(GameTestHelper h) {
        return new FAKE_PLAYER(h.getLevel(), new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(), "TorchBagTest"));
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
        SET_NAME
        BagInventory inv = new BagInventory(bag);
        h.assertTrue(inv.getContainerSize() == 54, "Expected one large-chest capacity");
        inv.setItem(0, new ItemStack(Items.DIAMOND));
        h.assertTrue(inv.isEmpty(), "Non-torch accepted");
        for (int i = 0; i < 54; i++) inv.setItem(i, new ItemStack(Items.TORCH, 64));
        h.assertTrue(new BagInventory(bag.copy()).count() == 3456, "Contents did not survive copy/serialization");
        inv.removeItem(0, 1);
        h.assertTrue(new BagInventory(bag).count() == 3455 && bag.getHoverName().getString().equals("Saved name"), "Storage or name did not persist");
        h.assertTrue(BagData.radius(bag) == 16, "Wrong default radius");
        h.assertTrue(BagData.density(bag) == BagData.DENSITY_LOW, "Wrong default light density");
        BagData.setRadius(bag, 64);
        BagData.setDensity(bag, BagData.DENSITY_HIGH);
        h.assertTrue(BagData.radius(bag.copy()) == 64 && BagData.density(bag.copy()) == BagData.DENSITY_HIGH, "Bag settings did not persist");
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
        h.assertTrue(menu.clickMenuButton(p, 201) && BagData.density(bag) == BagData.DENSITY_MEDIUM, "Density menu setting was not saved");
        h.assertTrue(AutoPlacer.densitySpacing(BagData.DENSITY_LOW) == 13 && AutoPlacer.densitySpacing(BagData.DENSITY_MEDIUM) == 9 &&
            AutoPlacer.densitySpacing(BagData.DENSITY_HIGH) == 8, "Density spacing ratios are wrong");
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
        ItemStack backpack = new ItemStack(net.minecraft.core.registries.BuiltInRegistries.ITEM.get(BACKPACK_ID));
        h.assertTrue(!backpack.isEmpty(), "Backpack registry item missing");
        var storage = BACKPACK_INVENTORY;
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
        java.util.function.Consumer<PLACE_EVENT_TYPE> deny = event -> {
            if (event.getEntity() == p) { event.setCanceled(true); cancelled[0]++; }
        };
        TEST_EVENT_BUS.addListener(deny);
        for (int tick=1;tick<90;tick++) h.runAtTickTime(tick,() -> {p.tickCount++;AutoPlacer.tick(p);});
        h.runAtTickTime(90,() -> {
            TEST_EVENT_BUS.unregister(deny);
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
'''.replace('GAMETEST_PACKAGE', 'net.minecraftforge.gametest' if old else 'net.neoforged.neoforge.gametest')
       .replace('FAKE_PLAYER', 'net.minecraftforge.common.util.FakePlayer' if old else 'net.neoforged.neoforge.common.util.FakePlayer')
       .replace('PLACE_EVENT_TYPE', 'net.minecraftforge.event.level.BlockEvent.EntityPlaceEvent' if old else 'net.neoforged.neoforge.event.level.BlockEvent.EntityPlaceEvent')
       .replace('TEST_EVENT_BUS', 'net.minecraftforge.common.MinecraftForge.EVENT_BUS' if old else 'net.neoforged.neoforge.common.NeoForge.EVENT_BUS')
       .replace('BACKPACK_ID', 'new net.minecraft.resources.ResourceLocation("sophisticatedbackpacks", "backpack")' if old else 'net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("sophisticatedbackpacks", "backpack")')
       .replace('BACKPACK_INVENTORY', 'backpack.getCapability(net.p3pp3rf1y.sophisticatedbackpacks.api.CapabilityBackpackWrapper.getCapabilityInstance()).orElseThrow(() -> new IllegalStateException("Missing backpack capability")).getInventoryHandler()' if old else 'net.p3pp3rf1y.sophisticatedbackpacks.backpack.wrapper.BackpackWrapper.fromStack(backpack).getInventoryHandler()')
       .replace('SET_NAME', 'bag.setHoverName(Component.literal("Saved name"));' if old else 'bag.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, Component.literal("Saved name"));'), version)

write('CuriosCompat.java', '''
package dev.torchbag;
import java.util.List;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

/** Only loaded after ModList confirms that Curios is present. */
public final class CuriosCompat {
    public static void register() {
        for (BagTier tier : BagTier.values()) CuriosApi.registerCurio(TorchBagMod.item(tier), new ICurioItem() {});
    }
    public static ItemStack equipped(Player player) {
        return CuriosApi.getCuriosInventory(player).map(handler -> {
            var slots = handler.findCurios("belt");
            for (var slot : slots) if (slot.stack().getItem() instanceof TorchBagItem) return slot.stack();
            return ItemStack.EMPTY;
        }).orElse(ItemStack.EMPTY);
    }
}
''')

write('BagAccess.java', '''
package dev.torchbag;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.fml.ModList;

public final class BagAccess {
    public static ItemStack equipped(Player player) {
        return ModList.get().isLoaded("curios") ? CuriosCompat.equipped(player) : ItemStack.EMPTY;
    }
    public static ItemStack at(Player player, int source) {
        if (source == -1) return equipped(player);
        return source >= 0 && source < player.getInventory().getContainerSize() ? player.getInventory().getItem(source) : ItemStack.EMPTY;
    }
    public static ItemStack active(Player player) {
        ItemStack worn = equipped(player);
        if (worn.getItem() instanceof TorchBagItem) return worn;
        if (player.getMainHandItem().getItem() instanceof TorchBagItem) return player.getMainHandItem();
        return player.getOffhandItem().getItem() instanceof TorchBagItem ? player.getOffhandItem() : ItemStack.EMPTY;
    }
}
''')

write('TorchSupply.java', '''
package dev.torchbag;
import net.minecraft.world.Container;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.items.IItemHandler;

public final class TorchSupply {
    /** Reserve exactly one torch before placement; return it to its source if placement fails. */
    public interface Source {
        ItemStack take();
        void restore(ItemStack torch);
    }
    public static Source find(Player player, ItemStack bag) {
        Source source = fromContainer(BagInventory.access(player, bag), player);
        if (source == null) source = fromContainer(player.getInventory(), player);
        if (source == null && ModList.get().isLoaded("sophisticatedbackpacks")) source = BackpackCompat.find(player);
        return source;
    }
    public static Source fromContainer(Container inventory, Player player) {
        for (int i = 0; i < inventory.getContainerSize(); i++) {
            if (!inventory.getItem(i).is(Items.TORCH)) continue;
            final int slot = i;
            return new Source() {
                public ItemStack take() { return inventory.getItem(slot).is(Items.TORCH) ? inventory.removeItem(slot, 1) : ItemStack.EMPTY; }
                public void restore(ItemStack torch) {
                    ItemStack current = inventory.getItem(slot);
                    if (current.isEmpty()) inventory.setItem(slot, torch);
                    else if (current.is(Items.TORCH) && current.getCount() < 64) { current.grow(torch.getCount()); inventory.setChanged(); }
                    else if (!player.getInventory().add(torch)) player.drop(torch, false);
                }
            };
        }
        return null;
    }
    public static Source fromHandler(IItemHandler inventory, Player player) {
        for (int i = 0; i < inventory.getSlots(); i++) {
            if (!inventory.getStackInSlot(i).is(Items.TORCH) || !inventory.extractItem(i, 1, true).is(Items.TORCH)) continue;
            final int slot = i;
            return new Source() {
                public ItemStack take() { return inventory.extractItem(slot, 1, false); }
                public void restore(ItemStack torch) {
                    ItemStack rest = inventory.insertItem(slot, torch, false);
                    if (!rest.isEmpty() && !player.getInventory().add(rest)) player.drop(rest, false);
                }
            };
        }
        return null;
    }
}
''')

for version in ['forge-1.20.1', 'neoforge-1.21.1']:
    wrapper = ('stack.getCapability(net.p3pp3rf1y.sophisticatedbackpacks.api.CapabilityBackpackWrapper.getCapabilityInstance()).map(w -> TorchSupply.fromHandler(w.getInventoryHandler(), player)).orElse(null)'
               if version.startswith('forge') else 'TorchSupply.fromHandler(net.p3pp3rf1y.sophisticatedbackpacks.backpack.wrapper.BackpackWrapper.fromStack(stack).getInventoryHandler(), player)')
    write('BackpackCompat.java', '''
package dev.torchbag;
import net.minecraft.world.entity.player.Player;
import net.p3pp3rf1y.sophisticatedbackpacks.util.PlayerInventoryProvider;

public final class BackpackCompat {
    public static TorchSupply.Source find(Player player) {
        TorchSupply.Source[] result = {null};
        PlayerInventoryProvider.get().runOnBackpacks(player, (stack, handler, identifier, slot) -> {
            result[0] = WRAPPER;
            return result[0] != null;
        });
        return result[0];
    }
}
'''.replace('WRAPPER', wrapper), version)

write('BagMenu.java', '''
package dev.torchbag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

public final class BagMenu extends AbstractContainerMenu {
    public final BagTier tier;
    public final ItemStack bag;
    public final BagInventory inventory;
    public final int source, rows, visibleSlots;
    private final Container contents;
    public int page, torchCount, radius = BagData.DEFAULT_RADIUS, density = BagData.DENSITY_LOW;
    public BagMenu(int id, Inventory player, FriendlyByteBuf data) {
        this(id, player, BagTier.of(data.readVarInt()), data.readInt(), null);
    }
    public BagMenu(int id, Inventory player, BagTier tier, int source, ItemStack bag) {
        super(TorchBagMod.menuType(), id);
        this.tier = tier;
        this.source = source;
        this.bag = bag == null ? ItemStack.EMPTY : bag;
        this.inventory = bag == null ? null : new BagInventory(bag);
        this.contents = inventory == null ? new SimpleContainer(tier.slots()) : inventory;
        rows = Math.min(6, tier.rows);
        visibleSlots = rows * 9;
        Container view = new Window();
        for (int row = 0; row < rows; row++) for (int col = 0; col < 9; col++) {
            addSlot(new Slot(view, row * 9 + col, 8 + col * 18, 18 + row * 18) {
                public boolean mayPlace(ItemStack stack) { return stack.is(Items.TORCH); }
            });
        }
        int y = 31 + rows * 18;
        for (int row = 0; row < 3; row++) for (int col = 0; col < 9; col++)
            addPlayerSlot(player, col + row * 9 + 9, 8 + col * 18, y + row * 18);
        for (int col = 0; col < 9; col++) addPlayerSlot(player, col, 8 + col * 18, y + 58);
        addDataSlot(new DataSlot() {
            public int get() { return page; }
            public void set(int value) { page = Math.max(0, Math.min(tier.rows - rows, value)); }
        });
        addDataSlot(new DataSlot() {
            public int get() { return inventory == null ? torchCount : inventory.count(); }
            public void set(int value) { torchCount = value; }
        });
        addDataSlot(new DataSlot() {
            public int get() { return inventory == null ? radius : BagData.radius(bag); }
            public void set(int value) { radius = value; }
        });
        addDataSlot(new DataSlot() {
            public int get() { return inventory == null ? density : BagData.density(bag); }
            public void set(int value) { density = value; }
        });
    }
    private void addPlayerSlot(Inventory player, int index, int x, int y) {
        final int inventoryIndex = index;
        addSlot(new Slot(player, index, x, y) {
            public boolean mayPickup(Player p) { return inventoryIndex != source; }
            public boolean mayPlace(ItemStack stack) { return inventoryIndex != source; }
        });
    }
    public boolean stillValid(Player player) {
        return inventory == null || (player.isAlive() && BagAccess.at(player, source) == bag);
    }
    public boolean clickMenuButton(Player player, int button) {
        if (!stillValid(player) || !getCarried().isEmpty()) return false;
        if (button >= 100 && button <= 103 && inventory != null) {
            int[] radii = {8, 16, 32, 64};
            radius = radii[button - 100];
            BagData.setRadius(bag, radius);
        } else if (button >= 200 && button <= 202 && inventory != null) {
            density = button - 200;
            BagData.setDensity(bag, density);
        } else if (button >= 0 && button <= tier.rows - rows) page = button;
        else return false;
        broadcastChanges();
        return true;
    }
    public void clicked(int slot, int button, ClickType type, Player player) {
        if (!stillValid(player) || type == ClickType.SWAP) return;
        super.clicked(slot, button, type, player);
    }
    public ItemStack quickMoveStack(Player player, int index) {
        if (!stillValid(player) || index < 0 || index >= slots.size()) return ItemStack.EMPTY;
        Slot slot = slots.get(index);
        if (!slot.hasItem() || !slot.mayPickup(player)) return ItemStack.EMPTY;
        ItemStack stack = slot.getItem(), original = stack.copy();
        if (index < visibleSlots) {
            if (!moveItemStackTo(stack, visibleSlots, slots.size(), true)) return ItemStack.EMPTY;
        } else {
            if (!stack.is(Items.TORCH)) return ItemStack.EMPTY;
            // Include hidden rows when shift-clicking into the bag.
            for (int pass = 0; pass < 2 && !stack.isEmpty(); pass++) {
                for (int i = 0; i < contents.getContainerSize() && !stack.isEmpty(); i++) {
                    ItemStack target = contents.getItem(i);
                    if (pass == 0 && target.is(Items.TORCH) && target.getCount() < 64) {
                        int move = Math.min(64 - target.getCount(), stack.getCount());
                        target.grow(move); stack.shrink(move); contents.setChanged();
                    } else if (pass == 1 && target.isEmpty()) contents.setItem(i, stack.split(Math.min(64, stack.getCount())));
                }
            }
            if (stack.getCount() == original.getCount()) return ItemStack.EMPTY;
        }
        if (stack.isEmpty()) slot.set(ItemStack.EMPTY); else slot.setChanged();
        slot.onTake(player, stack);
        return original;
    }
    private final class Window implements Container {
        // Client slots contain only the current page. Slot packets precede page-data packets.
        private int map(int slot) { return inventory == null ? slot : page * 9 + slot; }
        public int getContainerSize() { return visibleSlots; }
        public boolean isEmpty() { return contents.isEmpty(); }
        public ItemStack getItem(int slot) { return contents.getItem(map(slot)); }
        public ItemStack removeItem(int slot, int count) { return contents.removeItem(map(slot), count); }
        public ItemStack removeItemNoUpdate(int slot) { return contents.removeItemNoUpdate(map(slot)); }
        public void setItem(int slot, ItemStack stack) { contents.setItem(map(slot), stack); }
        public void setChanged() { contents.setChanged(); }
        public boolean stillValid(Player player) { return BagMenu.this.stillValid(player); }
        public void clearContent() { contents.clearContent(); }
    }
}
''')

for version in ['forge-1.20.1', 'neoforge-1.21.1']:
    tooltip = ('public void appendHoverText(ItemStack stack, Level level, List<Component> text, TooltipFlag flag)'
               if version.startswith('forge') else 'public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> text, TooltipFlag flag)')
    write('TorchBagItem.java', '''
package dev.torchbag;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

public final class TorchBagItem extends Item {
    public final BagTier tier;
    public TorchBagItem(BagTier tier) { super(new Item.Properties().stacksTo(1)); this.tier = tier; }
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player instanceof ServerPlayer server) Platform.open(server, hand == InteractionHand.MAIN_HAND ? player.getInventory().selected : 40);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }
    public InteractionResult useOn(UseOnContext context) {
        Player player = context.getPlayer();
        if (player == null) return InteractionResult.PASS;
        return use(context.getLevel(), player, context.getHand()).getResult();
    }
    TOOLTIP {
        text.add(Component.translatable("tooltip.torch_bag.capacity", tier.slots(), BagData.radius(stack)).withStyle(ChatFormatting.GRAY));
        text.add(Component.translatable("tooltip.torch_bag.density", Component.translatable("screen.torch_bag.density_" + BagData.density(stack))).withStyle(ChatFormatting.GRAY));
        text.add(Component.translatable("tooltip.torch_bag.usage").withStyle(ChatFormatting.GOLD));
        text.add(Component.translatable("tooltip.torch_bag.curios").withStyle(ChatFormatting.GRAY));
    }
}
'''.replace('TOOLTIP', tooltip), version)

for version in ['forge-1.20.1', 'neoforge-1.21.1']:
    tooltip = ('public void appendHoverText(ItemStack stack, Level level, List<Component> text, TooltipFlag flag)'
               if version.startswith('forge') else 'public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> text, TooltipFlag flag)')
    write('TorchBombItem.java', '''
package dev.torchbag;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;

public final class TorchBombItem extends Item {
    public final BombTier tier;
    public TorchBombItem(BombTier tier) { super(new Item.Properties().stacksTo(16)); this.tier = tier; }
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide && player instanceof ServerPlayer server) {
            if (!BombPlacer.release(server, tier)) return InteractionResultHolder.fail(stack);
            if (!player.getAbilities().instabuild) stack.shrink(1);
            player.getCooldowns().addCooldown(this, 20);
            player.awardStat(Stats.ITEM_USED.get(this));
            level.playSound(null, player.blockPosition(), SoundEvents.ENDER_EYE_DEATH, SoundSource.PLAYERS, 1.0F, 0.8F + tier.ordinal() * 0.15F);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }
    TOOLTIP {
        text.add(Component.translatable("tooltip.torch_bag.bomb_radius", tier.chunkRadius).withStyle(ChatFormatting.GOLD));
        text.add(Component.translatable("tooltip.torch_bag.bomb_usage").withStyle(ChatFormatting.GRAY));
    }
}
'''.replace('TOOLTIP', tooltip), version)

write('BombPlacer.java', (ROOT / 'scripts/templates/BombPlacer.java').read_text(encoding='utf-8'))

write('BagScreen.java', '''
package dev.torchbag;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public final class BagScreen extends AbstractContainerScreen<BagMenu> {
    private static final ResourceLocation BACKGROUND = RESOURCE_LOCATION;
    private static final ResourceLocation GEAR = GEAR_LOCATION;
    private static final int[] RADII = {8, 16, 32, 64};
    private boolean settingsOpen;
    public BagScreen(BagMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
        imageWidth = 176;
        imageHeight = 114 + menu.rows * 18;
        inventoryLabelY = imageHeight - 94;
    }
    protected void renderBg(GuiGraphics g, float partial, int mouseX, int mouseY) {
        int x = leftPos, y = topPos;
        int upper = menu.rows * 18 + 17;
        g.blit(BACKGROUND, x, y, 0, 0, imageWidth, upper, 256, 256);
        g.blit(BACKGROUND, x, y + upper, 0, 126, imageWidth, 96, 256, 256);
        int gearState = inside(mouseX, mouseY, x + 177, y + 5, 20, 20) ? 20 : 0;
        g.blit(GEAR, x + 177, y + 5, 0, gearState, 20, 20, 20, 40);
        if (settingsOpen) renderSettings(g, mouseX, mouseY);
    }
    protected void renderLabels(GuiGraphics g, int mx, int my) {
        super.renderLabels(g, mx, my);
    }
    private void renderSettings(GuiGraphics g, int mx, int my) {
        int x = leftPos + 176, y = topPos + 28, w = 82, h = 184;
        bevel(g, x, y, x + w, y + h, false);
        g.drawString(font, Component.translatable("screen.torch_bag.settings"), x + 8, y + 8, 0x404040, false);
        g.drawString(font, Component.translatable("screen.torch_bag.radius"), x + 8, y + 22, 0x404040, false);
        for (int i = 0; i < RADII.length; i++) {
            int by = y + 35 + i * 18;
            boolean selected = menu.radius == RADII[i];
            boolean hover = inside(mx, my, x + 8, by, 66, 16);
            bevel(g, x + 8, by, x + 74, by + 16, selected);
            int color = selected ? 0xFFFFA000 : (hover ? 0xFFFFFFA0 : 0xFFFFFFFF);
            String label = Component.translatable("screen.torch_bag.radius_value", RADII[i]).getString();
            g.drawString(font, label, x + 41 - font.width(label) / 2, by + 4, color, true);
        }
        g.drawString(font, Component.translatable("screen.torch_bag.density"), x + 8, y + 109, 0x404040, false);
        for (int i = 0; i < 3; i++) {
            int by = y + 122 + i * 18;
            boolean selected = menu.density == i;
            boolean hover = inside(mx, my, x + 8, by, 66, 16);
            bevel(g, x + 8, by, x + 74, by + 16, selected);
            int color = selected ? 0xFFFFA000 : (hover ? 0xFFFFFFA0 : 0xFFFFFFFF);
            String label = Component.translatable("screen.torch_bag.density_" + i).getString();
            g.drawString(font, label, x + 41 - font.width(label) / 2, by + 4, color, true);
        }
    }
    private static void bevel(GuiGraphics g, int x1, int y1, int x2, int y2, boolean pressed) {
        int light = pressed ? 0xFF373737 : 0xFFFFFFFF;
        int dark = pressed ? 0xFFFFFFFF : 0xFF373737;
        g.fill(x1, y1, x2, y2, 0xFFC6C6C6);
        g.fill(x1, y1, x2, y1 + 1, light); g.fill(x1, y1, x1 + 1, y2, light);
        g.fill(x1, y2 - 1, x2, y2, dark); g.fill(x2 - 1, y1, x2, y2, dark);
    }
    private static boolean inside(double mx, double my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }
    public void render(GuiGraphics g, int mx, int my, float partial) {
        RENDER_BACKGROUND
        super.render(g, mx, my, partial);
        renderTooltip(g, mx, my);
    }
    public boolean mouseClicked(double mx, double my, int button) {
        if (button == 0 && inside(mx, my, leftPos + 177, topPos + 5, 20, 20)) {
            settingsOpen = !settingsOpen;
            return true;
        }
        if (button == 0 && settingsOpen) for (int i = 0; i < RADII.length; i++) {
            if (inside(mx, my, leftPos + 184, topPos + 63 + i * 18, 66, 16)) {
                if (minecraft != null && minecraft.gameMode != null)
                    minecraft.gameMode.handleInventoryButtonClick(menu.containerId, 100 + i);
                return true;
            }
        }
        if (button == 0 && settingsOpen) for (int i = 0; i < 3; i++) {
            if (inside(mx, my, leftPos + 184, topPos + 150 + i * 18, 66, 16)) {
                if (minecraft != null && minecraft.gameMode != null)
                    minecraft.gameMode.handleInventoryButtonClick(menu.containerId, 200 + i);
                return true;
            }
        }
        return super.mouseClicked(mx, my, button);
    }
}
''')

write('BombTier.java', '''
package dev.torchbag;

public enum BombTier {
    I("torch_bomb_i", 4), II("torch_bomb_ii", 8), III("torch_bomb_iii", 16);
    public final String id;
    public final int chunkRadius;
    BombTier(String id, int chunkRadius) { this.id = id; this.chunkRadius = chunkRadius; }
}
''')

for version in ['forge-1.20.1', 'neoforge-1.21.1']:
    p = ROOT / version / 'src/main/java/dev/torchbag/BagScreen.java'
    code = p.read_text()
    code = code.replace('RENDER_BACKGROUND', 'renderBackground(g);' if version.startswith('forge') else '// The 1.21 container screen draws its own background.')
    code = code.replace('RESOURCE_LOCATION', 'new ResourceLocation("minecraft", "textures/gui/container/generic_54.png")' if version.startswith('forge') else 'ResourceLocation.withDefaultNamespace("textures/gui/container/generic_54.png")')
    code = code.replace('GEAR_LOCATION', 'new ResourceLocation(TorchBagMod.ID, "textures/gui/gear_button.png")' if version.startswith('forge') else 'ResourceLocation.fromNamespaceAndPath(TorchBagMod.ID, "textures/gui/gear_button.png")')
    p.write_text(code, encoding='utf-8')

write('AutoPlacer.java', '''
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
''')

for version in ['forge-1.20.1', 'neoforge-1.21.1']:
    old = version.startswith('forge')
    write('TorchBagMod.java', '''
package dev.torchbag;
import java.util.EnumMap;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.*;
IMPORTS

@Mod(TorchBagMod.ID)
public final class TorchBagMod {
    public static final String ID = "torch_bag";
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(Registries.ITEM, ID);
    private static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, ID);
    private static final EnumMap<BagTier, Supplier<TorchBagItem>> BAGS = new EnumMap<>(BagTier.class);
    private static final EnumMap<BombTier, Supplier<TorchBombItem>> BOMBS = new EnumMap<>(BombTier.class);
    private static final Supplier<MenuType<BagMenu>> MENU = MENUS.register("bag", () -> IMenuTypeExtension.create(BagMenu::new));
    static {
        for (BagTier tier : BagTier.values()) BAGS.put(tier, ITEMS.register(tier.id + "_torch_bag", () -> new TorchBagItem(tier)));
        for (BombTier tier : BombTier.values()) BOMBS.put(tier, ITEMS.register(tier.id, () -> new TorchBombItem(tier)));
    }
    public static TorchBagItem item(BagTier tier) { return BAGS.get(tier).get(); }
    public static TorchBombItem bomb(BombTier tier) { return BOMBS.get(tier).get(); }
    public static MenuType<BagMenu> menuType() { return MENU.get(); }
    CONSTRUCTOR {
        BUS_INIT
        ITEMS.register(bus); MENUS.register(bus);
        bus.addListener(this::setup);
        bus.addListener(this::creative);
        SERVER_EVENTS
        NETWORK_INIT
        if (FMLEnvironment.dist == Dist.CLIENT) ClientBootstrap.init(bus);
    }
    private void setup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> { if (ModList.get().isLoaded("curios")) CuriosCompat.register(); });
    }
    private void creative(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) {
            for (BagTier tier : BagTier.values()) event.accept(item(tier));
            for (BombTier tier : BombTier.values()) event.accept(bomb(tier));
        }
    }
}
'''.replace('IMPORTS', '''
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;
import net.minecraftforge.registries.DeferredRegister;
''' if old else '''
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.registries.DeferredRegister;
''').replace('IMenuTypeExtension.create', 'IForgeMenuType.create' if old else 'IMenuTypeExtension.create')
       .replace('CONSTRUCTOR', 'public TorchBagMod()' if old else 'public TorchBagMod(IEventBus bus)')
       .replace('BUS_INIT', 'var bus = FMLJavaModLoadingContext.get().getModEventBus();' if old else '')
       .replace('SERVER_EVENTS', '''
        MinecraftForge.EVENT_BUS.addListener((TickEvent.PlayerTickEvent event) -> {
            if (event.phase == TickEvent.Phase.END && event.player instanceof net.minecraft.server.level.ServerPlayer player) AutoPlacer.tick(player);
        });
        MinecraftForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent event) -> {
            if (event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player) { AutoPlacer.forget(player); BombPlacer.cancel(player.getUUID()); }
        });
        MinecraftForge.EVENT_BUS.addListener((TickEvent.ServerTickEvent event) -> { if (event.phase == TickEvent.Phase.END && event.haveTime()) BombPlacer.tick(event.getServer()); });
        MinecraftForge.EVENT_BUS.addListener((ServerStoppedEvent event) -> { AutoPlacer.clear(); BombPlacer.clear(); });
''' if old else '''
        NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post event) -> {
            if (event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player) AutoPlacer.tick(player);
        });
        NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent event) -> {
            if (event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player) { AutoPlacer.forget(player); BombPlacer.cancel(player.getUUID()); }
        });
        NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post event) -> { if (event.hasTime()) BombPlacer.tick(event.getServer()); });
        NeoForge.EVENT_BUS.addListener((ServerStoppedEvent event) -> { AutoPlacer.clear(); BombPlacer.clear(); });
''').replace('NETWORK_INIT', 'BagNetwork.init();' if old else 'bus.addListener(BagNetwork::register);'), version)

    write('Platform.java', '''
package dev.torchbag;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.WallTorchBlock;
import net.minecraft.world.level.block.state.BlockState;
IMPORTS

public final class Platform {
    public static void open(ServerPlayer player, int source) {
        ItemStack bag = BagAccess.at(player, source);
        if (!player.isAlive() || !(bag.getItem() instanceof TorchBagItem item)) return;
        SimpleMenuProvider provider = new SimpleMenuProvider((id, inv, p) -> new BagMenu(id, inv, item.tier, source, bag), bag.getHoverName());
        OPEN
    }
    public static boolean place(ServerPlayer player, BlockPos pos, BlockState state) {
        var level = player.serverLevel();
        Direction face = state.hasProperty(WallTorchBlock.FACING) ? state.getValue(WallTorchBlock.FACING) : Direction.UP;
        if (!level.mayInteract(player, pos) || player.server.isUnderSpawnProtection(level, pos, player) ||
            !player.mayUseItemAt(pos, face, new ItemStack(Items.TORCH))) return false;
        BlockSnapshot snapshot = BlockSnapshot.create(level.dimension(), level, pos);
        if (!level.setBlock(pos, state, 3)) return false;
        if (PLACE_EVENT) {
            snapshot.restore(true, false);
            return false;
        }
        return true;
    }
}
'''.replace('IMPORTS', '''
import net.minecraftforge.common.util.BlockSnapshot;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.network.NetworkHooks;
''' if old else '''
import net.neoforged.neoforge.common.util.BlockSnapshot;
import net.neoforged.neoforge.event.EventHooks;
''').replace('OPEN', 'NetworkHooks.openScreen(player, provider, buf -> { buf.writeVarInt(item.tier.ordinal()); buf.writeInt(source); });' if old else 'player.openMenu(provider, buf -> { buf.writeVarInt(item.tier.ordinal()); buf.writeInt(source); });')
       .replace('PLACE_EVENT', ('ForgeEventFactory' if old else 'EventHooks') + '.onBlockPlace(player, snapshot, face)'), version)

    write('ClientBootstrap.java', '''
package dev.torchbag;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.MenuScreens;
import org.lwjgl.glfw.GLFW;
IMPORTS

public final class ClientBootstrap {
    private static final KeyMapping OPEN = new KeyMapping("key.torch_bag.open", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_V, "key.categories.torch_bag");
    public static void init(IEventBus bus) {
        bus.addListener((RegisterKeyMappingsEvent event) -> event.register(OPEN));
        SCREEN_INIT
        TICK_INIT
    }
    private static void tick() {
        while (OPEN.consumeClick()) {
            Minecraft mc = Minecraft.getInstance();
            if (mc.player != null && mc.screen == null) BagNetwork.sendOpen();
        }
    }
}
'''.replace('IMPORTS', '''
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.TickEvent;
''' if old else '''
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.client.event.ClientTickEvent;
''').replace('SCREEN_INIT', 'bus.addListener((FMLClientSetupEvent event) -> event.enqueueWork(() -> MenuScreens.register(TorchBagMod.menuType(), BagScreen::new)));' if old else 'bus.addListener((RegisterMenuScreensEvent event) -> event.register(TorchBagMod.menuType(), BagScreen::new));')
       .replace('TICK_INIT', 'MinecraftForge.EVENT_BUS.addListener((TickEvent.ClientTickEvent event) -> { if (event.phase == TickEvent.Phase.END) tick(); });' if old else 'NeoForge.EVENT_BUS.addListener((ClientTickEvent.Post event) -> tick());'), version)

write('BagNetwork.java', '''
package dev.torchbag;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.simple.SimpleChannel;

public final class BagNetwork {
    private static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(new ResourceLocation(TorchBagMod.ID, "main"), () -> "1", "1"::equals, "1"::equals);
    private record Open() {}
    public static void init() {
        CHANNEL.messageBuilder(Open.class, 0, NetworkDirection.PLAY_TO_SERVER)
            .encoder((msg, buf) -> {}).decoder(buf -> new Open())
            .consumerMainThread((msg, context) -> {
                var player = context.get().getSender();
                if (player != null) Platform.open(player, -1);
                context.get().setPacketHandled(true);
            }).add();
    }
    public static void sendOpen() { CHANNEL.sendToServer(new Open()); }
}
''', 'forge-1.20.1')

write('BagNetwork.java', '''
package dev.torchbag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.PacketDistributor;

public final class BagNetwork {
    public record Open() implements CustomPacketPayload {
        public static final Type<Open> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath(TorchBagMod.ID, "open"));
        public static final StreamCodec<RegistryFriendlyByteBuf, Open> CODEC = StreamCodec.of((buf, msg) -> {}, buf -> new Open());
        public Type<Open> type() { return TYPE; }
    }
    public static void register(RegisterPayloadHandlersEvent event) {
        event.registrar("1").playToServer(Open.TYPE, Open.CODEC, (msg, ctx) -> ctx.enqueueWork(() -> {
            if (ctx.player() instanceof ServerPlayer player) Platform.open(player, -1);
        }));
    }
    public static void sendOpen() { PacketDistributor.sendToServer(new Open()); }
}
''', 'neoforge-1.21.1')
