# One air CARAC v2 — 2.0.1 — MOC 02 / TriCaster

Base verifiee : one-air-carac-v2.0.0, commit 8cac650c6adcc539979fc66f6706568b02d870d2.
36 WS2812E, D5/GPIO14, plafond 100 %, AP ON_AIR-MOC-02, macros, OTA et suivi TriCaster REC/STREAM conserves. Aucun boitier flashe et aucune branche Damien modifiee.

## Installation
Installer ONE_AIR_CARAC_V2_0_1_OTA.bin via /update. Ne pas effacer EEPROM ni formater LittleFS. Les identifiants et parametres TriCaster existants restent conserves.

## Wi-Fi CARAC
1. Se connecter au point d'acces ON_AIR-MOC-02 puis ouvrir http://192.168.4.1/settings.
2. Activer la connexion externe, saisir le SSID CARAC exact (2.4 GHz) et son mot de passe localement dans le formulaire, puis ENREGISTRER ET CONNECTER.
3. Dans Adresse IP, selectionner ce meme reseau et DHCP, puis enregistrer/appliquer.
4. Verifier le SSID et l'IP attribuee dans Reseau. Le dernier reseau enregistre est prioritaire au prochain boot. Oublier Sarah_Charles_Home si ce reseau ne doit plus servir de secours.
5. Verifier ensuite la connexion TriCaster et les etats REC/STREAM sur le reseau CARAC.

Aucun SSID CARAC exact ni mot de passe connu ou embarque. Une mise a jour OTA conserve Sarah_Charles_Home tant que CARAC n'a pas ete configure. Les identifiants restent en flash sur le boitier ; ne pas publier de sauvegarde contenant des secrets.

## Comportement et validation
Le code existant utilise DHCP explicite (WiFi.config avec adresses nulles), AP+STA, sauvegarde en flash et tentatives directes sans scan bloquant toutes les 30 secondes. La 2.0.1 affiche le reseau prioritaire et l'aide de configuration CARAC, explique la raison 201 dans le journal et desactive la reconnexion SDK concurrente ; le planificateur applicatif conserve les tentatives automatiques.

CI : tests de conservation de l'original, EEPROM, macros, moteur LED, Wi-Fi, adressage, TriCaster, interface et OTA ; compilation NodeMCU ESP-12E avec ESP8266 3.1.2 / NeoPixel 1.15.5 ; controle memoire et SHA256. La CI ne prouve pas la connexion physique a CARAC ou au TriCaster : validation sur place requise.
