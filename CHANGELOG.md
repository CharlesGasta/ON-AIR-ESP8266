# Changelog

## V3.4.3 — Aperçu et accès éditeur

- accès éditeur sobre, sans barre bleue ni phrase descriptive
- aperçu physique sans accumulation de requêtes ni renouvellement avant confirmation
- tolérance aux incidents réseau temporaires, délai de sécurité 15 secondes
- tentatives mDNS espacées après échec et soumises à la mémoire disponible


## V3.4.2 — Mémoire et navigation

- textes HTML transférés en flash, buffers libérés avant transmission des scripts
- contrôle du budget RAM à la compilation et refus HTTP 503 si mémoire insuffisante
- diagnostic mémoire léger /health et journal de démarrage
- suppression de la redirection automatique du portail vers les réglages


## V3.4.1 — Fiabilité OTA

- suppression des animations et callbacks LED pendant la mise à jour
- contrôle de taille, format .bin et MD5 ; réponse avant redémarrage différé
- vérification du nouveau démarrage et du firmware installé après reconnexion
- réponse perdue distincte d’un échec ; aucun renvoi automatique
- tests des handlers réels avec flash simulée et des scénarios navigateur perte de réponse / refus / résultat inconnu

## V3.4.0 — Bibliothèque commune

- éditeur unique et 16 séquences nommées réutilisables en Direct/Alerte dans les quatre émissions
- validation des noms, chargement/modification, création et suppression
- aperçu physique temporaire piloté par interrupteur, distinct de la sauvegarde
- migration des anciennes séquences et affectations ; formats EEPROM et backup V2 conservés
- fichier nom + cues remplacé atomiquement ; aperçu sans écriture flash, bail de 3 s et sessions révoquées après arrêt

## V3.3.2 — Menu de l’éditeur

- lignes compactes avec logos, noms lisibles et accès Direct / Alerte centrés
- teintes sobres clair/sombre et espacement mobile
- aucun changement du moteur LED, des données enregistrées ou de la logique OTA

## V3.3.1 — Accès éditeur, alertes, boot et OTA

- navigation Réglages → Éditeur d’animation et liens d’émission rendus visibles
- séquences personnalisées ALERTE indépendantes des séquences DIRECT existantes
- horloge de démarrage lancée après l’initialisation Wi-Fi pour conserver tout l’arc-en-ciel
- signaux OTA jaune / vert validé / rouge échec, basés sur les callbacks réels du moteur de mise à jour
- tests de sélection visible, séparation des fichiers, début différé, progression OTA et exclusion des faux succès

## V3.3.0 — Balayages et cues

- surfaces isolées pour les balayages horizontaux et verticaux
- éditeur mobile de 36 LED, 12 étapes par émission, maintien et fondu, aperçu et test borné
- fichiers de séquence avec contrôle d’intégrité et remplacement atomique ; import/export indépendant
- structures EEPROM et cinématique de démarrage conservées

## V3.2.0 — Thèmes et animations spatiales

- choix clair/sombre mémorisé dans le navigateur
- cartographie confirmée 12 bas / 5 gauche / 14 haut / 5 droite, départ bas droit
- huit modes en DIRECT avec période par émission ; cinq nouvelles alertes spatiales
- cinématique arc-en-ciel, flash, montée blanche et expansion rouge, puis états Wi-Fi
- démarrage non bloquant et interruptible par les commandes ; échec externe distinct du mode autonome
- extension de réglages LittleFS sans modifier le format EEPROM ; sauvegardes V2 et import V1
- tests C++ du moteur, de la persistance et de la priorité des commandes avant compilation

## V3.1.1 — Interface épurée

- nouveau dessin clair : cartes arrondies, boutons teintés, icônes et police système
- retrait des textes d’accueil, numéros, mentions PRÊT et cadres de logos
- nom du boîtier, connexion, roue crantée et commande OFF uniquement autour des émissions
- réglages harmonisés ; fonctions et paramètres conservés

## V3.1.0 — Studio mobile

- refonte complète de la console mobile, réglages et éditeur des émissions
- état du boîtier confirmé, gestion explicite des déconnexions, OFF / NOIR permanent dans la console
- sauvegardes de réglages séquencées, erreurs visibles et reprise avant navigation
- écran OTA avec progression ; gestionnaire de flash existant conservé
- moteur LED, 36 pixels, 100 %, fonctions et paramètres sauvegardés inchangés
- voir docs/releases/v3.1.0.md pour installation, tests et audit de la limite 25 %

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
