from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
code = '''package dev.torchbag;

import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import EVENT_PACKAGE.ScreenEvent;
import SUBSCRIBE_IMPORT;
import SUBSCRIBER_IMPORT;
import DIST_IMPORT;

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
'''
for version in ['forge-1.20.1','neoforge-1.21.1']:
    old = version.startswith('forge')
    text = code.replace('EVENT_PACKAGE','net.minecraftforge.client.event' if old else 'net.neoforged.neoforge.client.event')
    text = text.replace('EVENT_BUS','net.minecraftforge.common.MinecraftForge.EVENT_BUS' if old else 'net.neoforged.neoforge.common.NeoForge.EVENT_BUS')
    text = text.replace('SUBSCRIBE_IMPORT','net.minecraftforge.eventbus.api.SubscribeEvent' if old else 'net.neoforged.bus.api.SubscribeEvent')
    text = text.replace('SUBSCRIBER_IMPORT','net.minecraftforge.fml.common.Mod.EventBusSubscriber' if old else 'net.neoforged.fml.common.EventBusSubscriber')
    text = text.replace('DIST_IMPORT','net.minecraftforge.api.distmarker.Dist' if old else 'net.neoforged.api.distmarker.Dist')
    (ROOT / version / 'src/main/java/dev/torchbag/ClientVisualTest.java').write_text(text,encoding='utf-8')
