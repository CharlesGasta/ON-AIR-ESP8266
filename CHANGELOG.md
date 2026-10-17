# Changelog

## V3.0.4

- dérivée de la V3.0.3, plafond global de luminosité porté de 50 à 100 % pour les 36 WS2812E
- aucune modification des fonctions, valeurs par défaut ou paramètres sauvegardés (EEPROM / LittleFS)
- alimentation LED directe 5 V, GND commun ; précautions de mesure et limite 2 A détaillées dans le README

## V3.0.3

- nouveau plafond logiciel global de luminosite **50 %** pour les 36 WS2812E
- suite a la mesure utilisateur **318 mA sur le ruban a 25 % blanc**
- estimation de mesure a 50 % blanc : environ 0,64 A pour le ruban seul (a verifier)
- conserve portail captif, Wi-Fi, OTA, toutes les macros et les animations
- prudence : le courant admissible de VV reste a qualifier; couper l'alimentation si baisse de tension ou surchauffe


## V3.0.2

- limite logicielle globale fixe de luminosite **25 %** au point central `pixelColorLevel()`
- concerne les 36 WS2812E, le DIRECT, HORS DIRECT, les alertes, les apercus et les effets de logo
- corrige le risque du mode flash/fade : celui-ci peut produire 100 % meme si la macro est reglee plus bas
- estimations en blanc plein : environ **0,64 A nominal / 0,86 A pessimiste** carte comprise (reserve ESP de 300 mA)
- 25 % est une valeur provisoire sous reserve d'une source USB et d'un chemin VV adaptes ; aucune homologation de la carte


## V3.0.1

- nombre reel de LED du logo confirme : 36 LED WS2812E (au lieu des 30 supposees)
- driver NeoPixel configure pour 36 pixels (LED 0 a 35)
- animations conservees : chenillard et dessin progressif sur toute la chaine
- retrait des repartitions fixes 12/3/12/3, non confirmees sur le montage
- courant maximal theorique du ruban : 36 x 60 mA = 2,16 A au blanc 100 % ; verifier le passage de courant si alimentation par VV
- connexion DATA : D5 / GPIO14 via resistance 330 ohms


## V3.0.0

- passage du RGB analogique à un ruban adressable WS2812E 5 V
- ESP8266 conservé, DATA sur D5 / GPIO14
- géométrie du logo Damien : 500 mm = 200 + 50 + 200 + 50 mm
- 30 LED à 60 LED/m : 12 haut + 3 droite + 12 bas + 3 gauche
- suppression logicielle des trois sorties PWM RGB et des trois MOSFETs
- ajout de la bibliothèque Adafruit NeoPixel dans les builds GitHub
- conservation des couleurs, intensités, DIRECT / HORS DIRECT, Wi-Fi, portail captif et OTA
- ajout animation ALERTE "Logo : point lumineux tournant"
- ajout animation ALERTE "Logo : dessin progressif du contour"
- documentation matérielle dans `HARDWARE_ADDRESSABLE.md`


## V2.13.0

- portail captif iOS : vrai HTML 200 non vide aux sondes Apple au lieu du redirect 302 vide
- fenêtre captive dirigée automatiquement vers `/settings` (lien de secours présent)
- connexion initiale Wi-Fi externe sans scan synchrone, pour servir les requêtes iPhone dès l'association
- sondes Android / Windows conservées avec redirection HTML non vide
- nouveau diagnostic `/api/captiveStatus` et logs `[CAPTIVE IOS]`
- résolution DNS wildcard de l'AP conservée
- l'ouverture automatique reste décidée par iOS ; accès manuel `http://192.168.4.1/settings`


## V2.12.0

- portail captif Wi-Fi comme sur le projet CBR900RR
- DNS wildcard via DNSServer vers 192.168.4.1
- détection iPhone / iPad : ouverture automatique de la fenêtre de connexion au réseau
- prise en charge des sondes captive portal Apple, Android et Windows
- toute URL inconnue renvoie vers l'interface ON AIR
- accès manuel 192.168.4.1 toujours disponible


## V2.11.0

- indicateur RGB des étapes de démarrage
- bleu : point d'accès / serveur local
- orange : recherche et connexion au Wi-Fi externe
- violet : initialisation mDNS / adresse .local
- vert : prêt, puis extinction automatique
- rouge : erreur de démarrage du point d'accès
- indicateur non bloquant : il ne ralentit pas la connexion réseau
- toute commande DIRECT / ALERTE / OFF prend immédiatement la priorité


## V2.10.0

- animation Fade modifiée en boucle
- séquence : 100 % instantané → fade progressif jusqu'à 0 % → retour instantané à 100 %
- répétition pendant toute la durée d'alerte
- le réglage vitesse / rythme contrôle la durée d'un cycle

## V2.9.0

- stabilisation supplémentaire de l'interface Web
- `/api/status` allégé
- polling adaptatif : rapide pendant ALERTE, plus lent hors ALERTE
- timeout navigateur pour éviter un état visuel bloqué
- fin d'ALERTE principale corrigée : passage propre en DIRECT
- conservation de l'architecture Web en streaming

## V2.8.0

- bouton OFF / NOIR
- test ALERTE terminé automatiquement tout éteint
- fade 100 % → 0 % sur une seule timeline
- gradient vert → jaune → rouge sur une seule timeline
- animations d'alerte configurables

## V2.7.0

- pages Paramètres, Macro et Diagnostic envoyées en streaming
- réduction importante de la pression RAM / heap

## V2.6.0

- export / import de configuration
- mise à jour firmware OTA depuis navigateur
- page diagnostic
- animations d'alerte supplémentaires
