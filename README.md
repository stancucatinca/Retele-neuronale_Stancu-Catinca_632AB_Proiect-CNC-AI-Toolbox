
# README - CNC-AI Toolbox

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** [Stancu Catinca Stefania]  
**Proiect:** CNC-AI Toolbox – Optimizarea parametrilor de tăiere și Selectare Inteligentă a Sculelor  
**Data:** [20.11.2025]  

---

## Introducere

**CNC-AI Toolbox** este o aplicație software inteligentă destinată optimizării proceselor de prelucrare prin așchiere (frezare). Proiectul abordează problema selectării dificile a parametrilor tehnologici — Viteza de așchiere ($V$), Avansul ($f$) și Adâncimea de așchiere ($a_p$) — care influențează direct calitatea piesei și productivitatea.

În mod tradițional, acești parametri sunt aleși din tabele sau din experiență, ceea ce duce adesea la erori. Acest proiect propune o soluție automatizată bazată pe Inteligență Artificială care:

1.  **Recomandă Scula:** Selectează automat tipul de freză potrivit în funcție de materialul piesei (Oțel, Aluminiu, Fontă).
2.  **Prezice Calitatea ($R_a$):** Utilizează o **Rețea Neuronală** antrenată pe date simulate pentru a estima rugozitatea suprafeței înainte de prelucrarea efectivă.
3.  **Optimizează Procesul:** Identifică cele mai bune combinații de parametri (soluții Pareto) care oferă un timp de execuție minim, menținând în același timp rugozitatea sub limita impusă de utilizator.

---

## 1. Structura Repository-ului Github (Etapa 3)

```text
cnc-ai-toolbox/
├── README.md                       # Documentația principală a proiectului
├── requirements.txt                # Lista bibliotecilor necesare (pandas, torch, etc.)
├── config/
│   └── settings.json               # Fișier de configurare pentru căi și hiperparametri
├── data/
│   ├── raw/
│   │   └── dataset_simulare.csv    # Datele brute generate de simulare
│   ├── processed/
│   │   ├── scaler_x.pkl            # Scalerul salvat pentru input-uri (standardizare)
│   │   └── scaler_y.pkl            # Scalerul salvat pentru output-uri (Ra)
│   ├── train/
│   │   └── train.csv               # Setul de date pentru antrenare
│   ├── validation/
│   │   └── validation.csv          # Setul de date pentru validare
│   └── test/
│       └── test.csv                # Setul de date pentru testare
├── docs/
│   └── datasets/                   # Documentație suplimentară despre date (opțional)
├── models/
│   └── model_v1.pkl                # Modelul rețelei neuronale antrenat (salvat)
├── reports/                        # Folder generat automat cu rezultatele optimizărilor
│   ├── Raport_Optimizare_*.txt     # Raport detaliat (human-readable)
│   └── Solutii_Pareto_*.csv        # Tabel cu soluțiile optime (Excel-ready)
└── src/
    ├── data_acquisition/
    │   └── generate_simulation.py  # Scriptul care generează datele sintetice
    ├── neural_network/
    │   ├── model_regression.py     # Definirea arhitecturii rețelei neuronale (clasa CNCModel)
    │   ├── train_model.py          # Scriptul de antrenare a modelului
    │   └── predict.py              # Scriptul principal: Interfața, AI + Optimizare Pareto + Raportare
    └── preprocessing/
        └── preprocess.py           # Scriptul de curățare, scalare și împărțire a datelor
````

-----

## 2\. Descrierea Setului de Date

Datasetul este folosit pentru:

  - antrenarea rețelei neuronale (regresie pentru $R_a$)
  - validarea modelului
  - generarea soluțiilor Pareto (optimizare multi-obiectiv)

### 2.1 Sursa datelor

  * **Origine:** Date simulate programatic pentru procese CNC (frezare).
  * **Modul de achiziție:** Simulare Python (`generate_simulation.py`) bazată pe formule tehnologice + zgomot gaussian.
  * **Context:** Datele sunt generate pentru a acoperi un spațiu larg de parametri ($V, f, a_p$), simulând comportamentul real al așchierii oțelului, aluminiului și fontei.

Datele respectă relațiile empirice cunoscute:

  - $R_a$ crește proporțional cu pătratul avansului ($f^2$).
  - $R_a$ scade ușor odată cu creșterea vitezei de așchiere ($V$).
  - Timpul de prelucrare este calculat matematic ($L / V_f$).

### 2.2 Caracteristicile Dataset-ului

  * **Număr observații:** 1000 (generate sintetic pentru o bună convergență a rețelei).
  * **Număr caracteristici:** 7 (5 intrări + 2 ieșiri).
  * **Tipuri de date:** Numeric (float) + Categorial (codificat numeric).
  * **Format:** CSV (`dataset_simulare.csv`).

### 2.3 Descrierea caracteristicilor (Coloane CSV)

| Caracteristică | Tip | Unitate | Descriere | Domeniu |
|---|---|---|---|---|
| **V** (Input) | numeric | m/min | Viteza de așchiere | 100 – 350 |
| **f** (Input) | numeric | mm/rot | Avansul de așchiere | 0.05 – 0.35 |
| **ap** (Input) | numeric | mm | Adâncimea de așchiere | 0.5 – 4.0 |
| **D** (Input) | numeric | mm | Diametrul sculei | {10, 12, 16, 20} |
| **work\_material** (Input)| categorial | - | Cod material piesă | 0=Oțel, 1=Alu, 2=Fontă |
| **Ra** (Target AI) | numeric | µm | Rugozitatea suprafeței | 0.4 – 6.0 |
| **timp** (Target Calc)| numeric | s | Timpul de prelucrare | Calculat ($L=100mm$) |

> **Notă:** Caracteristicile sculei (Tip, Acoperire) sunt deduse logic în faza de post-procesare pe baza materialului piesei, nu sunt incluse ca text în datele brute pentru a simplifica antrenarea.

-----

## 3\. Analiza Exploratorie a Datelor (EDA)

### 3.1 Statistici descriptive

  - Au fost calculate media și deviația standard pentru a verifica plauzibilitatea datelor simulate.
  - Datele acoperă întreg domeniul de lucru al mașinii CNC vizate.

### 3.2 Calitatea datelor

  - **Lipsuri:** 0% (datele sunt generate controlat).
  - **Zgomot:** A fost adăugat intenționat un zgomot aleatoriu ($normal distribution$) peste $R_a$ teoretic pentru a simula erorile de măsurare și vibrațiile din lumea reală.

-----

## 4\. Preprocesarea Datelor

Procesul este automatizat în scriptul `src/preprocessing/preprocess.py`.

### 4.1 Curățare

  - Verificare consistență tipuri de date (float32).

### 4.2 Transformări (Normalizare)

  - **StandardScaler:** Variabilele de intrare ($V, f, a_p, D$) și ieșirea ($R_a$) sunt scalate (medie 0, deviație 1) pentru a asigura convergența rapidă a rețelei neuronale.
  - Obiectele scaler sunt salvate (`scaler_x.pkl`, `scaler_y.pkl`) pentru a fi folosite ulterior la predicție (denormalizare).

### 4.3 Structurare (Data Splitting)

Setul de date a fost amestecat și împărțit aleatoriu:

  * **70% – Train:** Pentru antrenarea rețelei (backpropagation).
  * **15% – Validation:** Pentru monitorizarea pierderii (loss) în timpul antrenării.
  * **15% – Test:** Pentru evaluarea finală a performanței modelului.

### 4.4 Salvare

Datele procesate sunt salvate în format CSV fără antet (header) pentru compatibilitate directă cu `PyTorch DataLoader`:

  - `data/train/train.csv`
  - `data/validation/validation.csv`
  - `data/test/test.csv`

-----

## 5\. Fișiere Generate

  - **Raw:** `data/raw/dataset_simulare.csv`
  - **Processed Scalers:** `data/processed/scaler_x.pkl`, `data/processed/scaler_y.pkl`
  - **Model:** `models/model_v1.pkl` (după rularea antrenării)

-----

## 6\. Stare Etapă

  - [x] Structură repository organizată conform cerințelor.
  - [x] Script de generare date implementat și rulat (1000 mostre).
  - [x] Pipeline de preprocesare (scalare + split) funcțional.
  - [x] Model Rețea Neuronală implementat și antrenat.
  - [x] Modul de predicție și optimizare (Toolbox) funcțional.
  - [x] Documentație completată.


```
```
