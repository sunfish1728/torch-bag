package dev.torchbag;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.MenuScreens;
import org.lwjgl.glfw.GLFW;

import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.TickEvent;


public final class ClientBootstrap {
    private static final KeyMapping OPEN = new KeyMapping("key.torch_bag.open", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_V, "key.categories.torch_bag");
    public static void init(IEventBus bus) {
        bus.addListener((RegisterKeyMappingsEvent event) -> event.register(OPEN));
        bus.addListener((FMLClientSetupEvent event) -> event.enqueueWork(() -> MenuScreens.register(TorchBagMod.menuType(), BagScreen::new)));
        MinecraftForge.EVENT_BUS.addListener((TickEvent.ClientTickEvent event) -> { if (event.phase == TickEvent.Phase.END) tick(); });
    }
    private static void tick() {
        while (OPEN.consumeClick()) {
            Minecraft mc = Minecraft.getInstance();
            if (mc.player != null && mc.screen == null) BagNetwork.sendOpen();
        }
    }
}
