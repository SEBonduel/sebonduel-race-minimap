# SEBonduel - Race Minimap

Des **minimaps personnalisées** pour organiser des **courses de chars** dans World
of Tanks : on dessine un circuit par-dessus le terrain, et le mod remplace la
texture de minimap de la map par « terrain + tracé ».

## Chaîne de fabrication

```
track-editor.html   →   tracks/*.json + *_overlay.png   →   mod/build.py   →   dist/*.wotmod   →   installeur   →   jeu
   (dessine)                  (exporte)                      (fusionne+zip)      (paquet)          (installe)     (teste)
```

1. **Dessiner** - ouvre `track-editor.html` (double-clic, aucun serveur requis).
   Charge un fond depuis `minimaps/`, clique le parcours, règle le style.
   Dans le champ **Map**, mets l'**ID d'arène** (ex. `05_prohorovka`) - voir
   `minimaps/manifest.json`. Exporte le **`.json`** *et* l'**overlay `.png`**.
2. **Déposer** les 2 fichiers dans `tracks/` (voir `tracks/README.txt`).
3. **Empaqueter** : `cd mod && python3 build.py` → génère
   `dist/sebonduel-race-minimap.wotmod` (une image « terrain + tracé » par map trouvée).
4. **Installer** : compile `installer/sebonduel-race-minimap.iss` avec Inno Setup
   (sur Windows) → un `.exe` qui propose **deux modes** (voir ci-dessous).
   *(Ou, sans installeur : copie le `.wotmod` dans `mods/<version>/`, ou
   l'arborescence `dist/res_mods_payload/` dans `res_mods/<version>/`.)*
5. **Tester** en jeu, idéalement en **salle d'entraînement**.

## Deux modes d'installation (compatibilité modpacks)

`build.py` produit **deux artefacts**, et l'installeur laisse choisir :

| Mode | Où | Pour qui |
|---|---|---|
| **Propre** (`.wotmod` → `mods/`) | à part, ne touche rien | défaut ; joueurs **sans** mod de minimap |
| **Écraser** (textures → `res_mods/`) | prime sur tout | joueurs qui ont des **minimaps HD** (Aslain…) et veulent voir le tracé |

Pourquoi : `res_mods/` l'emporte sur les `.wotmod`. Un joueur avec des minimaps
HD (dans `res_mods/`) ne verrait pas le tracé en mode *propre* → le mode *écraser*
place nos textures dans `res_mods/` pour passer devant (réversible, non destructif).

## Prérequis

- **build.py** : Python 3 + Pillow (`python3 -m pip install Pillow`).
- **installeur** : [Inno Setup](https://jrsoftware.org/isdl.php) (Windows uniquement).

## Variante dynamique (case in-game + entraînement uniquement)

En plus du pack statique, une **variante Python** (`mod/src/mod_sebonduel_race.py`) vise :
une case **« Activer les maps de course »** dans les Paramètres (via *ModsSettingsAPI*)
qui active les circuits **seulement en salle d'entraînement** - batailles aléatoires
jamais touchées. Principe : ne pas remplacer la minimap par défaut, mais ranger les
circuits dans un **dossier en clair et éditable**
(`res_mods/<version>/gui/maps/icons/map/screen_race/<arena>.png`) et **rediriger** la
minimap vers eux quand (case cochée) ET (`bonusType == TRAINING`). **Auto-découverte** :
le mod prend le fichier présent pour l'arène jouée - remplacer/ajouter un PNG met à
jour le circuit **sans recompiler**, et une map sans fichier garde sa minimap normale.
Répartition : le **code** dans le `.wotmod` (`mods/`), les **tracés** en clair dans
`res_mods/` (donc éditables à la volée).

**Statut : squelette.** Les parties stables sont écrites (structure, détection du
type de bataille, modèle de réglages, logs). Deux morceaux marqués
`[À FINALISER SUR CLIENT]` doivent être câblés et **testés sur ton client Windows**
(noms d'API version-dépendants) :
1. l'enregistrement ModsSettingsAPI (import/appel exacts) ;
2. le hook qui redirige la texture de minimap.

Trade-off : plus puissant (toggle, training-only, rien à désinstaller) mais **plus
fragile** que le pack statique (du Python à maintenir à chaque grosse MàJ).

## ⚠️ Le point à caler dans tous les cas : le chemin de la texture

Le mod remplace la texture de minimap du jeu. Le **chemin exact** et le **format**
(PNG ou DDS) de cette texture doivent être **confirmés sur ton client** - c'est LE
paramètre incertain. S'ils sont bons, le tracé apparaît ; sinon, rien ne change.

Réglages dans `mod/build.py` (tout en haut) :

```python
MINIMAP_RES_PATH = "gui/maps/icons/map/screen"   # dossier dans res/
MINIMAP_EXT      = "png"                          # "png" ou "dds"
```

Pour trouver la vraie valeur (sur Windows) :
1. Ouvre `World_of_Tanks/res/packages/*.pkg` avec **7-Zip** (ce sont des zips).
2. Cherche un nom d'arène, ex. `05_prohorovka`.
3. Repère l'image **carrée** de minimap : note son **chemin** (sous `gui/...`) et
   son **extension**. Reporte-les dans `build.py` et relance-le.

*(Quand on sera sur le PC Windows, je peux faire cette étape avec toi.)*

## Pourquoi remplacer la texture (et pas injecter du code)

La minimap en bataille est un empilement de couches (terrain → grille → chars…).
Remplacer la **couche terrain** par « terrain + tracé » est :
- **robuste** - aucune API Python fragile, insensible à la plupart des MàJ ;
- **fidèle** à l'intention (« minimaps personnalisées »).

Compatibilité (distribution en clan, ex. race EBR) :
- **Vs le jeu** : aucun risque - ressources seules, pas de code, aucun crash possible.
- **Vs Aslain / autres modpacks** : le `.wotmod` vit dans `mods/`, **séparé** du
  `res_mods/` d'Aslain → il **ne peut pas casser** leur install. Le pire cas est
  purement **cosmétique** (quelle minimap l'emporte), jamais une panne.
- **Joueur en minimap vanilla** : le tracé s'affiche direct.
- **Joueur avec minimaps HD** (textures `res_mods/`) : utiliser le **mode écraser**,
  ou désactiver ses minimaps HD le temps de la course.
- **Joueur avec minimap XVM** : affiche *en principe* la même texture de fond (donc
  le tracé apparaît), **à confirmer au premier test**.

## Fair-play

Overlay **cosmétique côté client**, affichant une donnée que **tu** as créée (pas
d'info de jeu cachée, pas d'automatisation) → catégorie autorisée par Wargaming, du
même type que les mods « dessin sur minimap ». À utiliser de préférence en salle
d'entraînement. *Rien ne remplace la lecture de la politique officielle « Fair Play ».*

## Fonds de minimap

`minimaps/` contient **48 maps WoT en HD 2048×2048** (source StratSketch), nommées
par ID d'arène, + `manifest.json` (ID → nom). Regénérable via `download_maps.py`.
Manquantes : **Dalny** (`123_dalny_gg`) et **Frozen Land** (`122_frozen_land`) -
à extraire des `.pkg` du jeu.

## Structure

```
track-editor.html      éditeur de tracé (navigateur)
download_maps.py       récupère les fonds HD
minimaps/              48 terrains HD + manifest.json
tracks/                tes tracés exportés (json + overlay png)
mod/meta.xml           métadonnées du .wotmod
mod/build.py           fusionne + empaquette le .wotmod
installer/*.iss        installeur Windows (Inno Setup)
dist/                  sortie : le .wotmod (créé par build.py)
```
