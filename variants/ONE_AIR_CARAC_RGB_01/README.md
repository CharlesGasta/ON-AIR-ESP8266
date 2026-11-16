# ON AIR CARAC RGB 01 — 2.1.0

Variante dediee au premier boitier TriCaster RGB analogique, derivee de la 2.0.1 CARAC.
Ne pas utiliser sur le ON AIR 02 adressable ou le boitier Damien.

## Materiel
NodeMCU ESP8266, flash 4 Mo, MOSFETs N actifs hauts : D2/GPIO4 rouge, D1/GPIO5 vert, D5/GPIO14 bleu. PWM 1 kHz, plage 0..1023. Aucun protocole NeoPixel et aucune dependance Adafruit.
Toutes les LED recoivent la meme couleur. Les cellules logiques des sequences sont moyennees en RGB : les fades, flashs et variations de couleur fonctionnent ; les deplacements spatiaux deviennent des variations globales, sans mouvement physique sur le ruban. L'interface rappelle cette limite.

## Fonctions
AP autonome ON_AIR-MOC-01 / 192.168.4.1, nom mDNS onair-moc-01.local, Wi-Fi externe memorise, DHCP ou IP fixe par reseau, reconnexion applicative directe toutes les 30 s, interface Web, macros CARAC manuelles prioritaires, profils automatiques REC / STREAM / REC+STREAM, bibliotheque et OTA.
Mot de passe AP initial public : 12345678, modifiable dans les reglages.

## Migration du premier boitier
Le layout EEPROM 340 octets portant la signature 0xca0a1a10, observe dans la sauvegarde du boitier et recoupe avec son interface Web, est reconnu. Le firmware lit les identifiants depuis la flash, conserve le mode IP, l'IP, le masque, la passerelle, le DNS, l'IP TriCaster et les couleurs ON/OFF. Aucun identifiant prive n'est present dans les sources publiques.
La migration reconnait uniquement un TriCaster designe par IPv4 et sans authentification historique. Un layout invalide ou une authentification non vide provoque un arret avant ecriture EEPROM. La configuration ancienne n'est remplacee qu'apres sauvegarde reussie des profils reseau et TriCaster. Les nouveaux profils automatiques reprennent les couleurs REC ON/OFF existantes ; les autres fonctions utilisent leurs nouveaux reglages par defaut.
La source historique exacte 1.0.0 STATIC IP FIX n'est pas dans l'historique Git disponible. Ne pas generaliser ce layout a d'autres boitiers sans verifier leur sauvegarde.

Avant installation : sauvegarder integralement les 4 Mo par USB et conserver ce fichier prive. Le binaire ecrit uniquement la zone sketch. Sur le boitier 01 observe, la zone FS 0x200000..0x3fa000 etait vierge ; LittleFS peut l'initialiser pour ses nouveaux fichiers. EEPROM a 0x3fb000. Aucune image de filesystem n'est fournie ni envoyee. Ne pas utiliser erase_flash.
FQBN : esp8266:esp8266:nodemcuv2:eesz=4M2M ; core 3.1.2. Conserver Only Sketch.

## Validation
CI : compilation reelle ESP8266, budget RAM, tests C++ des sorties RGB et de la migration (DHCP/fixe, couleurs, conservation des identifiants, layout invalide et echec stockage), tests existants Wi-Fi, reseau, TriCaster et priorite manuelle. Les deux autres sources de boitiers restent inchangees.
La CI ne remplace pas le controle sur materiel des couleurs et des etats REC/STREAM. Les sauvegardes privees, mots de passe et pages de configuration ne doivent pas etre publies.
