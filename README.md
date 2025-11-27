
# 📘 README 

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** [Stancu Catinca Stefania]  
**Proiect:** CNC-AI Toolbox – Optimizarea parametrilor de tăiere și Selectare Inteligentă a Sculelor  
**Data:** [20.11.2025]  

---

## Introducere

Acest document descrie activitățile realizate în **Etapa 3**, în care se analizează și se preprocesează setul de date necesar proiectului. Obiectivul este pregătirea corectă a datelor pentru instruirea rețelei neuronale, asigurând calitatea, consistența și reproductibilitatea acestora.

---

## 1. Structura Repository-ului Github (Etapa 3)

```
cnc-ai-toolbox/
├── README.md
├── docs/
│   └── datasets/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── train/
│   ├── validation/
│   └── test/
├── src/
│   ├── preprocessing/
│   ├── data_acquisition/
│   └── neural_network/
├── config/
└── requirements.txt
```

---

## 2. Descrierea Setului de Date

Datasetul este folosit pentru:
- antrenarea rețelei neuronale
- validarea modelului
- generarea soluțiilor Pareto
- testarea selectorului de scule



### 2.1 Sursa datelor

* **Origine:** Date simulate programatic pentru procese CNC (frezare/strunjire)(AI) 
* **Modul de achiziție:** Simulare Python / DoE numeric  
* **Perioada colectării:** Condiții experimentale specifice

Datele sunt **simulate programatic** pe baza relațiilor empirice cunoscute în prelucrările CNC:
- Ra crește cu avansul f
- Ra scade cu viteza de așchiere V
- Timpul scade cu creșterea lui V și f
- Materialul piesei și scula influențează valoarea finală


### 2.2 Caracteristicile Dataset-ului

* **Număr observații:** 50
* **Număr caracteristici:** 10
* **Tipuri de date:** Numeric + Categorial  
* **Format:** CSV

### 2.3 Descrierea caracteristicilor

| Caracteristică | Tip | Unitate | Descriere | Domeniu |
|----------------|-----|----------|-----------|---------|
| V | numeric | m/min | viteză așchiere | 120–350 |
| f | numeric | mm/rot | avans | 0.03–0.22 |
| ap | numeric | mm | adâncime | 0.1–1.2 |
| D | numeric | mm | diametru sculă | 6–20 |
| work_material | categorial | – | material piesă | {steel, aluminum, cast_iron} |
| tool_type | categorial | – | tip sculă | {endmill, CNMG, VNMG, drill} |
| tool_material | categorial | – | material sculă | {Carbură, HSS, Cermet} |
| coating | categorial | – | acoperire | {TiAlN, TiN, None} |
| Ra | numeric | µm | rugozitate | 0.4–4 |
| timp | numeric | s | timp prelucrare | 5–40 |

---

## 3. Analiza Exploratorie a Datelor (EDA)

### 3.1 Statistici descriptive
- medie, mediană, deviație standard  
- distribuii V,f,ap,Ra,timp  
- corelații (Pearson)

### 3.2 Calitatea datelor
- 0% lipsuri  
- distribuție echilibrată materiale  
- corelații așteptate: f→Ra, V→timp

### 3.3 Probleme detectate
- distribuția Ra ușor neuniformă  
- distribuție inegală a coating față de material  

---

## 4. Preprocesarea Datelor

### 4.1 Curățare
- eliminare duplicate  
- eliminare combinații fizic imposibile  
- conversie tipuri

### 4.2 Transformări
- scaling (StandardScaler) pentru V,f,ap,D  
- encoding pentru variabile categoriale

### 4.3 Structurare
* 70% – train  
* 15% – validation  
* 15% – test  

### 4.4 Salvare
- `data/processed/data_clean.csv`  
- foldere pentru train/validation/test  
- `config/preprocessing.yml`

---

## 5. Fișiere Generate

- dataset_simulare.csv  

---

## 6. Stare Etapă

- [x] Structură repository  
- [x] Dataset generat  
- [x] Preprocesare efectuată  
- [x] Documentație completată  

---

