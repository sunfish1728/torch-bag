package dev.torchbag;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.WallTorchBlock;
import net.minecraft.world.level.block.state.BlockState;

import net.neoforged.neoforge.common.util.BlockSnapshot;
import net.neoforged.neoforge.event.EventHooks;


public final class Platform {
    public static void open(ServerPlayer player, int source) {
        ItemStack bag = BagAccess.at(player, source);
        if (!player.isAlive() || !(bag.getItem() instanceof TorchBagItem item)) return;
        SimpleMenuProvider provider = new SimpleMenuProvider((id, inv, p) -> new BagMenu(id, inv, item.tier, source, bag), bag.getHoverName());
        player.openMenu(provider, buf -> { buf.writeVarInt(item.tier.ordinal()); buf.writeInt(source); });
    }
    public static boolean place(ServerPlayer player, BlockPos pos, BlockState state) {
        var level = player.serverLevel();
        Direction face = state.hasProperty(WallTorchBlock.FACING) ? state.getValue(WallTorchBlock.FACING) : Direction.UP;
        if (!level.mayInteract(player, pos) || player.server.isUnderSpawnProtection(level, pos, player) ||
            !player.mayUseItemAt(pos, face, new ItemStack(Items.TORCH))) return false;
        BlockSnapshot snapshot = BlockSnapshot.create(level.dimension(), level, pos);
        if (!level.setBlock(pos, state, 3)) return false;
        if (EventHooks.onBlockPlace(player, snapshot, face)) {
            snapshot.restore();
            return false;
        }
        return true;
    }
}
