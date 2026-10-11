# ON AIR Damien — câblage ruban adressable

## Ruban retenu

- WS2812E 5 V, 60 LED/m, IP30
- longueur totale du contour : 500 mm
- 200 mm + 50 mm + 200 mm + 50 mm
- 30 LED au total

Ordre logique prévu dans le firmware :

- LED 0 à 11 : côté haut, gauche vers droite
- LED 12 à 14 : côté droit, haut vers bas
- LED 15 à 26 : côté bas, droite vers gauche
- LED 27 à 29 : côté gauche, bas vers haut

Le sens des flèches DATA du ruban doit suivre cet ordre.

## Schéma de principe

```text
ALIMENTATION 5 V / 3 A
        +5V -----------------------------+------------------> +5V RUBAN
                                         |
                                         +--> VIN/5V ESP8266
        GND -----------------------------+------------------> GND RUBAN
                                         |
                                         +--> GND ESP8266
                                         |
                                         +--> GND 74AHCT125

ESP8266 D5 / GPIO14
        |
        +--> 74AHCT125 entrée 1A (pin 2)

74AHCT125
  pin 14 VCC --> +5V
  pin 7  GND --> GND
  pin 1  /OE --> GND
  pin 2  1A  <-- D5 / GPIO14
  pin 3  1Y  --> 330 ohms --> DIN du premier WS2812E

100 nF entre pins 14 et 7 du 74AHCT125.
1000 uF / 10 V entre +5V et GND près du premier WS2812E.
```

## Alimentation

Le calcul de dimensionnement se fait au pire cas :

30 LED × 60 mA = 1,8 A pour le ruban à blanc 100 %.

Avec l'ESP8266 et une marge de sécurité, utiliser une alimentation régulée 5 V / 3 A.

Pour 500 mm seulement, une injection d'alimentation au début du ruban suffit normalement. Le firmware limite toujours les intensités par les réglages des macros.

## Câble recommandé

Pour un câble court entre le boîtier et le ruban :

- 3 conducteurs
- +5 V : 0,5 mm² minimum
- GND : 0,5 mm² minimum
- DATA : 0,14 à 0,5 mm²
- connecteur verrouillable recommandé : Molex Micro-Fit 3.0, 3 contacts

Repérage conseillé :

1. +5 V
2. DATA
3. GND

Ne jamais brancher DATA sans GND commun.

## Ancien montage RGB analogique

La V3.0.0 n'utilise plus les trois MOSFET IRLZ44N ni les sorties D2/D1/D5 séparées.

Le seul signal LED est maintenant D5 / GPIO14 vers le 74AHCT125, puis vers DIN du ruban WS2812E.
