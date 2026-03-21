"""Download item sprites and catalog data from PokeAPI."""

import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

# ── Curated item list ────────────────────────────────────────────────────────
# Each tuple is (slug, category_label)
FEATURED_ITEMS: list[tuple[str, str]] = [
    # Pokéballs
    ("poke-ball",   "Pokeballs"),
    ("great-ball",  "Pokeballs"),
    ("ultra-ball",  "Pokeballs"),
    # Medicine
    ("potion",         "Medicine"),
    ("super-potion",   "Medicine"),
    ("hyper-potion",   "Medicine"),
    ("max-potion",     "Medicine"),
    ("revive",         "Medicine"),
    # Berries
    ("oran-berry",    "Berries"),
    ("sitrus-berry",  "Berries"),
    ("lum-berry",     "Berries"),
    ("chesto-berry",  "Berries"),
    ("pecha-berry",   "Berries"),
    ("leppa-berry",   "Berries"),
]

# Override prices for items with cost=0 in the API (berries are usually found,
# not bought, so PokeAPI lists them at 0).
_BERRY_PRICES: dict[str, int] = {
    "oran-berry":   80,
    "sitrus-berry": 200,
    "lum-berry":    250,
    "chesto-berry": 100,
    "pecha-berry":  100,
    "leppa-berry":  150,
}

# What each item does in this game
_EFFECTS: dict[str, dict] = {
    "poke-ball":     {"type": "pokeball", "note": "For future use"},
    "great-ball":    {"type": "pokeball", "note": "For future use"},
    "ultra-ball":    {"type": "pokeball", "note": "For future use"},
    "potion":        {"type": "heal", "amount": 20},
    "super-potion":  {"type": "heal", "amount": 50},
    "hyper-potion":  {"type": "heal", "amount": 200},
    "max-potion":    {"type": "heal", "amount": "full"},
    "revive":        {"type": "revive", "amount": "half"},
    "oran-berry":    {"type": "heal", "amount": 10},
    "sitrus-berry":  {"type": "heal", "amount": 25},
    "lum-berry":     {"type": "heal", "amount": 0, "note": "Cures all status"},
    "chesto-berry":  {"type": "heal", "amount": 0, "note": "Cures sleep"},
    "pecha-berry":   {"type": "heal", "amount": 0, "note": "Cures poison"},
    "leppa-berry":   {"type": "pp_restore", "amount": 10},
}


def _download_one(slug: str, category: str, items_path: Path) -> tuple[str, bool, object]:
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/item/{slug}", timeout=12)
        r.raise_for_status()
        data = r.json()

        name: str = data["name"]
        cost: int = data.get("cost", 0)
        if cost == 0 and name in _BERRY_PRICES:
            cost = _BERRY_PRICES[name]

        # English display name
        display_name = next(
            (e["name"] for e in data.get("names", []) if e["language"]["name"] == "en"),
            name.replace("-", " ").title(),
        )

        # Short English description
        description = ""
        for entry in data.get("flavor_text_entries", []):
            if entry["language"]["name"] == "en":
                description = entry["text"].replace("\n", " ").replace("\f", " ")[:80]
                break
        if not description:
            for entry in data.get("effect_entries", []):
                if entry["language"]["name"] == "en":
                    description = entry.get("short_effect", "")[:80]
                    break

        # Download sprite PNG
        sprite_url: Optional[str] = (data.get("sprites") or {}).get("default")
        sprite_saved = False
        if sprite_url:
            sr = requests.get(sprite_url, timeout=10)
            sr.raise_for_status()
            (items_path / f"{name}.png").write_bytes(sr.content)
            sprite_saved = True

        return slug, True, {
            "slug": name,
            "display_name": display_name,
            "category": category,
            "cost": cost,
            "description": description,
            "has_sprite": sprite_saved,
            "effect": _EFFECTS.get(name, {"type": "none"}),
        }
    except Exception as exc:
        return slug, False, str(exc)


def download_items(items_folder: str = "assets/items") -> bool:
    """
    Download sprites + metadata for all featured items; write catalog.json.

    Returns True if at least one item was downloaded.
    """
    items_path = Path(items_folder)
    items_path.mkdir(parents=True, exist_ok=True)

    catalog: list[dict] = []
    print(f"Downloading {len(FEATURED_ITEMS)} items from PokeAPI …")

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(_download_one, slug, cat, items_path): slug
            for slug, cat in FEATURED_ITEMS
        }
        for fut in as_completed(futures):
            slug, ok, result = fut.result()
            if ok:
                catalog.append(result)
                print(f"  ✓ {slug}")
            else:
                print(f"  ✗ {slug}: {result}")

    # Preserve display order
    order = {slug: i for i, (slug, _) in enumerate(FEATURED_ITEMS)}
    catalog.sort(key=lambda x: order.get(x["slug"], 99))

    catalog_path = items_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2))
    print(f"Saved {len(catalog)}-item catalog → {catalog_path}")
    return len(catalog) > 0


def check_items_exist(items_folder: str = "assets/items") -> bool:
    return (Path(items_folder) / "catalog.json").exists()


if __name__ == "__main__":
    download_items()
