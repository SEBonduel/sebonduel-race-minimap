#!/usr/bin/env python3
"""Assemble le mod « SEBonduel Race Minimap » (deux cibles d'installation).

Pour chaque tracé exporté depuis l'éditeur (tracks/<map>_track.json +
tracks/<map>_overlay_<res>.png), le script :
  1. résout la map -> ID d'arène (via minimaps/manifest.json) ;
  2. fusionne le terrain HD (minimaps/<arena>.png) et le tracé transparent.

Il produit ensuite DEUX artefacts dans dist/ :
  - sebonduel-race-minimap.wotmod        -> installation propre dans mods/ (n'écrase rien)
  - res_mods_payload/<...>/<arena>.png -> installation « écraser » dans res_mods/
                                          (passe devant les minimaps HD)
L'installeur Inno Setup propose les deux cibles.

Dépendance : Pillow  (python3 -m pip install Pillow)
Usage      : python3 build.py
"""
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TRACKS = ROOT / "tracks"
MINIMAPS = ROOT / "minimaps"
DIST = ROOT / "dist"
META = ROOT / "mod" / "meta.xml"

# ⚠️ À CONFIRMER SUR TON CLIENT (via les .pkg) - voir README, section
# « Caler le chemin de la texture ». C'est LE seul paramètre incertain :
# si le tracé n'apparaît pas en jeu, c'est presque sûrement ici que ça se joue.
MINIMAP_RES_PATH = "gui/maps/icons/map/screen"   # dossier dans res/
MINIMAP_EXT = "png"                              # "png" ou "dds"
TARGET_SIZE = 1024                               # côté de la texture finale (px)

WOTMOD_NAME = "sebonduel-race-minimap.wotmod"
PAYLOAD_DIR = "res_mods_payload"                 # arborescence pour res_mods/


def load_manifest():
    path = MINIMAPS / "manifest.json"
    if not path.exists():
        raise SystemExit("manifest.json introuvable - lance d'abord download_maps.py.")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_arena(map_field, manifest):
    """Résout le champ 'map' d'un tracé vers un ID d'arène du manifeste."""
    m = (map_field or "").strip()
    if m in manifest:                       # déjà un ID d'arène
        return m
    norm = lambda s: "".join(c for c in s.lower() if c.isalnum())
    want = norm(m)
    for arena, info in manifest.items():    # sinon, match par nom lisible
        if norm(info["name"]) == want or norm(arena) == want:
            return arena
    return None


def best_overlay(base):
    """Renvoie le PNG d'overlay de plus haute résolution pour un tracé donné."""
    cands = sorted(TRACKS.glob(base + "_overlay_*.png"),
                   key=lambda p: p.stat().st_size)
    return cands[-1] if cands else None


def bake(arena, overlay_path):
    """Fusionne terrain + tracé -> Image à TARGET_SIZE, prête à écrire."""
    terrain_path = MINIMAPS / f"{arena}.webp"
    if not terrain_path.exists():
        raise FileNotFoundError(f"terrain manquant : {terrain_path.name}")
    terrain = Image.open(terrain_path).convert("RGBA").resize(
        (TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
    overlay = Image.open(overlay_path).convert("RGBA").resize(
        (TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
    merged = Image.alpha_composite(terrain, overlay)
    return merged if MINIMAP_EXT == "dds" else merged.convert("RGB")


def main():
    manifest = load_manifest()
    tracks = sorted(TRACKS.glob("*_track.json"))
    if not tracks:
        raise SystemExit(
            "Aucun tracé dans tracks/. Exporte un circuit depuis l'éditeur "
            "(« Exporter le tracé (.json) » + « Exporter l'overlay (.png) »).")

    # dist/ propre à chaque build
    if DIST.exists():
        shutil.rmtree(DIST)
    tex_dir = DIST / PAYLOAD_DIR / MINIMAP_RES_PATH   # arborescence res_mods/
    tex_dir.mkdir(parents=True)

    done = []
    for tj in tracks:
        base = tj.name[:-len("_track.json")]
        data = json.loads(tj.read_text(encoding="utf-8"))
        arena = resolve_arena(data.get("map"), manifest)
        if not arena:
            print(f"  ✗ {tj.name} : map « {data.get('map')} » non résolue "
                  "(mets l'ID d'arène du manifeste dans le champ Map). Ignoré.")
            continue
        overlay = best_overlay(base)
        if not overlay:
            print(f"  ✗ {tj.name} : pas d'overlay PNG (exporte-le depuis l'éditeur). Ignoré.")
            continue
        out = tex_dir / f"{arena}.{MINIMAP_EXT}"
        bake(arena, overlay).save(out)
        done.append(arena)
        print(f"  ✓ {manifest[arena]['name']:<18} -> {MINIMAP_RES_PATH}/{arena}.{MINIMAP_EXT}")

    if not done:
        raise SystemExit("Rien à empaqueter (aucun tracé valide).")

    # .wotmod = meta.xml + les mêmes textures, préfixées « res/ ».
    # IMPORTANT : ZIP_STORED, WoT n'accepte pas la compression dans un .wotmod.
    wotmod = DIST / WOTMOD_NAME
    with zipfile.ZipFile(wotmod, "w", zipfile.ZIP_STORED) as z:
        z.write(META, "meta.xml")
        for tex in sorted(tex_dir.glob(f"*.{MINIMAP_EXT}")):
            z.write(tex, f"res/{MINIMAP_RES_PATH}/{tex.name}")

    print(f"\n{len(done)} map(s) empaquetée(s).")
    print(f"  • mods/     : dist/{WOTMOD_NAME}")
    print(f"  • res_mods/ : dist/{PAYLOAD_DIR}/  (arborescence à copier)")
    print("L'installeur propose les deux cibles.")


if __name__ == "__main__":
    main()
