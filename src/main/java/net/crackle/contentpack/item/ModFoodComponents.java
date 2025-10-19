package net.crackle.contentpack.item;

import net.minecraft.component.type.FoodComponent;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.stat.Stat;

public class ModFoodComponents {
    public static final FoodComponent CAULIFLOWER = new FoodComponent.Builder().nutrition(3).saturationModifier(0.25f)
            .statusEffect(new StatusEffectInstance(StatusEffects.HEALTH_BOOST, 200), 0.15f).build();
    public static final FoodComponent ORANGE = new FoodComponent.Builder().nutrition(4).saturationModifier(0.3f)
            .statusEffect(new StatusEffectInstance(StatusEffects.STRENGTH, 200), 0.2f).build();
    public static final FoodComponent GOLDEN_ORANGE = new FoodComponent.Builder().nutrition(4).saturationModifier(0.3f)
            .statusEffect(new StatusEffectInstance(StatusEffects.STRENGTH, 400), 1f)
            .statusEffect(new StatusEffectInstance(StatusEffects.SPEED, 400), 1f).build();
    public static final FoodComponent ENCHANTED_GOLDEN_ORANGE = new FoodComponent.Builder().nutrition(6).saturationModifier(0.5f)
            .statusEffect(new StatusEffectInstance(StatusEffects.STRENGTH, 600), 1f)
            .statusEffect(new StatusEffectInstance(StatusEffects.SPEED, 600), 1f)
            .statusEffect(new StatusEffectInstance(StatusEffects.REGENERATION, 200), 1f)
            .statusEffect(new StatusEffectInstance(StatusEffects.FIRE_RESISTANCE, 1600), 1f).build();

}