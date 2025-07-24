package net.crackle.contentpack.item;

import net.crackle.contentpack.ContentPack;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.minecraft.item.Item;
import net.minecraft.item.ItemGroups;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.util.Identifier;

public class ModItems {
    public static final Item TANZANITE = registerItem("tanzanite", new Item(new Item.Settings()));
    public static final Item CAULIFLOWER = registerItem("cauliflower", new Item(new Item.Settings().food(ModFoodComponents.CAULIFLOWER)));
    public static final Item SULFUR = registerItem("sulfur", new Item(new Item.Settings()));

    private static Item registerItem(String name, Item item) {
        return Registry.register(Registries.ITEM, Identifier.of(ContentPack.MOD_ID, name), item);
    }

    public static void registerModItems() {
        ContentPack.LOGGER.info("Registering Mod Items for " + ContentPack.MOD_ID);

    }
}