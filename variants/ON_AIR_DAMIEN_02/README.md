# ON AIR Damien 02 — V3.5.1 STUDIO — correction Wi-Fi

Corrige la V3.5.0-02 pour le deuxième boîtier.
- Les tentatives de connexion utilisent directement les SSID mémorisés, même absents de la liste détectée.
- Les réseaux enregistrés sont essayés à tour de rôle, sans scan automatique bloquant.
- La reconnexion reste active même quand un téléphone utilise le point d'accès.
- Les scans manuels et l'application des réglages ne démarrent pas simultanément.
- Diagnostic série : statut, motif de déconnexion et adresse IP obtenue. Aucun mot de passe n'est journalisé.
- Le scan manuel inclut les points d'accès masqués ; leur nom n'est pas nécessairement annoncé.

Conservés : éditeur complet V3.5.0 STUDIO, bibliothèque, séquences, macros, logos, effets, OTA, 36 WS2812E, D5/GPIO14, EEPROM et fichiers LittleFS.
Identifiants par défaut : ON_AIR-MOC-02, onair-moc-02.local ; mot de passe AP par défaut 12345678.
Les réglages et mots de passe déjà enregistrés restent conservés.
Ne pas effacer la flash ni faire de remise à zéro usine.
Le firmware Damien original et ses releases sont inchangés.

Tests de reconnexion exécutant les fonctions C++ réelles avec une radio simulée ; tests moteur d'animation/configuration/OTA/mémoire et compilation ESP8266 en CI.
Le comportement radio dans le logement doit encore être vérifié sur le boîtier : ce correctif supprime les blocages logiciels identifiés, sans prétendre avoir confirmé la cause de l'absence au scan.
