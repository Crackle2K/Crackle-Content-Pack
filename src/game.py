"""Main game class for Pokemon Juno."""

import json
import random
from pathlib import Path
from typing import Optional

from src.entities.pokemon import Pokemon
from src.entities.trainer import Trainer
from src.battle.battle import Battle
from src.ui.pygame_ui import PygameUI
from src.core.pokemon_data import get_available_pokemon_ids
from src.core.pokemon_constraints import STARTER_COUNTERS, pick_encounter_pokemon


class Game:
    """Main game controller."""

    STARTERS       = [1, 4, 7]   # Bulbasaur, Charmander, Squirtle
    SECRET_STARTER_ID = 25       # Pikachu (Konami unlock)
    STARTING_MONEY = 500

    # Item catalog cache for in-battle item use
    _catalog: dict = {}

    def __init__(self):
        self.ui          = PygameUI()
        self.player: Optional[Trainer] = None
        self.running     = True
        self.save_slot: Optional[int] = None
        self.battles_won = 0

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self):
        try:
            self.ui.show_message("Welcome to Pokemon Juno!")
            self._load_catalog()

            while self.running:
                if self.ui.quit_requested:
                    break
                choice = self.ui.show_main_menu()
                if choice == "new_game":
                    slot = self.ui.show_save_slot_selection()
                    if slot is not None and not self.ui.quit_requested:
                        self._new_game(slot)
                elif choice == "exit":
                    self.running = False

            if not self.ui.quit_requested:
                self.ui.show_message("Thanks for playing Pokemon Juno!")
        finally:
            self.ui.quit()

    # ── New game ──────────────────────────────────────────────────────────────

    def _new_game(self, slot: int):
        self.save_slot   = slot
        self.battles_won = 0

        name = self.ui.get_player_name()
        if self.ui.quit_requested:
            return

        self.player       = Trainer(name, is_player=True)
        self.player.money = self.STARTING_MONEY

        self.ui.show_message(f"Welcome, {name}! Choose your first Pokemon!")
        starter = self._choose_starter()
        if self.ui.quit_requested:
            return

        self.player.add_pokemon(starter)
        self.ui.show_message(f"Excellent choice! You received {starter.name}!")
        self.ui.wait_for_input()

        self._save_game()
        self._rival_battle()

    # ── Starter selection ─────────────────────────────────────────────────────

    def _choose_starter(self) -> Pokemon:
        starter_ids = list(self.STARTERS)
        starters    = [Pokemon(pid, level=5) for pid in starter_ids]

        while True:
            result = self.ui.show_pokemon_selection(starters, "Choose your starter Pokemon:")

            if result == "konami":
                if self.SECRET_STARTER_ID not in starter_ids:
                    starter_ids.append(self.SECRET_STARTER_ID)
                    starters = [Pokemon(pid, level=5) for pid in starter_ids]
                self.ui.show_message("★ A secret Pokemon has appeared!")
                self.ui.wait_for_input()
                continue

            return starters[int(result)]

    # ── Rival battle ──────────────────────────────────────────────────────────

    def _rival_battle(self):
        if self.ui.quit_requested:
            return
        rival           = Trainer("Rival Blue", is_player=False)
        starter         = self.player.team[0]
        rival_pokemon_id = STARTER_COUNTERS.get(starter.id, random.choice(self.STARTERS))
        rival.add_pokemon(Pokemon(rival_pokemon_id, level=5))

        self.ui.clear_screen()
        self.ui.show_message("Your rival Blue appears!")
        self.ui.show_message(f'"I\'ll show you how it\'s done, {self.player.name}!"')
        self.ui.wait_for_input()

        self._run_battle(rival)
        if not self.ui.quit_requested:
            self._hub_loop()

    # ── Hub loop ──────────────────────────────────────────────────────────────

    def _hub_loop(self):
        available_ids = get_available_pokemon_ids()

        while self.running and not self.ui.quit_requested:
            self._save_game()
            action = self.ui.show_hub_menu(self.player, self.battles_won)

            if self.ui.quit_requested:
                break

            if action == "battle":
                self._do_encounter(available_ids)
            elif action == "shop":
                self.ui.show_shop(self.player)
            elif action == "inventory":
                self.ui.show_inventory(self.player)
            elif action == "pokemon_center":
                self.ui.show_pokemon_center(self.player)
            elif action == "settings":
                result = self.ui.show_settings(self.player, self.battles_won)
                self._save_game()
                if result == "quit" or self.ui.quit_requested:
                    self.running = False
                    break

    # ── Random encounter ──────────────────────────────────────────────────────

    def _do_encounter(self, available_ids: list):
        self.battles_won += 1

        trainer_names = [
            "Youngster", "Lass", "Bug Catcher", "Swimmer",
            "Hiker", "Camper", "Picnicker", "Beauty",
            "Gentleman", "School Kid", "Ace Trainer",
        ]

        # Use team average level for scaling
        team_levels = [p.level for p in self.player.team]
        avg_level   = sum(team_levels) // max(1, len(team_levels))
        num_pokemon = min(3, 1 + self.battles_won // 3)

        # Wild encounter — player can catch these Pokemon
        opponent = Trainer(f"Wild Pokemon #{self.battles_won}",
                           is_player=False, is_wild=True)

        for _ in range(num_pokemon):
            target = random.randint(max(5, avg_level - 3), min(100, avg_level + 3))
            pid, level = pick_encounter_pokemon(available_ids, target)
            opponent.add_pokemon(Pokemon(pid, level=level))

        self.ui.clear_screen()
        first_pokemon = opponent.get_active_pokemon()
        self.ui.show_message(f"A wild {first_pokemon.name} appeared!")
        self.ui.wait_for_input()

        won = self._run_battle(opponent)

        if self.ui.quit_requested:
            return

        if not won and not (self.player.team and
                            any(not p.is_fainted for p in self.player.team)):
            penalty = self.player.money // 2
            self.player.money -= penalty
            self.ui.show_message("You blacked out!")
            if penalty:
                self.ui.show_message(f"You lost ${penalty}...")
            self.ui.wait_for_input()
            self.player.heal_team()
        elif not won:
            penalty = self.player.money // 2
            self.player.money -= penalty
            self.ui.show_message("You were defeated!")
            if penalty:
                self.ui.show_message(f"You lost ${penalty}...")
            self.ui.wait_for_input()
            self.player.heal_team()

    # ── Save / load ───────────────────────────────────────────────────────────

    def _save_game(self):
        if not hasattr(self, 'save_slot') or self.player is None:
            return

        save_folder = Path("saves")
        save_folder.mkdir(exist_ok=True)

        save_data = {
            'player_name':    self.player.name,
            'pokemon_count':  len(self.player.team),
            'pokemon_ids':    [p.id    for p in self.player.team],
            'pokemon_levels': [p.level for p in self.player.team],
            'battles_won':    self.battles_won,
            'money':          self.player.money,
            'items':          self.player.items,
        }

        with open(save_folder / f"save_{self.save_slot}.json", "w") as f:
            json.dump(save_data, f, indent=2)

    def _load_catalog(self):
        p = Path("assets/items/catalog.json")
        if p.exists():
            try:
                self._catalog = {it["slug"]: it for it in json.loads(p.read_text())}
            except Exception:
                self._catalog = {}

    # ── Battle runner ─────────────────────────────────────────────────────────

    def _run_battle(self, opponent: Trainer) -> bool:
        """Run a battle. Returns True if the player won (or caught a Pokemon)."""
        battle = Battle(self.player, opponent)
        self.ui.start_battle(battle)
        self.ui.clear_screen()

        events = battle.start()
        self.ui.show_battle_events(events)

        while not battle.is_over and not self.ui.quit_requested:
            self.ui.show_battle_status(self.player, opponent)

            if battle.player_must_switch():
                switch_idx = self.ui.show_forced_switch(self.player)
                events     = battle.execute_forced_switch(switch_idx)
                self.ui.show_battle_events(events)
                continue

            action, index = self.ui.show_battle_menu(battle)

            if self.ui.quit_requested:
                return False
            if action == "back":
                continue
            if action == "run":
                if not opponent.is_wild:
                    self.ui.show_message("Can't escape from a trainer battle!")
                else:
                    self.ui.show_message("Got away safely!")
                    self.ui.wait_for_input()
                    return False
                continue

            if action == "item":
                slug = index  # string slug
                self._apply_item_in_battle(battle, slug)
                continue

            if action == "catch":
                ball_slug = index  # string or None
                if ball_slug is None:
                    self.ui.show_message("You have no Pokeballs!")
                    continue
                self.player.use_item(ball_slug)
                caught, events = battle.attempt_catch(ball_slug)
                self.ui.show_battle_events(events)
                if caught and battle.caught_pokemon:
                    if len(self.player.team) < Trainer.MAX_TEAM_SIZE:
                        self.player.add_pokemon(battle.caught_pokemon)
                        self.ui.show_message(
                            f"{battle.caught_pokemon.get_display_name()} joined your team!")
                    else:
                        self.ui.show_message(
                            f"Team is full — {battle.caught_pokemon.get_display_name()} "
                            f"could not be kept.")
                    self.ui.wait_for_input()
                    self.ui.show_battle_result(battle)
                    return True
                continue

            self.ui.clear_screen()
            events = battle.execute_turn(action, index)
            self.ui.show_battle_events(events)

        if self.ui.quit_requested:
            return False

        self.ui.show_battle_result(battle)
        self.ui.wait_for_input()

        player_won = battle.winner == self.player or battle.caught_pokemon is not None
        if player_won:
            self._grant_battle_rewards(battle, opponent)

        return player_won

    def _apply_item_in_battle(self, battle: Battle, slug: str):
        """Use a healing/recovery item on the active Pokemon, then let the AI move."""
        if not self.player.use_item(slug):
            self.ui.show_message("No items left!")
            return

        meta   = self._catalog.get(slug, {})
        effect = meta.get("effect", {})
        etype  = effect.get("type", "none")
        amount = effect.get("amount", 0)
        pk     = self.player.get_active_pokemon()

        if etype == "heal":
            if isinstance(amount, int) and amount > 0:
                healed = pk.heal(amount)
                self.ui.show_message(f"{pk.get_display_name()} +{healed} HP!")
            elif amount == "full":
                pk.full_restore()
                self.ui.show_message(f"{pk.get_display_name()} fully restored!")
            else:
                self.ui.show_message(effect.get("note", "Item used!"))
        elif etype == "revive":
            pass  # Can't revive in battle (active pokemon is not fainted)
        elif etype == "pp_restore":
            for move in pk.moves:
                move.current_pp = min(move.max_pp, move.current_pp + amount)
            self.ui.show_message(f"{pk.get_display_name()} PP restored!")
        else:
            self.ui.show_message("Can't use that here!")
            self.player.add_item(slug)  # refund
            return

        # AI gets to act since player spent their turn
        events = battle.execute_ai_turn()
        self.ui.show_battle_events(events)

    # ── Post-battle rewards ───────────────────────────────────────────────────

    def _grant_battle_rewards(self, battle: Battle, opponent: Trainer):
        """Grant XP (to Pokemon that fought) and money."""
        total_xp = sum(p.level * 50 for p in opponent.team)
        battlers = list(battle.player_battlers) if battle.player_battlers else self.player.team
        xp_each  = total_xp // max(1, len(battlers))

        level_ups: list[tuple] = []   # (pokemon, new_move_names)
        for pk in battlers:
            leveled, new_moves = pk.gain_exp(xp_each)
            if leveled:
                level_ups.append((pk, new_moves))

        self.ui.show_message(
            f"Victory! {', '.join(p.get_display_name() for p in battlers)} "
            f"gained {xp_each} EXP!")

        for pk, new_moves in level_ups:
            self.ui.show_message(f"{pk.get_display_name()} grew to Lv. {pk.level}!")
            self.ui.wait_for_input()
            for move_name in new_moves:
                if len(pk.moves) < 4:
                    if pk.learn_move(move_name):
                        display = move_name.replace("_", " ").title()
                        self.ui.show_message(
                            f"{pk.get_display_name()} learned {display}!")
                        self.ui.wait_for_input()
                # If 4 moves already, skip silently (can be improved later)

        prize = sum(p.level * 30 for p in opponent.team) + 50
        self.player.add_money(prize)
        self.ui.show_message(f"You received ${prize}!")
        self.ui.wait_for_input()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
