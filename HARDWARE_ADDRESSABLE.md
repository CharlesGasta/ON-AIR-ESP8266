# ON AIR Damien — hardware ruban adressable V3.0.1

## Ruban et nombre de pixels confirmes

- 36 LED WS2812E adressables 5 V, LED 0 a 35.
- DATA sur D5 / GPIO14 de l'ESP8266 NodeMCU.
- Couleurs dans le firmware : NEO_GRB + NEO_KHZ800.
- Enchainement physique : DOUT d'une LED/section vers DIN de la suivante.
- Le sens de parcours du ruban definit le sens des animations.
- Ancien perimetre cible : 200 + 50 + 200 + 50 mm = 500 mm.
- ATTENTION : 36 LED a 60 LED/m representent 600 mm de ruban, et non 500 mm. Verifier la densite reelle et le compte des pixels par cote.
- Ne pas supposer de repartition fixe par cote pour l'instant. Les animations V3.0.1 fonctionnent sur les 36 LED en sequence.

## Branchement simple demande : une seule alimentation USB-C, via VV

```text
         Cable USB-C 5 V vers NodeMCU
                      |
                  ESP8266
                 /   |    \
               VV   GND  D5/GPIO14
                |    |      |
                |    |     330 ohms
                |    |      |
                |    |      +--------------> DIN premiere LED
                |    +---------------------> GND ruban
                +--------------------------> +5 V ruban

Condensateur 1000 uF / 10 ou 16 V, proche debut ruban :
  borne + vers +5 V
  borne - vers GND
```

## Limite de luminosite V3.0.2

Le firmware limite desormais chaque sortie LED au maximum a **25 %**, quelle que soit la luminosite de la macro (jusqu'a 100 % sur l'interface) et y compris les alertes. Cette limitation sert a reduire les consommations mais ne mesure pas le courant.

Tableau pour 36 pixels blancs :
- 25 % selon le fabricant WS2812E 12 mA/canal : env. 0,64 A pour ESP + ruban
- 25 % avec hypothese haute 20 mA/canal : env. 0,86 A pour ESP + ruban
- estimation de reserve ESP : 300 mA, sans garantie sur les pics reels
- la source USB et la carte VV restent a qualifier physiquement

## Limites electriques importantes

- Broche 3V3 : NE JAMAIS ALIMENTER LE RUBAN DEPUIS 3V3.
- Le signal D5 / GPIO14 est a 3,3 V, tandis que les LED sont alimentees a 5 V. Cela peut fonctionner avec un cablage DATA tres court, mais n'est pas garanti a toutes les tensions/temperatures. Ajouter un 74AHCT125 si des erreurs apparaissent.
- GND commun obligatoire.
- 36 LED x 60 mA = jusqu'a 2,16 A sur le ruban pour un blanc pleine puissance, PLUS la consommation/pics de l'ESP8266.
- VV correspond souvent au 5 V USB sur certaines cartes NodeMCU, mais sa capacite en courant depend du modele, des pistes, connecteurs et composants de protection. Sans verification de la carte, NE PAS CONSIDERER une alimentation de 36 LED a pleine puissance par VV comme validee.
- Reduire les intensites des macros ne constitue pas une limitation electrique absolue.
- L'utilisateur souhaite un montage sans fusible externe ; surveiller attentivement les courts-circuits de soudure et l'echauffement. Une protection amont adequate reste recommandee.

## Composants

- ESP8266 NodeMCU avec entree USB-C.
- 36 LED WS2812E 5 V.
- Resistance serie DATA 330 ohms, 1/4 W.
- Condensateur 1000 uF / 10 V ou 16 V entre +5 V et GND pres du ruban.
- Fil +5 V et GND de section convenable pour plus de 2 A max.
- Fil DATA court.
- Fils de pontage 5 V, GND et DOUT->DIN aux angles du logo.
- Gaine thermoretractable et isolant aux raccords.

## Sorties inutilisees

Les trois sorties PWM RGB analogiques et les 3 MOSFETs IRLZ44N ne sont plus utilises.

Le firmware pilote le ruban exclusivement avec la ligne DATA D5/GPIO14.
