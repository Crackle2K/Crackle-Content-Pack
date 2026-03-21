"""Download Gen 1 move data and per-Pokemon learnsets from PokeAPI."""

from __future__ import annotations
import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.pokemon_data import get_available_pokemon_ids


def _norm(name: str) -> str:
    """Normalise a PokeAPI name to underscored lowercase."""
    return name.replace("-", "_").lower()


# ── Learnset download ─────────────────────────────────────────────────────────

def _fetch_learnset(pokemon_id: int) -> tuple[int, list[dict]]:
    """Return (pokemon_id, learnset) where learnset is sorted by level."""
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/", timeout=15)
    r.raise_for_status()
    data = r.json()

    seen: set[str] = set()
    entries: list[dict] = []

    for move_entry in data["moves"]:
        for vgd in move_entry["version_group_details"]:
            vg   = vgd["version_group"]["name"]
            meth = vgd["move_learn_method"]["name"]
            if vg in ("red-blue", "yellow") and meth == "level-up":
                move_name = _norm(move_entry["move"]["name"])
                level     = vgd["level_learned_at"]
                key       = f"{move_name}@{level}"
                if key not in seen:
                    seen.add(key)
                    entries.append({"move": move_name, "level": level})

    entries.sort(key=lambda x: x["level"])
    return pokemon_id, entries


# ── Move data download ────────────────────────────────────────────────────────

def _fetch_move(move_name: str) -> tuple[str, dict | None]:
    """Download data for a single move (underscore name)."""
    api_slug = move_name.replace("_", "-")
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/move/{api_slug}/", timeout=12)
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        return move_name, None

    # Display name
    display_name = next(
        (e["name"] for e in data.get("names", []) if e["language"]["name"] == "en"),
        move_name.replace("_", " ").title(),
    )

    # Description
    desc = ""
    for entry in data.get("flavor_text_entries", []):
        if entry["language"]["name"] == "en":
            desc = entry["flavor_text"].replace("\n", " ").replace("\f", " ")[:100]
            break
    if not desc:
        for entry in data.get("effect_entries", []):
            if entry["language"]["name"] == "en":
                desc = entry.get("short_effect", "")[:100]
                break

    category = (data.get("damage_class") or {}).get("name", "status")

    # Stat changes (e.g. Growl lowers Attack by 1 stage)
    stat_effects = []
    for sc in data.get("stat_changes", []):
        stat_name = _norm(sc["stat"]["name"])
        change    = sc["change"]  # negative = lower, positive = raise
        # PokeAPI doesn't directly say "self" vs "opponent" for most moves;
        # positive changes are almost always self-boosts, negative are opponent drops
        target = "self" if change > 0 else "opponent"
        stat_effects.append({"stat": stat_name, "change": change, "target": target})

    result = {
        "display_name": display_name,
        "type":         data["type"]["name"],
        "category":     category,          # "physical" / "special" / "status"
        "power":        data.get("power")    or 0,
        "accuracy":     data.get("accuracy") or 100,
        "pp":           data.get("pp")       or 5,
        "priority":     data.get("priority", 0),
        "description":  desc,
    }
    if stat_effects:
        result["stat_effects"] = stat_effects
    return move_name, result


# ── Main entry point ──────────────────────────────────────────────────────────

def download_moves(moves_folder: str = "assets/moves") -> bool:
    """
    Download learnsets + move data for all available Gen 1 Pokemon.

    Writes:
        assets/moves/learnsets.json   — {str(pokemon_id): [{move, level}, ...]}
        assets/moves/moves_data.json  — {move_name: {type, category, power, …}}

    Returns True on success.
    """
    path = Path(moves_folder)
    path.mkdir(parents=True, exist_ok=True)

    available_ids = get_available_pokemon_ids()

    # ── Step 1: learnsets ─────────────────────────────────────────────────────
    print(f"Downloading learnsets for {len(available_ids)} Pokemon …")
    learnsets: dict[str, list] = {}
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(_fetch_learnset, pid): pid for pid in available_ids}
        for fut in as_completed(futures):
            try:
                pid, learnset = fut.result()
                learnsets[str(pid)] = learnset
                print(f"  ✓ #{pid}  ({len(learnset)} moves)")
            except Exception as exc:
                pid = futures[fut]
                print(f"  ✗ #{pid}: {exc}")

    # ── Step 2: collect unique moves ──────────────────────────────────────────
    all_moves: set[str] = set()
    for ls in learnsets.values():
        for entry in ls:
            all_moves.add(entry["move"])
    print(f"\nDownloading data for {len(all_moves)} unique moves …")

    # ── Step 3: move data ─────────────────────────────────────────────────────
    moves_data: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures2 = {pool.submit(_fetch_move, m): m for m in all_moves}
        for fut in as_completed(futures2):
            name, data = fut.result()
            if data:
                moves_data[name] = data
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name}: download failed")

    # ── Step 4: save ──────────────────────────────────────────────────────────
    (path / "learnsets.json").write_text(json.dumps(learnsets, indent=2))
    (path / "moves_data.json").write_text(json.dumps(moves_data, indent=2))
    print(f"\nSaved: {len(learnsets)} learnsets, {len(moves_data)} moves → {path}")
    return True


def check_moves_exist(moves_folder: str = "assets/moves") -> bool:
    p = Path(moves_folder)
    return (p / "learnsets.json").exists() and (p / "moves_data.json").exists()


if __name__ == "__main__":
    download_moves()
