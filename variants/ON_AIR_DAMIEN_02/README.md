# ON AIR Damien 02 — V3.0.4

Clone de la release vérifiée v3.0.4 (commit dfaecbc222bb5129992370446e1c1a063652c334).
La V3.0.4 demandée existe ; les versions plus récentes ne sont donc pas utilisées.

Seules les chaînes d'identification ON_AIR-MOC et onair-moc reçoivent le suffixe -02, y compris leurs indications dans l'interface.
Nom affiché et SSID AP par défaut : ON_AIR-MOC-02.
mDNS / hostname : onair-moc-02 (http://onair-moc-02.local).
Mot de passe AP inchangé : 12345678. Accès AP : http://192.168.4.1.

Matériel inchangé : NodeMCU ESP8266 ESP-12E, 36 WS2812E, DATA D5 / GPIO14, NEO_GRB 800 kHz.
Toutes les macros, logos, animations, luminosités et fonctions restent identiques à la V3.0.4.
Aucune intégration TriCaster supplémentaire n'est ajoutée.

Le boîtier vierge initialise et sauvegarde les nouveaux noms par setDefaults().
Le format EEPROM, les marqueurs, les migrations et les paramètres existants restent inchangés.
Une mise à jour d'un boîtier déjà configuré conserve ses noms enregistrés : elle ne force pas leur remplacement.
Ne pas restaurer une sauvegarde de l'autre boîtier sans adapter ses noms.
Un ESP vierge nécessite un premier flash USB ; le .bin est ensuite utilisable via l'OTA de l'interface.

L'original ON_AIR_ESP8266.ino et ses releases ne sont pas modifiés.
Le clone se trouve sur la branche damien-02-v3.0.4 dans variants/ON_AIR_DAMIEN_02/.
Compilation CI : core ESP8266 3.1.2, Adafruit NeoPixel 1.15.2, esp8266:esp8266:nodemcuv2.
La compilation et l'identité du code sont vérifiées par CI ; aucun essai physique du deuxième boîtier n'est revendiqué.
