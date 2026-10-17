# ON AIR — ESP8266

Contrôleur **ON AIR RGB autonome** basé sur ESP8266 / NodeMCU 1.0 (ESP-12E), avec interface Web mobile.

## V3.4.0 — Une bibliothèque commune d’animations

Un seul accès **Réglages → Éditeur d’animation**. Donner un nom puis Enregistrer crée une animation disponible par son nom dans les menus Direct et Alerte des quatre émissions. Jusqu’à 16 séquences communes, chacune de 12 étapes. Charger une ligne permet de la modifier ; Nouvelle crée une autre séquence ; la croix rouge supprime la séquence et ses affectations. Les noms vides ou déjà utilisés par une autre séquence sont refusés.

**Aperçu sur le boîtier** est un interrupteur indépendant de l’enregistrement : décoché, le travail reste dans le navigateur ; coché, l’étape choisie, ses couleurs et la lecture locale sont reflétées physiquement. Rien n’est écrit en mémoire permanente par l’aperçu. Il s’arrête à la désactivation ou après 3 s sans renouvellement et ne peut reprendre avec une ancienne session après une commande du boîtier.

Les anciennes séquences Direct/Alerte sont migrées automatiquement avec leurs affectations, sous des noms propres à leur émission d’origine. Le format EEPROM historique reste identique. Les nouveaux noms et couleurs sont enregistrés ensemble de façon atomique ; exporter les fichiers `.onair` pour sauvegarder les séquences séparément du fichier général de configuration.

Détails : [notes v3.4.0](docs/releases/v3.4.0.md).

## V3.3.2 — Menu de l’éditeur épuré

La rubrique Éditeur d’animation présente quatre lignes avec logos et noms d’émission, et deux accès Direct / Alerte compacts et centrés. Teintes distinctes adaptées au clair/sombre et espacement optimisé pour téléphone. Aucun changement des animations ou des réglages sauvegardés.

Détails : [notes v3.3.2](docs/releases/v3.3.2.md).

## V3.3.1 — Accès à l’éditeur, alertes et signaux de mise à jour

**Réglages → Éditeur d’animation** donne accès aux séquences DIRECT et ALERTE indépendantes de chaque émission. Le lien auparavant masqué dans les réglages d’émission est corrigé. Choisir Animation personnalisée dans le menu DIRECT ou ALERTE correspondant après avoir enregistré la séquence.

L’arc-en-ciel du démarrage à froid ne commence qu’après l’initialisation réseau. La mise à jour OTA affiche du jaune pendant l’écriture, deux signaux verts après validation et du rouge en cas d’erreur. Ces signaux seront actifs pour les mises à jour effectuées après installation de cette version.

Détails : [notes v3.3.1](docs/releases/v3.3.1.md). Séquences .onair à exporter séparément pour le DIRECT et l’ALERTE.

## V3.3.0 — Balayages et éditeur d’animation

Les balayages horizontaux utilisent uniquement le haut et le bas ; les nouveaux balayages verticaux utilisent uniquement les côtés. L’arc-en-ciel et le démarrage approuvés sont inchangés.

Dans les réglages d’une émission, **Créer une animation personnalisée** ouvre les 36 LED : sélection individuelle ou par surface, couleurs, 12 étapes avec maintien et transition directe ou fondue, aperçu, test de 15 secondes et import/export `.onair`. Après enregistrement, sélectionner **Animation personnalisée** dans Animation en direct. Les fichiers de séquences sont conservés lors des OTA et sauvegardés séparément du fichier de configuration général.

Détails : [notes v3.3.0](docs/releases/v3.3.0.md).

## V3.2.0 — Thèmes et animations spatiales

Choix clair/sombre, animations DIRECT par émission, balayages adaptés au placement 12/5/14/5 des LED, respiration, comète et arc-en-ciel. Nouvelle cinématique de démarrage puis indications de connexion Wi-Fi et de mode autonome. Le téléphone conserve l'interface épurée ; les réglages historiques sont préservés.

Installation, choix des animations et signification des signaux : [notes de version](docs/releases/v3.2.0.md).

## Fonctions

- 4 macros configurables
- couleur et intensité DIRECT par macro
- couleur / extinction HORS DIRECT
- bouton DIRECT
- bouton ALERTE
- bouton OFF / NOIR immédiat
- animations d'alerte :
  - clignotement classique
  - fade 100 % → 0 %
  - gradient vert → jaune → rouge
  - clignotement accéléré
  - double flash / heartbeat
- durée d'alerte programmable
- Wi-Fi autonome + Wi-Fi externe optionnel
- mémorisation de plusieurs réseaux
- scan Wi-Fi
- mDNS
- export / import de configuration
- diagnostic système
- mise à jour OTA depuis l'interface Web

## Luminosité 100 % — V3.0.4

Version dérivée de la V3.0.3 : plafond global porté de 50 à 100 % pour les 36 WS2812E, y compris les alertes et animations. Les réglages sauvegardés, leur format et toutes les autres fonctions restent inchangés. Une intensité déjà sauvegardée au-dessus de 50 % devient donc réellement plus lumineuse après la mise à jour OTA.

Alimenter les LED directement en 5 V avec GND commun à l'ESP, sans faire passer leur courant par la carte. Une alimentation 5 V / 2 A n'offre pas de marge garantie au blanc 100 % : l'hypothèse prudente de 60 mA par pixel représente 2,16 A pour les LED seules, plus l'ESP. La mesure précédente de 318 mA à 25 % suggère environ 1,27 A pour le ruban à 100 %, mais cette extrapolation doit être vérifiée.

Pour mesurer : commencer à faible intensité, monter progressivement, surveiller courant et tension au ruban. Brancher l'ampèremètre en série sur le calibre courant continu adapté (entrée et fusible vérifiés), jamais directement entre +5 V et GND. Couper avant de changer le câblage. Arrêter si la tension chute, si le montage redémarre ou chauffe. Ne pas relier les sorties +5 V de deux alimentations distinctes ; garder les masses communes. Les animations peuvent atteindre 100 % même avec un curseur de macro plus bas.

## Ruban adressable WS2812E

La V3.0.3 pilote les 36 LED WS2812E 5 V confirmees sur le logo Damien.

Contour vise : **200 + 50 + 200 + 50 mm = 500 mm**. Répartition confirmée vue de face : **12 en bas, 5 à gauche, 14 en haut, 5 à droite**, départ bas droit, parcours vers la gauche.

Le pilotage utilise uniquement **D5 / GPIO14** via un buffer logique **74AHCT125**. Les trois MOSFETs RGB analogiques de l'ancienne version ne sont plus utilisés.

Deux animations spatiales ont été ajoutées aux alertes : **point lumineux tournant** et **dessin progressif du contour**.

Voir `HARDWARE_ADDRESSABLE.md` pour le câblage complet.

## Matériel

Firmware compilé pour :

`esp8266:esp8266:nodemcuv2`

Arduino IDE : **NodeMCU 1.0 (ESP-12E Module)**

### Sorties RGB

| Couleur | ESP8266 | GPIO |
|---|---|---:|
| Rouge | D2 | 4 |
| Vert | D1 | 5 |
| Bleu | D5 | 14 |

Chaque canal pilote un MOSFET N logique :
- Gate via 330 Ω
- pulldown Gate 10 kΩ vers GND
- Source vers GND commun
- Drain vers canal R/G/B du ruban
- ruban RGB à anode commune +5 V

## Indicateur de démarrage

Quand l'indicateur de démarrage est activé :

- 🔵 **bleu** : point d'accès / serveur local en cours de démarrage
- 🟠 **orange** : recherche / connexion au Wi-Fi externe
- 🟣 **violet** : initialisation mDNS (`.local`)
- 🟢 **vert** : système prêt ; trois clignotements puis extinction
- 🔴 **rouge** : erreur du point d'accès

L'indicateur est non bloquant et une commande DIRECT / ALERTE / OFF reste prioritaire.

## Portail captif iPhone

Quand un iPhone rejoint directement le Wi-Fi du boîtier, le DNS wildcard tente de déclencher l'assistant captif Apple. Le boîtier renvoie à `hotspot-detect.html` une petite page HTML avec ouverture automatique de `http://192.168.4.1/settings`.

La décision d'afficher une fenêtre automatique appartient à iOS : elle peut ne pas apparaître si le réseau est déjà mémorisé, si l'accès privé/VPN perturbe les sondes ou selon la version d'iOS.

**En cas d'absence de fenêtre :** Paramètres iPhone → Wi-Fi → (i) → Oublier ce réseau, puis reconnecter. L'accès manuel à `http://192.168.4.1/settings` reste permanent.

Diagnostic depuis le réseau ESP : `http://192.168.4.1/api/captiveStatus` donne les nombres de sondes iOS/autres et le nombre de clients AP. Le moniteur série affiche `[CAPTIVE IOS]` à chaque sonde Apple reçue.

## Firmware

Source principale :

`ON_AIR_ESP8266.ino`

GitHub Actions compile automatiquement le firmware et publie :

- `ON_AIR_ESP8266_OTA.bin` — mise à jour OTA
- le `.bin` versionné
- le `.ino` versionné
- un ZIP complet

## Mise à jour OTA

Dans l'interface du boîtier :

**Paramètres → MISE À JOUR FIRMWARE OTA**

Envoyer le fichier :

`ON_AIR_ESP8266_OTA.bin`

## Version actuelle

**V3.0.3 — ADDRESSABLE LOGO 36LED**

## Auteur

Charles Gastault
