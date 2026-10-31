# ON AIR 02 — V3.7.0 — CARAC prioritaire et TriCaster automatique

## Roles fixes

1. CARAC : Direct / Alerte en manuel, prioritaire.
2. REC seul : commande uniquement par le TriCaster.
3. STREAM seul : commande uniquement par le TriCaster.
4. REC + STREAM : commande uniquement par le TriCaster.

Les noms, couleurs, intensites, logos et animations enregistres sont conserves.
Les menus d'affectation sont retires ; la migration remet les anciens reglages sur les profils 2/3/4 sans modifier leur contenu.

## Console

CARAC seul possede des boutons Direct et Alerte.
Les trois cartes automatiques affichent leur etat et un lien de personnalisation, sans commande manuelle.
CARAC uniquement : usage manuel.
CARAC + TriCaster : suivi automatique, CARAC restant prioritaire.

Un Direct ou une Alerte CARAC prend la main. Le suivi REC/STREAM continue en arriere-plan.
Rendre la main au TriCaster reprend l'etat actuel ; un deuxieme appui Direct CARAC fait de meme lorsque le suivi est actif.
OFF eteint tout et suspend l'automatique. Reprendre le suivi le reactive.
Les deux etats arretes = extinction ; etats inconnus ou lien perdu = orange, sauf si CARAC detient la priorite.
Le boitier ne commande pas l'enregistrement ni la diffusion du TriCaster.

## Reglages

CARAC conserve Direct, Hors direct et Alerte.
Les profils automatiques montrent couleur et animation ; les anciens champs inutiles restent conserves pour compatibilite, sans etre exposes.
L'editeur et sa simulation restent disponibles. Aucun apercu physique ne permet de declencher un profil automatique.
Connexion TriCaster : adresse a renseigner, port 5951 en options avancees.
Le Wi-Fi se configure dans Connexion reseau. Aucun SSID ou mot de passe prive n'est publie.

## Preservation

Structures EEPROM et sauvegardes historiques V1/V2 inchangees, fichiers de logos et d'animations conserves.
Garder le decoupage flash actuel et Only Sketch lors d'un televersement USB. Aucune remise a zero necessaire.
Le fichier /tricaster.cfg migre vers les roles fixes ; adresse, port et activation sont conserves.
Le backup general historique n'inclut pas ce fichier ni les images/sequences de bibliotheque : conserver les exports avant une remise a zero.
Le firmware Damien original et ses releases restent intacts.

## Verifications

Tests des vrais gestionnaires HTTP : refus des commandes manuelles sur REC/STREAM, priorite CARAC et OFF.
Tests du controleur et du parseur reels : quatre combinaisons, etats incomplets, perte de lien et reprise apres CARAC.
Tests des vrais acces aux reglages : migrations des anciennes affectations, checksum et sauvegarde atomique.
Test du JavaScript reel et du rendu HTML par les fonctions C++ reelles.
Tests existants moteur LED, EEPROM, OTA et memoire ; compilation NodeMCU ESP-12E.
36 WS2812E sur D5/GPIO14 ; core ESP8266 3.1.2 ; NeoPixel 1.15.5.
Validation finale de l'ergonomie et du suivi sur le vrai TriCaster a faire par l'utilisateur.
