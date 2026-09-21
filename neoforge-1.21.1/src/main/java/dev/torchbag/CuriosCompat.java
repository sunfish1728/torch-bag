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
