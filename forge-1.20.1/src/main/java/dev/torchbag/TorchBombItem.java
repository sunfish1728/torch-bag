package dev.torchbag;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;

public final class TorchBombItem extends Item {
    public final BombTier tier;
    public TorchBombItem(BombTier tier) { super(new Item.Properties().stacksTo(16)); this.tier = tier; }
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide && player instanceof ServerPlayer server) {
            if (!BombPlacer.release(server, tier)) return InteractionResultHolder.fail(stack);
            if (!player.getAbilities().instabuild) stack.shrink(1);
            player.getCooldowns().addCooldown(this, 20);
            player.awardStat(Stats.ITEM_USED.get(this));
            level.playSound(null, player.blockPosition(), SoundEvents.ENDER_EYE_DEATH, SoundSource.PLAYERS, 1.0F, 0.8F + tier.ordinal() * 0.15F);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }
    public void appendHoverText(ItemStack stack, Level level, List<Component> text, TooltipFlag flag) {
        text.add(Component.translatable("tooltip.torch_bag.bomb_radius", tier.chunkRadius).withStyle(ChatFormatting.GOLD));
        text.add(Component.translatable("tooltip.torch_bag.bomb_usage").withStyle(ChatFormatting.GRAY));
    }
}
