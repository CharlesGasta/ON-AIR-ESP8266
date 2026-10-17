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

## Luminosité 100 % — V3.0.4

Version dérivée de la V3.0.3 : plafond global porté de 50 à 100 % pour les 36 WS2812E, y compris les alertes et animations. Les réglages sauvegardés, leur format et toutes les autres fonctions restent inchangés. Une intensité déjà sauvegardée au-dessus de 50 % devient donc réellement plus lumineuse après la mise à jour OTA.

Alimenter les LED directement en 5 V avec GND commun à l'ESP, sans faire passer leur courant par la carte. Une alimentation 5 V / 2 A n'offre pas de marge garantie au blanc 100 % : l'hypothèse prudente de 60 mA par pixel représente 2,16 A pour les LED seules, plus l'ESP. La mesure précédente de 318 mA à 25 % suggère environ 1,27 A pour le ruban à 100 %, mais cette extrapolation doit être vérifiée.

Pour mesurer : commencer à faible intensité, monter progressivement, surveiller courant et tension au ruban. Brancher l'ampèremètre en série sur le calibre courant continu adapté (entrée et fusible vérifiés), jamais directement entre +5 V et GND. Couper avant de changer le câblage. Arrêter si la tension chute, si le montage redémarre ou chauffe. Ne pas relier les sorties +5 V de deux alimentations distinctes ; garder les masses communes. Les animations peuvent atteindre 100 % même avec un curseur de macro plus bas.

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
