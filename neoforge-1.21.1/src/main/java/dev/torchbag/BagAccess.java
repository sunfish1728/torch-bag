package dev.torchbag;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.fml.ModList;

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
