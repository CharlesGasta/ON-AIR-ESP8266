# Changelog

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
