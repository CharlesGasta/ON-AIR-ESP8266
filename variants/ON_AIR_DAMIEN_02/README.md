## Trois scenarios independants

Reglages > Mode TriCaster : choisir separement une emission pour REC seul, STREAM seul et REC + STREAM. Chacune utilise sa couleur et son animation dans l’editeur existant. Les deux arretes : extinction. Etat incomplet ou lien perdu : orange, jamais un faux etat arrete.

# ON AIR Damien 02 — V3.6.1 STUDIO + TriCaster REC / STREAM

Base : V3.5.1-02, validee par Charles sur le deuxieme ESP8266 le 31 octobre 2026.
Conserve 36 WS2812E, D5/GPIO14, macros, editeur de cinematrique, banque et bibliotheque, logos, animations, mode manuel et OTA.

## Activation

1. Installer le .bin par l'interface OTA existante, ou ouvrir le .ino complet et televerser par USB avec Only Sketch et le meme decoupage flash.
2. Reglages > Mode de fonctionnement > TriCaster — suivre REC.
3. Adresse proposee : adresse locale a renseigner. Port : 5951.
4. Choisir trois emissions pour REC seul, STREAM seul et REC + STREAM ; personnaliser leur animation dans les reglages des emissions.
5. Wi-Fi de regie propose : nom du Wi-Fi de regie a renseigner. Renseigner son mot de passe une fois s'il n'est pas deja memorise. Aucun mot de passe prive n'est integre ou publie.
6. Enregistrer. Le boitier se connecte au routeur puis au TriCaster.

REC seul, STREAM seul et les deux : emission correspondante avec son animation. Les deux arretes : extinction complete.
Orange clignotant : connexion ou etat REC indisponible, et non une confirmation de REC arrete.
OFF suspend le suivi ; Reprendre le suivi REC le reactive. Enregistrer un mode ou redemarrer reinitialise aussi cette suspension.
Les commandes DIRECT/ALERTE manuelles restent disponibles en mode Manuel ; elles sont refusees en mode TriCaster pour eviter deux sources de commande contradictoires.
Le mode Manuel reste le defaut a la premiere installation. Le passage en mode TriCaster est volontaire.

## Protocole et provenance

Lecture seule du flux TCP TriCaster sur 5951, abonnement `<register name="NTK_states"/>`, lecture de `shortcut_state name="record_toggle"`.
Ce protocole est implemente dans bitfocus/node-tricaster (teste par ses auteurs sur TC2 Elite et TC Mini 4K).
Le module Companion newtek-tricaster utilise aussi record_toggle pour le retour d'enregistrement.
Sources : https://github.com/bitfocus/node-tricaster/blob/main/index.js et https://github.com/bitfocus/companion-module-newtek-tricaster/blob/master/index.js
Le premier sketch personnel ON AIR TriCaster n'a pas ete retrouve dans les archives accessibles ; cette version ne pretend donc pas etre sa copie exacte.
Cette version lit record_toggle et streaming_toggle et ne commande ni l’enregistrement ni la diffusion.

## Conservation et limites

Parametres EEPROM et fichiers d'animation inchanges. Nouveau fichier /tricaster.cfg avec checksum et remplacement atomique ; absent ou invalide = mode Manuel.
Le backup general historique ne contient pas ce nouveau fichier : noter separement les reglages TriCaster avant une remise a zero.
Les identifiants restent ON_AIR-MOC-02 / onair-moc-02.local. Le mot de passe AP deja enregistre est conserve.
La remise a zero usine supprime aussi les reglages TriCaster.
L'original Damien et ses releases restent intacts. Cette release du boitier 02 est distincte.

## Verification

Tests C++ du parseur et du controleur reels : XML fragmente, gros dictionnaire, etats REC, mode manuel, pause OFF, perte de lien, reprise, demarrage et apercus.
Tests existants moteur LED, EEPROM, OTA et budget memoire ; compilation NodeMCU ESP-12E.
Core ESP8266 3.1.2, NeoPixel 1.15.5 (version utilisee par le firmware Damien original).
Le flux est traite avec un budget de 1024 octets / 2 ms par boucle ; tentative TCP bornee a 80 ms, au plus toutes les 3 secondes.
Un flux sans changement de REC reste valide ; keepalive TCP detecte les pertes silencieuses. Un etat inconnu n'est jamais transforme en REC OFF.
Validation reelle avec le routeur CARAC et le TriCaster a faire par l'utilisateur : compilation et tests simules ne la remplacent pas.

Migration automatique du fichier de reglages V3.6.0 : emission REC conservee, STREAM propose sur emission 2 et REC+STREAM sur emission 3, modifiables. Les etats sont invalides a chaque perte de connexion ; les deux valeurs doivent etre recues avant de choisir un scenario. Tests natifs des quatre combinaisons, transitions, perte de lien et sauvegarde/migration atomique.
