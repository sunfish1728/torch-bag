package dev.torchbag;
import java.util.EnumMap;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.*;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;
import net.minecraftforge.registries.DeferredRegister;


@Mod(TorchBagMod.ID)
public final class TorchBagMod {
    public static final String ID = "torch_bag";
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(Registries.ITEM, ID);
    private static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, ID);
    private static final EnumMap<BagTier, Supplier<TorchBagItem>> BAGS = new EnumMap<>(BagTier.class);
    private static final EnumMap<BombTier, Supplier<TorchBombItem>> BOMBS = new EnumMap<>(BombTier.class);
    private static final Supplier<MenuType<BagMenu>> MENU = MENUS.register("bag", () -> IForgeMenuType.create(BagMenu::new));
    static {
        for (BagTier tier : BagTier.values()) BAGS.put(tier, ITEMS.register(tier.id + "_torch_bag", () -> new TorchBagItem(tier)));
        for (BombTier tier : BombTier.values()) BOMBS.put(tier, ITEMS.register(tier.id, () -> new TorchBombItem(tier)));
    }
    public static TorchBagItem item(BagTier tier) { return BAGS.get(tier).get(); }
    public static TorchBombItem bomb(BombTier tier) { return BOMBS.get(tier).get(); }
    public static MenuType<BagMenu> menuType() { return MENU.get(); }
    public TorchBagMod() {
        var bus = FMLJavaModLoadingContext.get().getModEventBus();
        ITEMS.register(bus); MENUS.register(bus);
        bus.addListener(this::setup);
        bus.addListener(this::creative);
        
        MinecraftForge.EVENT_BUS.addListener((TickEvent.PlayerTickEvent event) -> {
            if (event.phase == TickEvent.Phase.END && event.player instanceof net.minecraft.server.level.ServerPlayer player) AutoPlacer.tick(player);
        });
        MinecraftForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent event) -> {
            if (event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player) { AutoPlacer.forget(player); BombPlacer.cancel(player.getUUID()); }
        });
        MinecraftForge.EVENT_BUS.addListener((TickEvent.ServerTickEvent event) -> { if (event.phase == TickEvent.Phase.END && event.haveTime()) BombPlacer.tick(event.getServer()); });
        MinecraftForge.EVENT_BUS.addListener((ServerStoppedEvent event) -> { AutoPlacer.clear(); BombPlacer.clear(); });

        BagNetwork.init();
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
