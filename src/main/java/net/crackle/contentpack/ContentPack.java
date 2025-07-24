package net.crackle.contentpack;

import net.crackle.contentpack.block.ModBlocks;
import net.crackle.contentpack.item.ModItemGroups;
import net.crackle.contentpack.item.ModItems;
import net.fabricmc.api.ModInitializer;

import net.fabricmc.fabric.api.registry.FuelRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ContentPack implements ModInitializer {


	public static final String MOD_ID = "contentpack";
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	@Override
	public void onInitialize() {

		ModItems.registerModItems();
		ModBlocks.registerModBlocks();

		ModItemGroups.registerItemGroups();

		FuelRegistry.INSTANCE.add(ModItems.SULFUR, 600);

	}
}