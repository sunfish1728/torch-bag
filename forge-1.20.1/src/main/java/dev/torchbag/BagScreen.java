package dev.torchbag;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public final class BagScreen extends AbstractContainerScreen<BagMenu> {
    private static final ResourceLocation BACKGROUND = new ResourceLocation("minecraft", "textures/gui/container/generic_54.png");
    private static final ResourceLocation GEAR = new ResourceLocation(TorchBagMod.ID, "textures/gui/gear_button.png");
    private static final int[] RADII = {8, 16, 32, 64};
    private boolean settingsOpen;
    public BagScreen(BagMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
        imageWidth = 176;
        imageHeight = 114 + menu.rows * 18;
        inventoryLabelY = imageHeight - 94;
    }
    protected void renderBg(GuiGraphics g, float partial, int mouseX, int mouseY) {
        int x = leftPos, y = topPos;
        int upper = menu.rows * 18 + 17;
        g.blit(BACKGROUND, x, y, 0, 0, imageWidth, upper, 256, 256);
        g.blit(BACKGROUND, x, y + upper, 0, 126, imageWidth, 96, 256, 256);
        int gearState = inside(mouseX, mouseY, x + 177, y + 5, 20, 20) ? 20 : 0;
        g.blit(GEAR, x + 177, y + 5, 0, gearState, 20, 20, 20, 40);
        if (settingsOpen) renderSettings(g, mouseX, mouseY);
    }
    protected void renderLabels(GuiGraphics g, int mx, int my) {
        super.renderLabels(g, mx, my);
    }
    private void renderSettings(GuiGraphics g, int mx, int my) {
        int x = leftPos + 176, y = topPos + 28, w = 82, h = 184;
        bevel(g, x, y, x + w, y + h, false);
        g.drawString(font, Component.translatable("screen.torch_bag.settings"), x + 8, y + 8, 0x404040, false);
        g.drawString(font, Component.translatable("screen.torch_bag.radius"), x + 8, y + 22, 0x404040, false);
        for (int i = 0; i < RADII.length; i++) {
            int by = y + 35 + i * 18;
            boolean selected = menu.radius == RADII[i];
            boolean hover = inside(mx, my, x + 8, by, 66, 16);
            bevel(g, x + 8, by, x + 74, by + 16, selected);
            int color = selected ? 0xFFFFA000 : (hover ? 0xFFFFFFA0 : 0xFFFFFFFF);
            String label = Component.translatable("screen.torch_bag.radius_value", RADII[i]).getString();
            g.drawString(font, label, x + 41 - font.width(label) / 2, by + 4, color, true);
        }
        g.drawString(font, Component.translatable("screen.torch_bag.density"), x + 8, y + 109, 0x404040, false);
        for (int i = 0; i < 3; i++) {
            int by = y + 122 + i * 18;
            boolean selected = menu.density == i;
            boolean hover = inside(mx, my, x + 8, by, 66, 16);
            bevel(g, x + 8, by, x + 74, by + 16, selected);
            int color = selected ? 0xFFFFA000 : (hover ? 0xFFFFFFA0 : 0xFFFFFFFF);
            String label = Component.translatable("screen.torch_bag.density_" + i).getString();
            g.drawString(font, label, x + 41 - font.width(label) / 2, by + 4, color, true);
        }
    }
    private static void bevel(GuiGraphics g, int x1, int y1, int x2, int y2, boolean pressed) {
        int light = pressed ? 0xFF373737 : 0xFFFFFFFF;
        int dark = pressed ? 0xFFFFFFFF : 0xFF373737;
        g.fill(x1, y1, x2, y2, 0xFFC6C6C6);
        g.fill(x1, y1, x2, y1 + 1, light); g.fill(x1, y1, x1 + 1, y2, light);
        g.fill(x1, y2 - 1, x2, y2, dark); g.fill(x2 - 1, y1, x2, y2, dark);
    }
    private static boolean inside(double mx, double my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }
    public void render(GuiGraphics g, int mx, int my, float partial) {
        renderBackground(g);
        super.render(g, mx, my, partial);
        renderTooltip(g, mx, my);
    }
    public boolean mouseClicked(double mx, double my, int button) {
        if (button == 0 && inside(mx, my, leftPos + 177, topPos + 5, 20, 20)) {
            settingsOpen = !settingsOpen;
            return true;
        }
        if (button == 0 && settingsOpen) for (int i = 0; i < RADII.length; i++) {
            if (inside(mx, my, leftPos + 184, topPos + 63 + i * 18, 66, 16)) {
                if (minecraft != null && minecraft.gameMode != null)
                    minecraft.gameMode.handleInventoryButtonClick(menu.containerId, 100 + i);
                return true;
            }
        }
        if (button == 0 && settingsOpen) for (int i = 0; i < 3; i++) {
            if (inside(mx, my, leftPos + 184, topPos + 150 + i * 18, 66, 16)) {
                if (minecraft != null && minecraft.gameMode != null)
                    minecraft.gameMode.handleInventoryButtonClick(menu.containerId, 200 + i);
                return true;
            }
        }
        return super.mouseClicked(mx, my, button);
    }
}
