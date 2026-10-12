# ON AIR — ESP8266

Contrôleur **ON AIR RGB autonome** basé sur ESP8266 / NodeMCU 1.0 (ESP-12E), avec interface Web mobile.

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

## Limite lumineuse 50 %

La V3.0.3 applique un **plafond global fixe de 50 %** a l'intensite de sortie des 36 pixels WS2812E, y compris les alertes, les couleurs de demarrage, les tests et les animations spatiales.

Les curseurs peuvent encore afficher des valeurs jusqu'a 100 %, mais toute valeur au-dela de 50 % a le meme rendu que 50 % jusqu'a une nouvelle version du firmware. Les couleurs restent conservees.

Ce plafond vise un courant estime entre **0,94 A et 1,40 A** (ESP compris, hypothese carte 300 mA) pour 36 LED en blanc, selon les hypotheses electriques nominale/pessimiste. Ce n'est pas une validation de la capacite de la broche VV ni une protection contre les courts-circuits. Verifier le modele de carte et la source USB reellement utilises.

## Ruban adressable WS2812E

La V3.0.3 pilote les 36 LED WS2812E 5 V confirmees sur le logo Damien.

Contour vise : **200 + 50 + 200 + 50 mm = 500 mm**. La repartition exacte des **36 LED** entre les 4 cotes reste a verifier : ne pas supposer 12/3/12/3.

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
