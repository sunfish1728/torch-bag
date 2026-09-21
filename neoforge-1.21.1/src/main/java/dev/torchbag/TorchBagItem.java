package dev.torchbag;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

public final class TorchBagItem extends Item {
    public final BagTier tier;
    public TorchBagItem(BagTier tier) { super(new Item.Properties().stacksTo(1)); this.tier = tier; }
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player instanceof ServerPlayer server) Platform.open(server, hand == InteractionHand.MAIN_HAND ? player.getInventory().selected : 40);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }
    public InteractionResult useOn(UseOnContext context) {
        Player player = context.getPlayer();
        if (player == null) return InteractionResult.PASS;
        return use(context.getLevel(), player, context.getHand()).getResult();
    }
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> text, TooltipFlag flag) {
        text.add(Component.translatable("tooltip.torch_bag.capacity", tier.slots(), BagData.radius(stack)).withStyle(ChatFormatting.GRAY));
        text.add(Component.translatable("tooltip.torch_bag.density", Component.translatable("screen.torch_bag.density_" + BagData.density(stack))).withStyle(ChatFormatting.GRAY));
        text.add(Component.translatable("tooltip.torch_bag.usage").withStyle(ChatFormatting.GOLD));
        text.add(Component.translatable("tooltip.torch_bag.curios").withStyle(ChatFormatting.GRAY));
    }
}
