Dépose ici les tracés exportés depuis l'éditeur (track-editor.html).

Pour chaque circuit, tu obtiens 2 fichiers via les boutons d'export :
  - <map>_track.json          (les points du parcours, pour rééditer)
  - <map>_overlay_<res>.png   (le tracé transparent, utilisé par build.py)

IMPORTANT - nom de la map :
Dans l'éditeur, mets dans le champ « Map » l'ID d'arène interne
(ex. 05_prohorovka, 19_monastery). La liste complète ID -> nom est dans
  ../minimaps/manifest.json
C'est ce qui permet à build.py de fusionner le bon terrain avec ton tracé.
(Un nom lisible « Prohorovka » marche aussi en secours, mais l'ID est plus sûr.)

Ensuite, depuis le dossier mod/ :
  python3 build.py
=> génère ../dist/sebonduel-race-minimap.wotmod avec toutes les maps trouvées ici.
