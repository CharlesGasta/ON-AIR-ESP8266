# Vérification de l'interface embarquée

Le CSS et les scripts sont stockés en flash (`PROGMEM`). Les pages restent envoyées par petits fragments pour éviter de construire une grande page en RAM. La nouvelle page `/firmware` utilise le gestionnaire de mise à jour existant `POST /update` ; la page avancée `/update` reste disponible.

## Aperçu et tests

Pré-requis : Python 3, Node.js, Playwright et Chrome (ou une autre installation compatible avec `BROWSER_CHANNEL`).

```text
python tools/check-firmware.py
python tools/check-motion.py
node tools/preview.cjs
node tools/check-ui.cjs
```

`preview.cjs` exécute une traduction limitée des générateurs C++ de pages avec des valeurs de démonstration et des adaptateurs serveur. Il réutilise directement le HTML, CSS, JavaScript et les logos intégrés du firmware. Ce mécanisme ne remplace pas une compilation ESP8266.

`check-ui.cjs` intercepte toutes les requêtes vers le nom fictif `onair.test`, simule les réponses du boîtier et produit captures et rapport dans `preview/` (non versionné). Aucun test ne se connecte à une carte réelle ou ne flashe de firmware.

Le contrôle `check-firmware.py` protège le format EEPROM historique par comparaison avec la v3.1.1. `check-motion.py` nécessite g++ ou clang++ : il compile le véritable moteur extrait du firmware et les véritables fonctions de démarrage et persistance avec des adaptateurs matériels, réseau et fichiers de test. Il s'exécute dans GitHub Actions avant chaque compilation.

Les réglages DIRECT sont dans `/motion.cfg` avec checksum, écriture temporaire puis remplacement. Les backups V2 incluent cette extension ; les backups V1 restent acceptés. Le thème est local au navigateur et ne provoque aucune écriture sur la flash du boîtier.

Les commandes d'activation ne sont jamais rejouées automatiquement après une erreur réseau. L'état DIRECT est affiché uniquement après une réponse valide du boîtier ; une réponse plus ancienne ne peut pas remplacer celle d'une commande plus récente. En arrière-plan, le navigateur suspend la consultation de l'état. Au retour, il demande à nouveau confirmation au boîtier.
