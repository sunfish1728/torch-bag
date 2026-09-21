package dev.torchbag;
import net.minecraft.world.Container;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.items.IItemHandler;

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
