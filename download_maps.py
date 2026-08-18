#!/usr/bin/env python3
"""Télécharge en masse les fonds de minimap (StratSketch) pour toutes les maps
WoT, les réduit en webp 1024px (léger, pour le web ET le mod) et écrit un
manifeste id d'arène -> {name, file}.

Usage : python3 download_maps.py
Les fichiers atterrissent dans minimaps/<arena_id>.webp. manifest.json récapitule.
Dépendance : Pillow.
"""
import json
import subprocess
from pathlib import Path

from PIL import Image

CDN = "https://stratsketch.com/img/games/wot/maps/{}.webp?v=16"
OUT = Path(__file__).parent / "minimaps"
OUT.mkdir(exist_ok=True)
SIZE = 1024  # côté du webp final (léger, suffisant pour l'éditeur ET le mod)

# (arena_id, nom lisible) - extrait de __NEXT_DATA__ de StratSketch.
MAPS = [
    ("01_karelia", "Karelia"), ("02_malinovka", "Malinovka"),
    ("03_campania_big", "Province"), ("04_himmelsdorf", "Himmelsdorf"),
    ("05_prohorovka", "Prokhorovka"), ("06_ensk", "Ensk"),
    ("06_ensk_big", "Ensk Region"), ("07_lakeville", "Lakeville"),
    ("08_ruinberg", "Ruinberg"), ("10_hills", "Mines"),
    ("11_murovanka", "Murovanka"), ("13_erlenberg", "Erlenberg"),
    ("14_siegfried_line", "Siegfried Line"), ("17_munchen", "Widepark"),
    ("18_cliff", "Cliff"), ("19_monastery", "Abbey"),
    ("23_westfeld", "Westfield"), ("28_desert", "Sand River"),
    ("29_el_hallouf", "El Halluf"), ("31_airfield", "Airfield"),
    ("33_fjord", "Fjords"), ("34_redshire", "Redshire"),
    ("35_steppes", "Steppes"), ("36_fishing_bay", "Fisherman's Bay"),
    ("37_caucasus", "Mountain Pass"), ("38_mannerheim_line", "Mannerheim Line"),
    ("44_north_america", "Live Oaks"), ("45_north_america", "Highway"),
    ("47_canada_a", "Serene Coast"), ("59_asia_great_wall", "Empire's Border"),
    ("60_asia_miao", "Pearl River"), ("63_tundra", "Tundra"),
    ("83_kharkiv", "Kharkov"), ("90_minsk", "Minsk"),
    ("99_poland", "Studzianki"), ("101_dday", "Overlord"),
    ("105_germany", "Berlin"), ("112_eiffel_tower_ctf", "Paris"),
    ("114_czech", "Pilsen"), ("115_sweden", "Glacier"),
    ("122_frozen_land", "Frozen Land"), ("123_dalny_gg", "Dalny"),
    ("128_last_frontier_v", "Outpost"), ("212_epic_random_valley", "Nebelburg"),
    ("217_er_alaska", "Klondike"), ("95_lost_city_ctf", "Ghost Town"),
    ("222_er_clime", "Hinterland"), ("127_japort", "Safe Haven"),
    ("121_lost_paradise_v", "Oyster Bay"), ("120_graf_zeppelin", "Nordskar"),
]


def main():
    manifest, ok, fail = {}, 0, 0
    for arena, name in MAPS:
        src = OUT / f"{arena}.src.webp"
        out = OUT / f"{arena}.webp"
        try:
            subprocess.run(
                ["curl", "-sSLf", "-A", "Mozilla/5.0", "-o", str(src),
                 CDN.format(arena)],
                check=True,
            )
            Image.open(src).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)\
                 .save(out, "WEBP", quality=82, method=6)
            src.unlink(missing_ok=True)
            size = out.stat().st_size
            manifest[arena] = {"name": name, "file": out.name}
            print(f"  ✓ {arena:<24} {name:<18} {size // 1024} Ko")
            ok += 1
        except (subprocess.CalledProcessError, OSError) as exc:
            print(f"  ✗ {arena:<24} {name:<18} ÉCHEC ({exc})")
            src.unlink(missing_ok=True)
            fail += 1
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{ok} maps OK, {fail} échec(s). Manifeste -> minimaps/manifest.json")


if __name__ == "__main__":
    main()
