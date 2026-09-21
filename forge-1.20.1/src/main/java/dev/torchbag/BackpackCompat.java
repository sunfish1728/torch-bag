package dev.torchbag;
import net.minecraft.world.entity.player.Player;
import net.p3pp3rf1y.sophisticatedbackpacks.util.PlayerInventoryProvider;

public final class BackpackCompat {
    public static TorchSupply.Source find(Player player) {
        TorchSupply.Source[] result = {null};
        PlayerInventoryProvider.get().runOnBackpacks(player, (stack, handler, identifier, slot) -> {
            result[0] = stack.getCapability(net.p3pp3rf1y.sophisticatedbackpacks.api.CapabilityBackpackWrapper.getCapabilityInstance()).map(w -> TorchSupply.fromHandler(w.getInventoryHandler(), player)).orElse(null);
            return result[0] != null;
        });
        return result[0];
    }
}
