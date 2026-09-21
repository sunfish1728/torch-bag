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
