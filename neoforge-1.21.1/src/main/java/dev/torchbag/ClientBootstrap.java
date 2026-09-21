package dev.torchbag;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.MenuScreens;
import org.lwjgl.glfw.GLFW;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.client.event.ClientTickEvent;


public final class ClientBootstrap {
    private static final KeyMapping OPEN = new KeyMapping("key.torch_bag.open", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_V, "key.categories.torch_bag");
    public static void init(IEventBus bus) {
        bus.addListener((RegisterKeyMappingsEvent event) -> event.register(OPEN));
        bus.addListener((RegisterMenuScreensEvent event) -> event.register(TorchBagMod.menuType(), BagScreen::new));
        NeoForge.EVENT_BUS.addListener((ClientTickEvent.Post event) -> tick());
    }
    private static void tick() {
        while (OPEN.consumeClick()) {
            Minecraft mc = Minecraft.getInstance();
            if (mc.player != null && mc.screen == null) BagNetwork.sendOpen();
        }
    }
}
