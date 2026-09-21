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
