package net.crackle.contentpack.item;

import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.crackle.contentpack.ContentPack;
import net.crackle.contentpack.block.ModBlocks;
import net.minecraft.item.ItemGroup;
import net.minecraft.item.ItemStack;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.text.Text;
import net.minecraft.util.Identifier;

public class ModItemGroups {
    public static final ItemGroup CONTENTPACK_ITEMS_GROUP = Registry.register(Registries.ITEM_GROUP,
            Identifier.of(ContentPack.MOD_ID, "contentpack_items"),
            FabricItemGroup.builder().icon(() -> new ItemStack(ModItems.TANZANITE))
                    .displayName(Text.translatable("itemgroup.contentpack.contentpack_items"))
                    .entries((displayContext, entries) -> {
                        entries.add(ModItems.TANZANITE);
                        entries.add(ModItems.CAULIFLOWER);
                        entries.add(ModItems.SULPHUR);
                        entries.add(ModItems.ORANGE);
                        entries.add(ModItems.GOLDEN_ORANGE);
                    }).build());


    public static void registerItemGroups() {
        ContentPack.LOGGER.info("Registering Item Groups for " + ContentPack.MOD_ID);
    }
}