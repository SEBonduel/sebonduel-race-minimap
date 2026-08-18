# -*- coding: utf-8 -*-
"""SEBonduel Race Minimap - variante DYNAMIQUE (case à cocher + entraînement only).

Comportement voulu :
  - une case « Activer les maps de course » dans les Paramètres (via ModsSettingsAPI) ;
  - si cochée ET bataille = salle d'entraînement -> la minimap de la map affiche le
    circuit, lu automatiquement depuis un dossier EN CLAIR et éditable
    (res_mods/.../screen_race/<arena>.png) : remplacer un PNG met à jour le circuit
    sans recompiler, et une map sans fichier garde sa minimap normale ;
  - sinon -> minimap normale. Les batailles aléatoires ne sont jamais touchées.

⚠️ STATUT : SQUELETTE. Deux morceaux marqués « [À FINALISER SUR CLIENT] » doivent
être branchés/testés sur le vrai client (noms d'API version-dépendants). Le reste
(structure, détection du type de bataille, logs) est stable.

Emplacement dans le .wotmod : res/scripts/client/gui/mods/mod_sebonduel_race.py
"""
import logging

_log = logging.getLogger("sebonduel.race")
_log.setLevel(logging.INFO)

# Dossier des textures « circuit », EN CLAIR et éditable, dans res_mods (2e chemin,
# à côté des minimaps normales). L'installeur y dépose tes tracés ; remplacer un PNG
# ici met à jour le circuit sans rien recompiler. Aucun manifeste : on découvre les
# circuits en testant la présence du fichier de l'arène jouée.
#   res_mods/<version>/gui/maps/icons/map/screen_race/<arena>.png
RACE_TEX_PATH = "gui/maps/icons/map/screen_race"

# État piloté par la case ModsSettingsAPI (persisté par l'API).
_state = {"enabled": True}


# --- Réglages in-game (ModsSettingsAPI) -------------------------------------
# Modèle du bloc de réglages ajouté aux Paramètres généraux.
SETTINGS_TEMPLATE = {
    "modDisplayName": "SEBonduel Race Minimap",
    "enabled": True,
    "column1": [
        {
            "type": "CheckBox",
            "text": "Activer les maps de course",
            "value": True,
            "varName": "enabled",
            "tooltip": "Affiche le circuit SEBonduel sur la minimap, uniquement en "
                       "salle d'entraînement. Décoché = minimap normale.",
        }
    ],
    "column2": [],
}


def _on_settings_changed(_link, values):
    """Callback ModsSettingsAPI quand l'utilisateur (dé)coche la case."""
    _state["enabled"] = bool(values.get("enabled", True))
    _log.info("[SEBonduel-Race] enabled = %s", _state["enabled"])


def _register_settings():
    # [À FINALISER SUR CLIENT] - l'import et l'API exacte dépendent de la version
    # de ModsSettingsAPI installée. Schéma courant ci-dessous ; à valider en jeu.
    try:
        from gui.modsSettingsApi import g_modsSettingsApi  # noqa: import var selon version
    except Exception as exc:  # noqa: BLE001
        _log.warning("[SEBonduel-Race] ModsSettingsAPI absent (%s) - case indisponible, "
                     "on retombe sur enabled=True par défaut.", exc)
        return
    try:
        saved = g_modsSettingsApi.setModTemplate(
            "sebonduel_race", SETTINGS_TEMPLATE, _on_settings_changed)
        if saved:
            _state["enabled"] = bool(saved.get("enabled", True))
        _log.info("[SEBonduel-Race] réglages enregistrés (enabled=%s).", _state["enabled"])
    except Exception as exc:  # noqa: BLE001
        _log.error("[SEBonduel-Race] échec enregistrement réglages : %s", exc)


# --- Logique d'activation ----------------------------------------------------
def _is_training_arena(arena):
    """True si la bataille est une salle d'entraînement."""
    try:
        from constants import ARENA_BONUS_TYPE
        return arena is not None and arena.bonusType == ARENA_BONUS_TYPE.TRAINING
    except Exception as exc:  # noqa: BLE001
        _log.warning("[SEBonduel-Race] bonusType illisible (%s).", exc)
        return False


def race_active(arena):
    """La minimap-circuit doit-elle s'appliquer maintenant ?"""
    return _state["enabled"] and _is_training_arena(arena)


def race_texture_for(arena_name):
    """Chemin de la texture circuit si un fichier existe pour cette arène, sinon None.

    Auto-découverte : on teste la présence du PNG dans le dossier éditable. Ajouter
    ou modifier un fichier suffit - aucun manifeste, aucune recompilation.
    """
    path = "%s/%s.png" % (RACE_TEX_PATH, arena_name)
    try:
        import ResMgr  # API ressources du client
        # [À CONFIRMER SUR CLIENT] - test de présence d'une ressource. ResMgr.isFile
        # existe sur la plupart des versions ; sinon, tester openSection() != None.
        if ResMgr.isFile(path):
            return path
    except Exception as exc:  # noqa: BLE001
        _log.warning("[SEBonduel-Race] test de présence '%s' échoué (%s).", path, exc)
    return None


# --- Branchement minimap -----------------------------------------------------
def _install_minimap_hook():
    """[À FINALISER SUR CLIENT] - cœur du mod : rediriger la texture de minimap.

    Approche visée : envelopper la méthode du composant minimap qui fixe l'image
    de fond, et - si race_active(arena) et qu'un circuit existe pour l'arène -
    substituer race_texture_for(name) au chemin d'origine ; sinon appeler
    l'original inchangé.

    Le nom exact de la classe/méthode (Scaleform vs nouveau GUI) dépend de la
    version : à repérer et tester sur le client. On log abondamment pour ça.
    """
    try:
        from gui.Scaleform.daapi.view.battle.shared.minimap.common import (
            SimplePlugin,  # noqa: nom à confirmer
        )
        _ = SimplePlugin
        _log.info("[SEBonduel-Race] point de hook minimap trouvé (à câbler).")
        # TODO(client): monkey-patch coopératif ici (garder l'original, appeler-le).
    except Exception as exc:  # noqa: BLE001
        _log.error("[SEBonduel-Race] hook minimap non câblé (%s) - à faire en jeu.", exc)


# --- Point d'entrée (exécuté au chargement du client) ------------------------
def init():
    _log.info("[SEBonduel-Race] chargement du mod (squelette v0.1).")
    _register_settings()
    _install_minimap_hook()


init()
