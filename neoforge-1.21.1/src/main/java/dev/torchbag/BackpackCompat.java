package dev.torchbag;
import net.minecraft.world.entity.player.Player;
import net.p3pp3rf1y.sophisticatedbackpacks.util.PlayerInventoryProvider;

public final class BackpackCompat {
    public static TorchSupply.Source find(Player player) {
        TorchSupply.Source[] result = {null};
        PlayerInventoryProvider.get().runOnBackpacks(player, (stack, handler, identifier, slot) -> {
            result[0] = TorchSupply.fromHandler(net.p3pp3rf1y.sophisticatedbackpacks.backpack.wrapper.BackpackWrapper.fromStack(stack).getInventoryHandler(), player);
            return result[0] != null;
        });
        return result[0];
    }
}
