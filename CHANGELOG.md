# Changelog

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
