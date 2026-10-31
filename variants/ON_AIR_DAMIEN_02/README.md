# ON AIR Damien 02 — V3.5.0 STUDIO

Version complète avec LED adressables et éditeur de cinématique.
Clone exact de la dernière release Damien v3.5.0, commit 35e91ae68b172eb7efb5c7d3c07fd48e41bbc532.
Cette release remplace le choix de base v3.0.4-02 pour le deuxième boîtier.

Conservés : 36 LED WS2812E sur D5 / GPIO14, macros, logos, animations de démarrage, éditeur LED par LED, séquences, chenillards, flash/strobe, fondus, banque et bibliothèque partagée d'animations, import/export, réglages et fonctions OTA.
Seules les chaînes d'identification ON_AIR-MOC et onair-moc reçoivent le suffixe -02.
Nom et SSID AP par défaut : ON_AIR-MOC-02.
Adresse mDNS : http://onair-moc-02.local
Mot de passe AP par défaut hérité de la source : 12345678.
Adresse sur le réseau AP : http://192.168.4.1

Le format EEPROM, les fichiers LittleFS, les migrations et les réglages restent identiques.
Un boîtier vierge reçoit les noms -02 au premier démarrage.
Un boîtier déjà configuré conserve ses noms et son mot de passe enregistrés : les adapter dans les paramètres si nécessaire.
Ne pas effacer les paramètres ni restaurer la sauvegarde d'un autre boîtier sans adapter ses noms.
Premier flash USB pour un boîtier vierge ; mises à jour suivantes possibles par OTA.

L'original Damien, la branche main et les releases originales ne sont pas modifiés.
Compilation et tests automatiques exécutés en CI ; aucun nouvel essai physique n'est revendiqué.
