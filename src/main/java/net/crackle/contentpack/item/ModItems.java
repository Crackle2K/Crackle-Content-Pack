package net.crackle.contentpack.item;

import net.crackle.contentpack.ContentPack;
import net.crackle.contentpack.item.custom.EnchantedGoldenOrangeItem;
import net.minecraft.item.Item;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.util.Identifier;
import net.minecraft.util.Rarity;

public class ModItems {
    public static final Item TANZANITE = registerItem("tanzanite", new Item(new Item.Settings()));
    public static final Item CAULIFLOWER = registerItem("cauliflower", new Item(new Item.Settings().food(ModFoodComponents.CAULIFLOWER)));
    public static final Item SULPHUR = registerItem("sulphur", new Item(new Item.Settings()));
    public static final Item ROCK = registerItem("rock", new Item(new Item.Settings()));
    public static final Item ORANGE = registerItem("orange", new Item(new Item.Settings().food(ModFoodComponents.ORANGE)));
    public static final Item GOLDEN_ORANGE = registerItem("golden_orange", new Item(new Item.Settings().rarity(Rarity.RARE).food(ModFoodComponents.GOLDEN_ORANGE)));
    public static final Item ENCHANTED_GOLDEN_ORANGE = registerItem("enchanted_golden_orange", new EnchantedGoldenOrangeItem(new Item.Settings().rarity(Rarity.EPIC).food(ModFoodComponents.ENCHANTED_GOLDEN_ORANGE)));

    private static Item registerItem(String name, Item item) {
        return Registry.register(Registries.ITEM, Identifier.of(ContentPack.MOD_ID, name), item);
    }

    public static void registerModItems() {
        ContentPack.LOGGER.info("Registering Mod Items for " + ContentPack.MOD_ID);

    }
}