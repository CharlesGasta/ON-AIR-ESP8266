# Vérification de l'interface embarquée

Le CSS et les scripts sont stockés en flash (`PROGMEM`). Les pages restent envoyées par petits fragments pour éviter de construire une grande page en RAM. La nouvelle page `/firmware` utilise le gestionnaire de mise à jour existant `POST /update` ; la page avancée `/update` reste disponible.

## Aperçu et tests

Pré-requis : Python 3, Node.js, Playwright et Chrome (ou une autre installation compatible avec `BROWSER_CHANNEL`).

```text
python tools/check-firmware.py
node tools/preview.cjs
node tools/check-ui.cjs
```

`preview.cjs` exécute une traduction limitée des générateurs C++ de pages avec des valeurs de démonstration et des adaptateurs serveur. Il réutilise directement le HTML, CSS, JavaScript et les logos intégrés du firmware. Ce mécanisme ne remplace pas une compilation ESP8266.

`check-ui.cjs` intercepte toutes les requêtes vers le nom fictif `onair.test`, simule les réponses du boîtier et produit captures et rapport dans `preview/` (non versionné). Aucun test ne se connecte à une carte réelle ou ne flashe de firmware.

Le contrôle `check-firmware.py` compare les parties hors présentation avec le commit v3.0.4 `dfaecbc`. Il protège les structures de configuration, la persistance, les migrations, les valeurs par défaut, le pilotage LED, les gestionnaires existants et la boucle principale.

Les commandes d'activation ne sont jamais rejouées automatiquement après une erreur réseau. L'état DIRECT est affiché uniquement après une réponse valide du boîtier ; une réponse plus ancienne ne peut pas remplacer celle d'une commande plus récente. En arrière-plan, le navigateur suspend la consultation de l'état. Au retour, il demande à nouveau confirmation au boîtier.
