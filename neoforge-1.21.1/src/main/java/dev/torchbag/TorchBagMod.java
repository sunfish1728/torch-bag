package dev.torchbag;
import java.util.EnumMap;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.*;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.registries.DeferredRegister;


@Mod(TorchBagMod.ID)
public final class TorchBagMod {
    public static final String ID = "torch_bag";
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(Registries.ITEM, ID);
    private static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, ID);
    private static final EnumMap<BagTier, Supplier<TorchBagItem>> BAGS = new EnumMap<>(BagTier.class);
    private static final EnumMap<BombTier, Supplier<TorchBombItem>> BOMBS = new EnumMap<>(BombTier.class);
    private static final Supplier<MenuType<BagMenu>> MENU = MENUS.register("bag", () -> IMenuTypeExtension.create(BagMenu::new));
    static {
        for (BagTier tier : BagTier.values()) BAGS.put(tier, ITEMS.register(tier.id + "_torch_bag", () -> new TorchBagItem(tier)));
        for (BombTier tier : BombTier.values()) BOMBS.put(tier, ITEMS.register(tier.id, () -> new TorchBombItem(tier)));
    }
    public static TorchBagItem item(BagTier tier) { return BAGS.get(tier).get(); }
    public static TorchBombItem bomb(BombTier tier) { return BOMBS.get(tier).get(); }
    public static MenuType<BagMenu> menuType() { return MENU.get(); }
    public TorchBagMod(IEventBus bus) {
        
        ITEMS.register(bus); MENUS.register(bus);
        bus.addListener(this::setup);
        bus.addListener(this::creative);
        
        NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post event) -> {
            if (event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player) AutoPlacer.tick(player);
        });
        NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent event) -> {
            if (event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player) { AutoPlacer.forget(player); BombPlacer.cancel(player.getUUID()); }
        });
        NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post event) -> { if (event.hasTime()) BombPlacer.tick(event.getServer()); });
        NeoForge.EVENT_BUS.addListener((ServerStoppedEvent event) -> { AutoPlacer.clear(); BombPlacer.clear(); });

        bus.addListener(BagNetwork::register);
        if (FMLEnvironment.dist == Dist.CLIENT) ClientBootstrap.init(bus);
    }
    private void setup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> { if (ModList.get().isLoaded("curios")) CuriosCompat.register(); });
    }
    private void creative(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) {
            for (BagTier tier : BagTier.values()) event.accept(item(tier));
            for (BombTier tier : BombTier.values()) event.accept(bomb(tier));
        }
    }
}
