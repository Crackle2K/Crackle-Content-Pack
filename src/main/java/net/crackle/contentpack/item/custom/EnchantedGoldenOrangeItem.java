package net.crackle.contentpack.item.custom;

import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;

public class EnchantedGoldenOrangeItem extends Item {
    public EnchantedGoldenOrangeItem(Settings settings) {
        super(settings);
    }

    @Override
    public boolean hasGlint(ItemStack stack) {
        return true;
    }
}
