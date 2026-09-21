package dev.torchbag;

import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod.EventBusSubscriber;
import net.minecraftforge.api.distmarker.Dist;

/** Development-only renderer check. Excluded from the distributable jar. */
@EventBusSubscriber(modid = TorchBagMod.ID, value = Dist.CLIENT)
public final class ClientVisualTest {
    private static int frames;
    @SubscribeEvent
    public static void render(ScreenEvent.Render.Post event) {
        if (!Boolean.getBoolean("torchbag.visualTest")) return;
        Minecraft mc = Minecraft.getInstance();
        if (event.getScreen() == null || mc.getOverlay() != null) return;
        frames++;
        if (frames == 100) { mc.stop(); return; }
        if (frames != 60) return;
        BagTier tier = BagTier.LEATHER;
        Inventory inventory = new Inventory(null);
        inventory.setItem(0, new ItemStack(TorchBagMod.item(tier)));
        BagMenu menu = new BagMenu(1, inventory, tier, -1, null);
        menu.torchCount = tier.slots() * 64;
        for (int i = 0; i < menu.visibleSlots; i++) menu.getSlot(i).set(new ItemStack(Items.TORCH, 64));
        BagScreen screen = new BagScreen(menu, inventory, TorchBagMod.item(tier).getDescription());
        screen.init(mc, mc.getWindow().getGuiScaledWidth(), mc.getWindow().getGuiScaledHeight());
        screen.mouseClicked((mc.getWindow().getGuiScaledWidth() + 176) / 2.0 + 1, (mc.getWindow().getGuiScaledHeight() - 222) / 2.0 + 10, 0);
        var graphics = event.getGuiGraphics();
        graphics.flush();
        com.mojang.blaze3d.systems.RenderSystem.clear(16640, Minecraft.ON_OSX);
        graphics.pose().pushPose();
        graphics.fill(0,0,mc.getWindow().getGuiScaledWidth(),mc.getWindow().getGuiScaledHeight(),0xFF252830);
        screen.render(graphics,-100,-100,0F);
        graphics.flush();
        graphics.pose().popPose();
        Screenshot.grab(mc.gameDirectory,"torch-bag.png",mc.getMainRenderTarget(),c -> System.out.println("TORCH_BAG_SCREENSHOT " + c.getString()));
    }
}
