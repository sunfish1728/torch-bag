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
