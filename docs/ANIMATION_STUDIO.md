# Atelier d’animations 3.5.0

## Couleurs et sélection

Cliquer au centre d’une LED pour la sélectionner ou la désélectionner. Tout/Aucune et Haut/Bas/Gauche/Droite permettent de choisir une zone rapidement. Choisir une couleur de la palette (13 teintes) ou une couleur libre pour peindre la sélection. Le curseur Intensité de la séquence règle de 0 à 100 % l’ensemble de l’animation ; il est mémorisé à l’enregistrement. Le réglage d’intensité de l’émission reste également appliqué.

Le grand ON AIR simule la diffusion des LED dans les lettres, d’après les photos du boîtier. Il s’agit d’une approximation ; le diffuseur physique peut mélanger davantage ou différemment les couleurs. L’aperçu sur le boîtier reste la référence.

## Étapes

Couleurs LED : image de 36 couleurs, maintien et transition directe ou fondue.

Chenillard : choisir LED de départ, LED d’arrivée et intervalle par déplacement (ms). L’ordre peut être inversé, par exemple 36 → 1. La durée de l’étape est ajustée pour permettre un parcours complet ; elle reste modifiable ensuite.

Flash / strobe : choisir les LED, la couleur et l’intervalle allumé/éteint (20 à 10000 ms). Appliquer aux LED sélectionnées actualise le groupe qui clignote. Un intervalle de 100 ms donne 100 ms allumé puis 100 ms éteint. Le maintien détermine la durée totale de cette étape.

Douze étapes maximum ; duplication, déplacement, suppression et export/import sont conservés. Les effets procéduraux génèrent leur mouvement pendant la lecture : ils ne consomment pas une étape par LED ni par flash.

## Banque

Banque, à côté d’Exporter et Importer, propose les modèles Rouge · Bleu · Vert, Respiration, Arc-en-ciel horizontal, Chenillard et Flash / strobe. Utiliser charge un modèle comme nouvelle animation à enregistrer.

Dans Mes animations, Modifier rappelle une animation existante. Copier charge une variante indépendante : l’original reste conservé et la nouvelle séquence peut être renommée puis enregistrée. La liste en bas de l’éditeur reste disponible pour rappeler directement une animation.

## Compatibilité

Les anciens fichiers CUE1 version 1 restent lisibles. Les nouveaux fichiers CUE1 version 2 gardent 1356 octets et le checksum. Ils utilisent l’octet 6 pour l’intensité, l’octet 7 pour le marqueur 0xA5 et le champ transition d’une étape procédurale pour son type et son intervalle. Aucun changement du format EEPROM des réglages. Un ancien firmware ne peut pas lire les nouvelles séquences version 2 : exporter ses animations avant un éventuel retour à une ancienne version.
