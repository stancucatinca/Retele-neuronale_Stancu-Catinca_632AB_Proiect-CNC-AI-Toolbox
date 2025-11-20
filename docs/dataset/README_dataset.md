
# Dataset – CNC-AI Toolbox

Acest fișier documentează setul de date folosit în proiectul *CNC-AI Toolbox – Optimizarea parametrilor de așchiere cu Rețele Neuronale*.

##  Sursa datelor

Datele sunt **simulate programatic** pe baza relațiilor empirice cunoscute în prelucrările CNC:
- Ra crește cu avansul f
- Ra scade cu viteza de așchiere V
- Timpul scade cu creșterea lui V și f
- Materialul piesei și scula influențează valoarea finală

Nu există valori lipsă. Distribuția este controlată (DoE + sampling randomizat).

##  Structura dataset-ului (50 observații)

| Coloană | Tip | Descriere |
|---------|------|-----------|
| V | numeric | viteză de așchiere (m/min) |
| f | numeric | avans pe rotație sau per dinte |
| ap | numeric | adâncime de așchiere |
| D | numeric | diametrul sculei |
| work_material | categorial | material piesă |
| tool_type | categorial | tip sculă |
| tool_material | categorial | material sculă |
| coating | categorial | acoperire sculă |
| Ra | numeric | rugozitate estimată |
| timp | numeric | timpul de prelucrare estimat |

##  Format

Fișierul este disponibil în format **CSV**:  
`dataset_simulare.csv`

##  Utilizare

Datasetul este folosit pentru:
- antrenarea rețelei neuronale
- validarea modelului
- generarea soluțiilor Pareto
- testarea selectorului de scule

##  Dimensiune

- 50 rânduri  
- 10 coloane

