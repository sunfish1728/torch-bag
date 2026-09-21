package dev.torchbag;
import net.minecraft.core.NonNullList;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemContainerContents;

public final class BagData {
    public static final int DEFAULT_RADIUS = 16;
    public static NonNullList<ItemStack> load(ItemStack bag, int size) {
        NonNullList<ItemStack> items = NonNullList.withSize(size, ItemStack.EMPTY);
        bag.getOrDefault(DataComponents.CONTAINER, ItemContainerContents.EMPTY).copyInto(items);
        return items;
    }
    public static void save(ItemStack bag, NonNullList<ItemStack> items) {
        bag.set(DataComponents.CONTAINER, ItemContainerContents.fromItems(items));
    }
    public static void copy(ItemStack source, ItemStack target) { target.applyComponents(source.getComponentsPatch()); }
    public static int radius(ItemStack bag) {
        int value = bag.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().getInt("TorchBagRadius");
        return validRadius(value) ? value : DEFAULT_RADIUS;
    }
    public static void setRadius(ItemStack bag, int radius) {
        if (!validRadius(radius)) return;
        CompoundTag tag = bag.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        tag.putInt("TorchBagRadius", radius);
        bag.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
    }
    private static boolean validRadius(int value) { return value == 8 || value == 16 || value == 32 || value == 64; }
}
