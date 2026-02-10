# README – Etapa 6: Analiza Performanței, Optimizarea și Concluzii Finale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Stancu Catinca Stefania, Grupa 632AB  
**Link Repository GitHub:** https://github.com/stancucatinca/Retele-neuronale_Stancu-Catinca_632AB_Proiect-CNC-AI-Toolbox.git  
**Data predării:** 09.02.2026

---

## Scopul Etapei 6

Această etapă marchează maturizarea completă a Sistemului cu Inteligență Artificială (SIA). Obiectivul principal a fost optimizarea modelului de regresie pentru predicția rugozității ($R_a$) și transformarea aplicației dintr-un simplu instrument de predicție într-un sistem de suport decizional prin implementarea **optimizării Pareto**.

---

## PREREQUISITE – Verificare Etapa 5 (VALIDAT)

- [x] **Model antrenat** salvat în `models/model_v1.pkl`
- [x] **Metrici baseline** raportate: $R^2$ Score $\approx$ 0.95
- [x] **UI funcțional** care încarcă modelul antrenat și face inferență reală
- [x] **State Machine** implementat pentru filtrarea logică a parametrilor

---

## 1. Experimente de Optimizare și Selecție Model Final

Am rulat un proces sistematic de tip Grid Search pentru a identifica configurația care maximizează precizia și stabilitatea predicției.

| **Exp#** | **Modificare față de Baseline (Etapa 5)** | **$R^2$ Score** | **MSE (Eroare)** | **Timp antrenare** | **Observații** |
|----------|------------------------------------------|--------------|--------------|-------------------|----------------|
| Baseline | Configurația din Etapa 5 (Batch 32) | 0.9973 | 0.0025 | ~2 min | Referință stabilă |
| Exp 1 | Learning rate 0.01 → 0.001 | 0.9567 | 0.0407 | ~3 min | Convergență mai lentă |
| Exp 2 | Arhitectură: 64 → 128 Neuroni | 0.9982 | 0.0016 | ~4 min | Precizie ridicată, risc de overfitting |
| **Exp 3** | **Batch size 32 → 64** | **0.9986** | **0.0013** | **~2 min** | **BEST - Ales pentru varianta finală** |

**Justificare alegere configurație finală:**
Am ales **Exp 3** (Batch Size 64) deoarece a oferit cel mai mare scor $R^2$ (0.9986) și cea mai mică eroare medie pătratică (MSE). Creșterea batch size-ului a stabilizat procesul de învățare (gradient descent mai lin), reducând oscilațiile funcției de loss în ultimele epoci. Modelul a fost salvat ca `models/optimized_model.pkl`.

---

## 2. Actualizarea Aplicației Software în Etapa 6

Am transformat pipeline-ul de date pentru a permite o decizie multicriterială (Viteză vs. Calitate).

### Tabel Modificări Aplicație Software

| **Componenta** | **Stare Etapa 5** | **Modificare Etapa 6** | **Justificare** |
|----------------|-------------------|------------------------|-----------------|
| **Model încărcat** | `model_v1.pkl` | `optimized_model.pkl` | Creștere de precizie ($R^2$ de la 0.95 la 0.99) |
| **Configurare** | Hardcoded în cod | Fișier `model_config.json` | Permite citirea dinamică a arhitecturii modelului |
| **Funcționalitate** | Predicție punctuală | **Optimizare Pareto** | Utilizatorul primește Top 5 soluții care minimizează timpul și rugozitatea |
| **Vizualizare** | Text/Tabele simple | Scatter Plot Pareto | Vizualizarea clară a compromisului (trade-off) între viteză și calitate |
| **Lansare** | Streamlit manual | Script `run_proiect.bat` | Lansare "One-Click" pentru utilizatorii din mediul industrial |



### Diagrama State Machine Actualizată
Fluxul logic a fost extins pentru a include starea de optimizare:
`INPUT` → `GENERATE_SCENARIOS` (2000 probe) → `INFERENCE` (RN) → `FILTER_LOGIC` (Threshold $R_a$ + Limită RPM) → `OPTIMIZE_PARETO` → `OUTPUT`.

---

## 3. Analiza Detaliată a Performanței

### 3.1 Interpretare Rezultate (Regression "Confusion Matrix")
**Locație:** `docs/confusion_matrix_optimized.png`

Analiza graficului de corelație între valorile reale și cele prezise indică:
- **Liniaritate:** Aliniere excelentă pe diagonala ideală ($R^2 = 0.9986$), ceea ce confirmă că modelul a învățat corect relația fizică dintre avans ($f$) și rugozitate ($R_a$).
- **Corelație:** Parametrul "Avans ($f$)" prezintă o corelație de **0.85** cu rugozitatea, fiind cel mai critic factor învățat de rețea.

### 3.2 Analiza a 5 Exemple Greșite (Top Errors)
Am analizat cele mai mari deviații din setul de test (din `results/top5_errors.csv`):

| **Index** | **Real ($R_a$)** | **Predis ($R_a$)** | **Eroare Abs.** | **Cauză probabilă** | **Soluție propusă** |
|-----------|----------------|---------------|----------------|---------------------|---------------------|
| #112 | 3.20 µm | 3.05 µm | 0.15 | Zgomot gaussian ridicat în simulare | Filtrare outlieri la antrenare |
| #305 | 5.50 µm | 5.32 µm | 0.18 | Valori extreme (regim agresiv) | Utilizare `RobustScaler` în loc de Standard |
| #45 | 0.80 µm | 0.88 µm | 0.08 | Zonă de graniță (finisare extremă) | Augmentare date în zona $R_a < 1.0$ |
| #810 | 1.60 µm | 1.63 µm | 0.03 | Eroare neglijabilă | Model stabil în regim normal |
| #950 | 2.40 µm | 2.44 µm | 0.04 | Eroare neglijabilă | Model stabil în regim normal |

---

## 4. Agregarea Rezultatelor și Vizualizări

### 4.1 Tabel Sumar Rezultate Finale

| **Metrică** | **Etapa 4** | **Etapa 5** | **Etapa 6 (Final)** | **Target Industrial** | **Status** |
|-------------|-------------|-------------|-------------|----------------------|------------|
| Accuracy ($R^2$) | ~0.60 | 0.95 | **0.9986** | ≥ 0.90 | **DEPĂȘIT** |
| MSE (Eroare) | > 0.1 | 0.02 | **0.0013** | ≤ 0.05 | **DEPĂȘIT** |
| Latență inferență | 50ms | 40ms | **35ms** | ≤ 50ms | **OK** |

### 4.2 Vizualizări Obligatorii
- [x] **`confusion_matrix_optimized.png`**: Predicție vs Realitate (Scatter Plot).
- [x] **`loss_curve.png`**: Demonstrația convergenței fără overfitting.
- [x] **`screenshots/inference_optimized.png`**: Captură UI cu optimizarea Pareto funcțională.

---

## 5. Concluzii Finale și Lecții Învățate

### 5.1 Evaluarea Performanței Finale
Modelul optimizat atinge un scor $R^2$ de **0.9986**, ceea ce îl face extrem de fiabil pentru utilizarea în atelierele CNC. Implementarea algoritmului Pareto permite operatorului să aleagă un regim de așchiere care scade timpul de producție fără a risca depășirea rugozității impuse de desenul tehnic.

### 5.2 Limitări și Lecții Învățate
- **Limitări:** Modelul este antrenat pe date simulate. Deși am inclus zgomot gaussian pentru realism, pe o mașină fizică uzura sculei poate introduce variații neliniare neprevăzute în acest model.
- **Lecție tehnică:** Preprocesarea datelor și calibrarea zgomotului gaussian au avut un impact mai mare asupra realismului decât simpla adăugare de straturi neuronale.
- **Lecție proces:** Modularizarea codului prin utilizarea `model_config.json` a permis actualizarea rapidă a aplicației fără a rescrie logica interfeței Streamlit.

---

## Structura Repository-ului la Finalul Proiectului

```text
proiect-rn-[nume-prenume]/
│
├── README.md                       # ← ACEST FIȘIER (Documentația Principală)
├── requirements.txt                # Dependențe (PyTorch, Streamlit, Pandas)
├── run_proiect.bat                 # Script de lansare rapidă (Windows)
│
├── config/
│   └── settings.json               # Configurare globală (căi, hiperparametri)
│
├── data/
│   ├── raw/
│   │   └── dataset_simulare.csv    # Date brute generate (100% originale)
│   ├── processed/
│   │   ├── scaler_x.pkl            # Scaler salvat pentru input (StandardScaler)
│   │   └── scaler_y.pkl            # Scaler salvat pentru output (Ra)
│   ├── train/
│   │   └── train.csv               # Set antrenare (70%)
│   ├── validation/
│   │   └── validation.csv          # Set validare (15%)
│   └── test/
│       └── test.csv                # Set testare (15%)
│
├── docs/
│   ├── etapa3_analiza_date.md      # Documentație Etapa 3
│   ├── etapa4_arhitectura_SIA.md   # Documentație Etapa 4
│   ├── etapa5_antrenare_model.md   # Documentație Etapa 5
│   ├── etapa6_optimizare_concluzii.md # Documentație Etapa 6
│   ├── datasets/                   # Descrieri suplimentare dataset
│   ├── state_machine_initial.png   # Diagrama stărilor aplicației initial
│   ├── state_machine.png           # Diagrama stărilor aplicației 
│   ├── confusion_matrix_optimized.png  # Grafic Performanță (Predicție vs Real)
│   ├── loss_curve.png              # Curba de învățare (Train vs Val Loss)
│   └── screenshots/
│       ├── inference_real.png      # Screenshot UI Etapa 5
│       ├── inference_optimized_1.png # Screenshot UI Final (Input)
│
├── models/
│   ├── model_v1.pkl                # Model Baseline (Etapa 5)
│   ├── optimized_model.pkl         # Model Final Optimizat (Etapa 6)
│   └── model_config.json           # Configurare dinamică a arhitecturii
│
├── reports/
│   ├── Raport_Optimizare_*.txt     # Raport text generat automat
│   └── Solutii_Pareto_*.csv        # Export soluții optime
│
├── results/
│   ├── training_history.csv        # Istoric loss pe epoci
│   ├── optimization_experiments.csv # Rezultate Grid Search
│   ├── final_metrics.json          # Metrici finale json
│   └── top5_errors.csv             # Analiza cazurilor cu eroare mare
│
└── src/
    ├── app/
    │   └── interface.py            # Interfața Grafică (Streamlit)
    ├── data_acquisition/
    │   └── generate_simulation.py  # Script generare date sintetice
    ├── preprocessing/
    │   └── preprocess.py           # Curățare, Scalare, Split
    ├── neural_network/
    │   ├── model_regression.py     # Clasa PyTorch MLP
    │   ├── train_model.py          # Script antrenare (Training Loop)
    │   ├── predict.py              # Logica predicție pe date noi
    │   ├── optimize.py             # Script optimizare (Grid Search)
    │   └── visualize_final.py      # Generare grafice
    └── genereaza_grafice.py        # Utilitar plotare