package dev.torchbag;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.item.ItemStack;

public final class BagData {
    public static final int DEFAULT_RADIUS = 16;
    public static final int DENSITY_LOW = 0, DENSITY_MEDIUM = 1, DENSITY_HIGH = 2;
    public static NonNullList<ItemStack> load(ItemStack bag, int size) {
        NonNullList<ItemStack> items = NonNullList.withSize(size, ItemStack.EMPTY);
        if (bag.hasTag()) ContainerHelper.loadAllItems(bag.getTag().getCompound("TorchBag"), items);
        return items;
    }
    public static void save(ItemStack bag, NonNullList<ItemStack> items) {
        CompoundTag data = new CompoundTag();
        ContainerHelper.saveAllItems(data, items);
        bag.getOrCreateTag().put("TorchBag", data);
    }
    public static void copy(ItemStack source, ItemStack target) {
        if (source.hasTag()) target.setTag(source.getTag().copy());
    }
    public static int radius(ItemStack bag) {
        int value = bag.hasTag() ? bag.getTag().getInt("TorchBagRadius") : 0;
        return validRadius(value) ? value : DEFAULT_RADIUS;
    }
    public static void setRadius(ItemStack bag, int radius) {
        if (validRadius(radius)) bag.getOrCreateTag().putInt("TorchBagRadius", radius);
    }
    public static int density(ItemStack bag) {
        int value = bag.hasTag() ? bag.getTag().getInt("TorchBagDensity") : DENSITY_LOW;
        return validDensity(value) ? value : DENSITY_LOW;
    }
    public static void setDensity(ItemStack bag, int density) {
        if (validDensity(density)) bag.getOrCreateTag().putInt("TorchBagDensity", density);
    }
    private static boolean validRadius(int value) { return value == 8 || value == 16 || value == 32 || value == 64; }
    private static boolean validDensity(int value) { return value >= DENSITY_LOW && value <= DENSITY_HIGH; }
}
