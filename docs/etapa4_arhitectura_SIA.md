# README – Etapa 4: Arhitectura Completă a Aplicației SIA bazată pe Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Stancu Catinca Stefania
**Link Repository GitHub**: https://github.com/stancucatinca/Retele-neuronale_Stancu-Catinca_632AB_Proiect-CNC-AI-Toolbox.git
---

### 1. Tabelul Nevoie Reală → Soluție SIA → Modul Software

| **Nevoie reală concretă** | **Cum o rezolvă SIA-ul vostru** | **Modul software responsabil** |
|---------------------------|--------------------------------|--------------------------------|
| Predicția rugozității suprafeței ($R_a$) pentru evitarea rebuturilor CNC | Rețea de regresie care estimează $R_a$ cu precizie ridicată înainte de prelucrarea fizică | `src/neural_network` + `src/app` |
| Optimizarea productivității (timp minim) | Algoritm de selecție Pareto care alege cel mai rapid regim ce respectă calitatea impusă | `src/app/interface.py` |
| Siguranța utilajului (Safe RPM) | Validarea automată a input-ului pentru a preveni depășirea limitelor mecanice ale mașinii | `src/app` (State Machine) |

---

### 2. Contribuția Originală la Setul de Date – MINIM 40% din Totalul Observațiilor Finale

### 2.1 Sinteză Contribuție
| Indicator | Valoare | Procent |
|:---|:---|:---|
| **Total observații finale (N)** | 1000 | 100% |
| **Observații originale (M)** | 1000 | **100%** |
| **Sursă date** | Simulare Fizică (Python) | Contribuție proprie |

### 2.2 Declarație obligatorie:

**Tipul contribuției:**
[x] Date generate prin simulare fizică  
[ ] Date achiziționate cu senzori proprii  
[ ] Etichetare/adnotare manuală  
[ ] Date sintetice prin metode avansate  

**Descriere detaliată:**
Datele au fost generate folosind scriptul `generate_simulation.py`, care implementează modelul matematic al rugozității teoretice în frezare ($R_a \approx f^2 / 8R$). Pentru a simula condiții industriale reale, am introdus un **zgomot gaussian** cu deviație standard de 0.05, care reprezintă factori precum vibrațiile mașinii, micro-ciobirile sculei și variațiile de duritate ale materialului.

Simularea a acoperit 1000 de puncte de lucru, variind randomizat parametrii tehnologici în intervale sigure: Viteza (50-250 m/min), Avansul (0.05-0.4 mm/rot) și Adâncimea (0.5-3.0 mm), pentru trei tipuri de materiale (Oțel, Aluminiu, Fontă). Acest dataset original permite rețelei neuronale să învețe nu doar o formulă, ci și modul în care zgomotul procesului afectează calitatea finală a piesei.

**Locația codului:** `src/data_acquisition/generate_simulation.py`  
**Locația datelor:** `data/raw/dataset_simulare.csv`  

**Dovezi:**

Graficele de mai jos sunt generate prin scriptul `src/genereaza_grafice.py` și validează calitatea setului de date original:
- **Heatmap Corelații (`docs/heatmap_corelatii.png`)**: Confirmă ponderile parametrilor în predicția rugozității.
- **Distribuția Rugozității (`docs/distributie_RA.png`)**: Demonstrează acoperirea uniformă a regimurilor de lucru.
- **Validare Fizică (`docs/relatie_f_Ra.png`)**: Scatter plot care confirmă creșterea rugozității odată cu avansul, validând realismul datelor generate.

---

### 3. Diagrama State Machine a Întregului Sistem (OBLIGATORIE)

**Locație:** `docs/state_machine.png` (sau `.svg` / `.mermaid`)

### Justificarea State Machine-ului ales:

Am ales arhitectura de tip **control și decizie în timp real pentru procese industriale** deoarece proiectul nostru vizează predicția rugozității în așchiere, un domeniu unde succesiunea operațiilor și siguranța utilajului sunt critice. Într-un atelier CNC, nu se pot aplica parametri tehnologici fără o validare prealabilă, iar sistemul nostru inteligent reflectă acest flux logic prin stări bine definite.

Stările principale sunt:
1. **IDLE**: Aplicația așteaptă input-ul operatorului (Material, Diametru sculă, Rugozitate țintă) prin interfața Streamlit.
2. **ACQUIRE_DATA**: Sistemul generează automat un set de 2000 de candidați (combinații de $V$, $f$, $a_p$) în limitele tehnologice permise.
3. **PREPROCESS**: Datele brute sunt normalizate folosind `scaler_x.pkl` pentru a asigura compatibilitatea cu modelul MLP.
4. **INFERENCE**: Rețeaua neuronală (Modulul 2) procesează toți candidații și estimează rugozitatea rezultată ($R_a$).
5. **DECISION**: Filtrarea soluțiilor care respectă pragul de calitate și nu depășesc turația maximă (RPM) a mașinii.
6. **OUTPUT**: Identificarea și afișarea soluțiilor optime (Frontul Pareto) în interfața grafică.

Tranzițiile critice sunt:
- **IDLE → ACQUIRE_DATA**: Se declanșează când operatorul apasă butonul de calcul în UI.
- **DECISION → OUTPUT**: Are loc doar dacă există soluții care îndeplinesc criteriile de siguranță și calitate.
- **ORICE STARE → ERROR**: Se activează în cazul în care input-urile sunt invalide sau procesarea datelor eșuează.

Starea **ERROR** este esențială pentru că în mediul industrial pot apărea erori de comunicare sau date corupte (ex: valori de turație fizic imposibile). Trebuie să gestionăm aceste excepții pentru a preveni recomandarea unor parametri care ar putea duce la ruperea sculei sau rebutarea piesei.

Bucla de feedback funcționează astfel: rezultatul inferenței și validarea din starea DECISION permit reajustarea rapidă a scenariilor de așchiere până la găsirea optimului de producție.

---

### 4. Scheletul Complet al celor 3 Module

În această etapă, am dezvoltat și integrat structura funcțională a celor trei module fundamentale ale sistemului. Deși modelul rețelei neuronale nu este încă antrenat pentru precizie industrială, întreg pipeline-ul rulează "end-to-end": datele sunt generate, trecute prin arhitectura rețelei și afișate în interfața grafică.

| **Modul** | **Fișier / Tehnologie** | **Cerință minimă funcțională (Etapa 4)** |
|-----------|----------------------------------|----------------------------------------------|
| **1. Data Logging / Acquisition** | `src/data_acquisition/generate_simulation.py` | **REALIZAT:** Scriptul produce fișierul `dataset_simulare.csv` conținând 1000 de observații (100% originale), incluzând zgomotul gaussian calibrat. |
| **2. Neural Network Module** | `src/neural_network/model_regression.py` | **REALIZAT:** Arhitectura MLP este definită în PyTorch (5 → 64 → 64 → 1). Modelul poate fi instanțiat, compilat și salvat sub formă de fișier `.pkl`. |
| **3. Web Service / UI** | `src/app/interface.py` | **REALIZAT:** Aplicația Streamlit pornește fără erori, permite utilizatorului să selecteze materialul/rugozitatea și afișează un tabel de rezultate simulate. |

#### Detalii per modul:

#### **Modul 1: Data Logging / Acquisition**
- **Funcționare:** Scriptul utilizează bibliotecile `numpy` și `pandas` pentru a genera seturi de date bazate pe modelele fizice de așchiere.
- **Dovada originalității:** Codul generează automat datele în folderul `data/raw/`, asigurând independența de seturi de date publice.
- **Parametri:** Simularea folosește intervale de viteză $V \in [50, 250]$ și avans $f \in [0.05, 0.4]$, cu un zgomot de $0.05$ pentru realism.


#### **Modul 2: Neural Network Module**
- **Arhitectură:** S-a ales un model de tip Regresie (MLP) deoarece target-ul nostru ($R_a$) este o valoare continuă. 
- **Justificare:** Cele două straturi ascunse cu funcție de activare ReLU permit modelarea interacțiunilor neliniare dintre avans și material.
- **Status:** Modelul primește un tensor de intrare $[1, 5]$ și returnează o valoare scalară, demonstrând integritatea fluxului de calcul.

#### **Modul 3: Web Service / UI**
- **Interacțiune:** Interfața este construită pentru a fi utilizată direct în atelier. Operatorul alege materialul dintr-un meniu drop-down și setează rugozitatea dorită.
- **Screenshot demonstrativ:** Disponibil în `docs/screenshots/inference_real.png`.
- **Lansare:** Aplicația se pornește cu comanda `streamlit run src/app/interface.py`.

**Scop realizat:** Am demonstrat că pipeline-ul tehnic funcționează complet: input user → preprocesare → model (neantrenat) → output tabelar.


## Structura Repository-ului la Finalul Etapei 4 

**Verificare consistență cu Etapa 3:**

```text
cnc-ai-toolbox/
├── data/
│   ├── raw/
│   │   └── dataset_simulare.csv    # Date originale (100% contribuție proprie)
│   ├── processed/
│   │   ├── scaler_x.pkl            # Salvare stare StandardScaler (Etapa 3)
│   │   └── scaler_y.pkl
│   ├── train/
│   ├── validation/
│   └── test/
├── src/
│   ├── data_acquisition/
│   │   └── generate_simulation.py  # MODUL 1: Generatorul de date
│   ├── preprocessing/
│   │   └── preprocess.py           # Logica de procesare (Etapa 3)
│   ├── neural_network/
│   │   └── model_regression.py     # MODUL 2: Arhitectura MLP PyTorch
│   ├── app/
│   │   └── interface.py            # MODUL 3: Interfața Streamlit (Schelet)
│   └── genereaza_grafice.py        # Script pentru vizualizări
├── docs/
│   ├── state_machine.png           # Diagrama logică obligatorie
│   ├── heatmap_corelatii.png       # Analiză corelații 
│   ├── distributie_RA.png          # Distribuția datelor 
│   ├── relatie_f_Ra.png            # Validare fizică
│   ├── etapa3_analiza_date.md         # Documentație Etapa 3
│   ├── etapa4_arhitectura_SIA.md      # Documentație Etapa 4
│   └── screenshots/
│       └── inference_real.png             # Captură de ecran cu interfața pornită
├── models/
│   └── model_v1.pkl                # Model neantrenat salvat pentru testare
├── config/
│   └── settings.json               # Configurații proiect
├── README.md                       # Overview general
├── docs/etapa3_analiza_date.md      # Documentația Etapa 3
├── docs/etapa4_arhitectura_SIA.md  # Acest fișier completat
└── requirements.txt                # Dependențe (torch, streamlit, pandas etc.)
```
**Diferențe față de Etapa 3:**
- Adăugat `data/raw/dataset_simulare.csv` – Reprezintă contribuția originală de 100% (generată prin simulare proprie).
- Adăugat `src/data_acquisition/generate_simulation.py` – **MODUL 1**: Scriptul responsabil pentru generarea datelor.
- Adăugat `src/neural_network/model_regression.py` – **MODUL 2**: Definirea arhitecturii modelului MLP (neantrenat).
- Adăugat `src/app/interface.py` – **MODUL 3**: Logica aplicației și interfața Streamlit.
- Adăugat `src/genereaza_grafice.py` – Scriptul utilizat pentru generarea vizualizărilor EDA și a curbelor de învățare.
- Adăugat folderul `docs/datasets/figures/` – Locația unde sunt salvate cele 3 grafice de analiză a datelor.
- Adăugat `docs/state_machine.png` – **OBLIGATORIU**: Diagrama de stări a întregului sistem.
- Adăugat `docs/screenshots/inference_real.png ` – Captură de ecran care demonstrează funcționarea scheletului UI.

---

## Checklist Final 

### Documentație și Structură
- [x] Tabelul Nevoie → Soluție → Modul completat cu exemple concrete din industria CNC.
- [x] Declarație contribuție originală (100% date originale) completată în README.
- [x] Cele 3 grafice EDA (`distributie_Ra`, `heatmap`, `relatie_f_Ra`) sunt generate și salvate în `docs/datasets/figures/`.
- [x] Diagrama State Machine creată și salvată în `docs/state_machine.png`.
- [x] Legendă State Machine scrisă (justificarea stărilor pentru procesul industrial).
- [x] Repository structurat conform modelului SIA (modulele 1, 2 și 3 organizate în `src/`).

### Modul 1: Data Logging / Acquisition
- [x] Codul rulează fără erori: `python src/data_acquisition/generate_simulation.py`.
- [x] Produce integral datele originale (1000 eșantioane) în format CSV.
- [x] CSV generat în format compatibil cu scriptul de preprocesare din Etapa 3.
- [x] Documentație inclusă: Metoda de simulare și zgomotul gaussian sunt explicate.

### Modul 2: Neural Network
- [x] Arhitectură RN (Regresie MLP) definită în PyTorch și documentată prin comentarii în cod.
- [x] Modelul poate fi instanțiat și salvat în folderul `models/` (chiar dacă este neantrenat).
- [x] README în `src/neural_network/` cu detaliile arhitecturii alese.

### Modul 3: Web Service / UI
- [x] Interfața Streamlit pornește fără erori: `streamlit run src/app/interface.py`.
- [x] Screenshot demonstrativ salvat în `docs/screenshots/inference_real.png `.
- [x] Pipeline-ul end-to-end funcționează: Input User -> Predictie -> Afișare.

---

**Predarea se face prin commit pe GitHub cu mesajul:** `"Etapa 4 completă - Arhitectură SIA funcțională"`

**Tag obligatoriu:** `git tag -a v0.4-architecture -m "Etapa 4 - Skeleton complet SIA"`



