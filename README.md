# Hunger_Gamer-Sim
Door Tobias, Khai-tam, Kevin en Peter

## Gebruik
1. Executeer het main.py bestand het programma zal dan een venster aanmaken waarin de simulatie wordt aangetoond
![image](https://user-images.githubusercontent.com/35180025/224565749-96c4eb3c-357e-44df-b629-fe354b0192e3.png)
2. Druk op de spacebar op de simulatie stapsgewijs te vorderen

## Objecten op het veld
### De Agent (Blauwe bol)
- Kan objecten die het heeft gezien of opgepakt onthouden in een variable genaamd memory
- Kan alleen grids direct naast zichzelf zien
- Berekent op basis van zijn memory en minst bezochte grid plek en gevonden Eten hotspot zijn volgende richting
- Kan op reflex direct Enemies ontwijken als het direct naast hem belanden

### De Enemies (Rood bolen)
- bewegen volledig willekeurig in 4 richtingen
- Kunnen de Agent beschadigen 

### Eten (Groen bol)
- Pick-upable object
- Hervult de Agent hunger bar
- Spawnt in voorgedefineerde hotspots
- bestaat een kleine kans voor andere willekeurige plekken

### Wapen (Gele omgedraaide L)
- Pick-upable object
- Spawnt maar 1 op het veld willekeurig
- Geeft extra DMG waarneer opgepakt door de Agent
