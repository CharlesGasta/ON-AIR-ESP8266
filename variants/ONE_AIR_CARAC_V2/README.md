# One air Carac v2 — 2.0.0

Projet derive du firmware ON AIR 02 V3.7.0 valide pour CARAC manuel prioritaire et TriCaster automatique.
Les versions Damien et ON AIR 02 existantes restent intactes.

## Nouveautes

- Boutons de mode lisibles en themes clair et sombre, avec couleurs de texte/fond explicites et contraste teste.
- Nouveau nom One air Carac v2 et panneau de mode simplifie.
- Menu Reseau : etat de connexion, SSID, IPv4, masque, passerelle, DNS, MAC, RSSI, mDNS et IP du point d'acces autonome.
- Profil DHCP ou IP fixe independant pour chaque Wi-Fi memorise. Pas d'adresse privee ni de mot de passe inclus dans le source.
- Verification du masque, des adresses de reseau/broadcast, de la passerelle, des DNS et du chevauchement avec le point d'acces autonome.
- Application differee apres la reponse du navigateur, sans reset usine. DHCP est reactive explicitement en quittant un profil statique.
- Champs de couleur/intensite OFF visibles sur les profils automatiques, comme sur CARAC.
- Sans connexion TriCaster : animation jaune clignotante conservee. Connecte : affichage REC ON/OFF, STREAM ON/OFF et combinaison.
- Lorsque les deux etats sont OFF, afficher l'etat OFF du dernier profil actif ou d'un profil choisi dans les reglages TriCaster.
- 9 nouveaux modeles editables : signatures CARAC bleu/vert/orange, respiration, comete, ouverture, bleu/orange TriCaster, pulsation REC, vague STREAM, double signature et veille bleue. Les 5 anciens modeles restent disponibles.
- Aucun modele n'ecrase une animation existante : utiliser Banque, choisir un modele puis enregistrer sa propre copie.

## Utilisation du reseau

Memoriser le Wi-Fi dans la rubrique existante, puis choisir ce reseau dans Adresse IP — DHCP ou fixe.
DHCP reste le defaut de tous les reseaux sans profil explicite.
En IP fixe, indiquer IP, masque et passerelle ; DNS principal vide utilise la passerelle, DNS secondaire facultatif.
Enregistrer et appliquer. La page affiche la nouvelle adresse ou l'acces mDNS. Le point d'acces autonome conserve son adresse habituelle.
Les adresses ne sont jamais reutilisees sur un autre SSID. Un profil invalide ou absent au demarrage conserve DHCP.
Le menu ne peut pas verifier qu'une adresse statique est libre sur le routeur : choisir une adresse libre ou reservee.

## Roles et priorite conserves

CARAC seul possede Direct/Alerte et garde la priorite manuelle.
REC, STREAM et REC + STREAM sont des profils fixes commandes exclusivement par le TriCaster.
Rendre la main au TriCaster reprend les etats actuels ; OFF general eteint tout et suspend le suivi.
Le boitier lit les etats mais ne commande ni l'enregistrement ni la diffusion.
36 WS2812E sur D5/GPIO14, macros, logos, bibliotheque, editeur et OTA conserves.

## Installation et conservation

Le .ino est complet et autonome. Les headers joints servent aussi aux tests et a la maintenance.
Installer le .bin via l'OTA ou televerser le .ino par USB avec le decoupage flash actuel et Only Sketch.
Aucune remise a zero necessaire. Ne pas formater LittleFS.
Les identifiants reseau deja enregistres restent inchanges, meme si le nom du produit change.
Les structures EEPROM historiques et sauvegardes V1/V2 restent compatibles.
Reglages IP dans /network.cfg, reglages TriCaster dans /tricaster.cfg, avec checksum et remplacement atomique.
Les sauvegardes historiques .cfg ne contiennent pas ces deux fichiers ni les images et sequences de bibliotheque : conserver les exports d'animations et noter les reglages de connexion avant une remise a zero.

## Validation

Core ESP8266 3.1.2, NeoPixel 1.15.5, NodeMCU ESP-12E.
Tests des fonctions reelles d'application et de sauvegarde reseau, validation IPv4, retour DHCP et isolation entre SSID.
Tests des vrais gestionnaires de commande, parseur TriCaster et controleur ON/OFF/priorite.
Tests du JavaScript, de la banque d'animations et du contraste des boutons ; rendu HTML produit par les fonctions C++ reelles.
Tests existants moteur LED, EEPROM, OTA et budget memoire.
La connexion IP fixe reelle, le routeur et le TriCaster doivent etre valides sur le materiel de l'utilisateur.
