
# 📘 Descriere Dataset CNC-AI Toolbox

## 1. Introducere
Acest dataset este utilizat pentru antrenarea rețelelor neuronale care prezic:
- Rugozitatea Ra
- Timpul de prelucrare

Datasetul conține 50 de observații reale din simularea CNC.

## 2. Structura dataset-ului

| Caracteristică | Tip | Unitate | Descriere |
|----------------|-----|----------|-----------|
| V | numeric | m/min | Viteză așchiere |
| f | numeric | mm/rot | Avans |
| ap | numeric | mm | Adâncime |
| D | numeric | mm | Diametru sculă |
| work_material | categorial | - | Material piesă |
| tool_type | categorial | - | Tip sculă |
| tool_material | categorial | - | Material sculă |
| coating | categorial | - | Acoperire |
| Ra | numeric | µm | Rugozitate |
| timp | numeric | s | Timp prelucrare |

## 3. Sursa Datelor

Datasetul este generat prin simulare Python folosind modele matematice CNC:
- Ra scade cu V
- Ra crește cu f și ap
- timpul scade cu V și f
- se adaugă zgomot gaussian pentru realism

## 4. EDA

Graficele sunt incluse în folderul `figures/`.

