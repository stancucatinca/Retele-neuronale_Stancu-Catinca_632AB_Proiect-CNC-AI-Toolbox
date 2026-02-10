# README – Etapa 3: Analiza și Pregătirea Setului de Date pentru Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Stancu Catinca Stefania   
**Proiect:** CNC-AI Toolbox – Predicția Rugozității Ra

---

## Introducere
Această etapă marchează fundamentul sistemului inteligent, axându-se pe identificarea unei nevoi reale în industria prelucrărilor prin așchiere: dificultatea operatorilor de a alege parametrii tehnologici optimi (viteză, avans, adâncime) pentru a garanta calitatea suprafeței ($R_a$). Obiectivul principal al acestei etape a fost generarea, analiza și preprocesarea unui set de date care să permită ulterior antrenarea unui model de rețea neuronală robust.

## 1. Structura Repository-ului Github (Versiunea Etapei 3)
În această fază a proiectului, structura este concentrată pe modulele de achiziție și preprocesare a datelor:

```text
cnc-ai-toolbox/
├── data/
│   ├── raw/
│   │   └── dataset_simulare.csv    # Datele brute rezultate din simulator
│   ├── processed/
│   │   ├── scaler_x.pkl            # Obiect de normalizare pentru intrări
│   │   └── scaler_y.pkl            # Obiect de normalizare pentru ieșire
│   ├── train/                      # Subset antrenare (70%)
│   ├── validation/                 # Subset validare (15%)
│   └── test/                       # Subset testare (15%)
├── docs/
│   └── etapa3_analiza_date.md      # Documentația curentă
├── src/
│   ├── data_acquisition/
│   │   └── generate_simulation.py  # Script generare date originale
│   └── preprocessing/
│       └── preprocess.py           # Script curățare și scalare
└── requirements.txt                # Biblioteci necesare (pandas, scikit-learn)

---

##  2. Descrierea Setului de Date

### 2.1 Sursa datelor

* **Origine:** Datele sunt sintetice și au fost generate folosind scriptul `src/data_acquisition/generate_simulation.py`.
* **Modul de achiziție:** Generarea s-a bazat pe formula teoretică a rugozității ($R_a \approx f^2 / (8 \cdot R)$), unde $f$ este avansul și $R$ este raza vârfului sculei.

### 2.2 Caracteristicile dataset-ului

* **Număr total de observații:** Setul cuprinde 1000 de observații (rânduri).
* **Număr de caracteristici (features):** 5 caracteristici de intrare
* **Tipuri de date:** Numerice, Categoriale 
* **Format fișiere:** CSV

### 2.3 Descrierea fiecărei caracteristici

| **Caracteristică** | **Tip** | **Unitate** | **Descriere** | **Domeniu valori** |
|-------------------|---------|-------------|---------------|--------------------|
| **Viteza (V)** | numeric | m/min | Viteza de așchiere a procesului | 50–250 |
| **Avans (f)** | numeric | mm/rot | Avansul pe rotație al sculei | 0.05–0.4 |
| **Adâncime (ap)** | numeric | mm | Adâncimea de așchiere (pătrunderea) | 0.5–3.0 |
| **Diametru (D)** | numeric | mm | Diametrul sculei utilizate | 10–50 |
| **Material** | categorial | – | Tipul materialului piesei | {Oțel, Aluminiu, Fontă} |
| **Ra (Target)** | numeric | µm | Rugozitatea suprafeței rezultate | 0.4–6.5 |

**Fișier recomandat:**  `data/README.md`

---

##  3. Analiza Exploratorie a Datelor (EDA) – Sintetic

### 3.1 Statistici descriptive aplicate

Pentru a înțelege distribuția și variabilitatea datelor generate, s-au calculat principalele metrici statistice pentru variabilele numerice:

* **Medie, mediană, deviație standard:** S-a observat că parametrii tehnologici ($V, f, a_p$) urmează o distribuție uniformă în intervalele setate, în timp ce deviația standard a rugozității ($R_a$) reflectă impactul zgomotului gaussian adăugat.
* **Min–max și quartile:** Valorile rugozității variază între 0.4 µm (finisare) și 6.5 µm (degroșare), acoperind o gamă largă de aplicații industriale.
* **Distribuții pe caracteristici (histograme):** Vizualizarea prin histograme confirmă acoperirea echilibrată a spațiului parametrilor, asigurând că modelul va învăța uniform pe toate regimurile de așchiere.
* **Identificarea outlierilor (IQR / percentile):** Deoarece datele sunt generate prin simulare controlată, nu s-au identificat outlieri rezultați din erori de măsură, ci doar valori extreme fiziologice ale procesului de așchiere.

### 3.2 Analiza calității datelor

* **Detectarea valorilor lipsă:** Setul de date este complet (0% valori lipsă), integritatea fiind garantată de scriptul de generare.
* **Detectarea valorilor inconsistente sau eronate:** S-a verificat ca toate turațiile calculate (RPM) să fie pozitive și corelate logic cu viteza de așchiere și diametrul sculei.
* **Identificarea caracteristicilor redundant sau puternic corelate:** Matricea de corelație a indicat o legătură matematică puternică între Avans ($f$) și Rugozitate ($R_a$), confirmând modelul teoretic implementat.

### 3.3 Probleme identificate

* **Complexitatea Neliniară:** Relația dintre parametri nu este liniară (în special influența pătratică a avansului), ceea ce justifică utilizarea unei rețele neuronale de tip MLP în locul unei regresii liniare simple.
* **Zgomotul Gaussian:** Introducerea zgomotului de 0.05 a creat suprapuneri între zonele de tranziție ale rugozității, provocare pe care modelul RN va trebui să o gestioneze pentru a fi robust.
---

##  4. Preprocesarea Datelor

### 4.1 Curățarea datelor

* **Eliminarea duplicatelor:** S-a verificat integritatea setului de date generat prin simulator, nefiind identificate rânduri duplicate care să distorsioneze antrenarea.
* **Tratarea valorilor lipsă:** Deoarece datele sunt generate sintetic în mod controlat, nu există valori lipsă în dataset (0% missing values), deci nu a fost necesară imputarea cu mediană sau eliminarea de coloane.
* **Tratarea outlierilor:** S-a aplicat tehnica IQR pentru a asigura că zgomotul gaussian adăugat nu a produs valori în afara limitelor fizice acceptabile pentru parametrii de așchiere.

### 4.2 Transformarea caracteristicilor

* **Normalizare:** S-a utilizat tehnica **Standardizării (StandardScaler)** pentru trăsăturile numerice ($V, f, a_p, D$), aducând datele la medie 0 și deviație standard 1. Acest pas este critic pentru a asigura o pondere egală a caracteristicilor în calculul gradientului.
* **Encoding pentru variabile categoriale:** Variabila „Material” a fost transformată din format text în format numeric folosind **Label Encoding** (Oțel=0, Aluminiu=1, Fontă=2), permițând modelului matematic să proceseze informația despre material.
* **Ajustarea dezechilibrului de clasă:** Nu a fost necesară (ca în cazul SMOTE), deoarece simulatorul a fost programat să genereze un număr egal de mostre pentru fiecare tip de material.

### 4.3 Structurarea seturilor de date

**Împărțire respectată:**
* **70% – train (700 observații):** Utilizat pentru ajustarea ponderilor rețelei neuronale.
* **15% – validation (150 observații):** Utilizat pentru monitorizarea performanței în timpul antrenării și prevenirea overfitting-ului.
* **15% – test (150 observații):** Rezervat exclusiv pentru evaluarea finală, neîrtâlnit de model în timpul învățării.

**Principii respectate:**
* **Fără scurgere de informație (data leakage):** Statisticile pentru scalare (medie, std) au fost calculate DOAR pe setul de train și apoi aplicate pe seturile de validare și test.

### 4.4 Salvarea rezultatelor preprocesării

* **Date preprocesate:** Fișierele sunt stocate în `data/processed/` sub formă de obiecte `.pkl` (scalerele).
* **Seturi train/val/test:** Sunt salvate ca fișiere CSV individuale în folderele `data/train/`, `data/validation/` și `data/test/`.
* **Parametrii de preprocesare:** Obiectele `scaler_x.pkl` și `scaler_y.pkl` sunt arhivate pentru a fi utilizate ulterior în faza de inferență a aplicației.

---

##  5. Fișiere Generate în Această Etapă

În urma finalizării proceselor de achiziție și preprocesare din această etapă, au fost generate și structurate următoarele fișiere:

* **data/raw/** – Conține fișierul `dataset_simulare.csv` cu datele brute rezultate din simulatorul de așchiere.
* **data/processed/** – Conține fișierele de tip `.pkl` (scalerele salvate) și datele transformate gata de utilizare.
* **data/train/, data/validation/, data/test/** – Conțin seturile finale de date repartizate conform strategiei de split (70/15/15).
* **src/preprocessing/** – Găzduiește scriptul `preprocess.py` care execută automatizat întreg fluxul de curățare și transformare.
* **data/README.md** – Documentație detaliată a dataset-ului, incluzând unitățile de măsură și descrierea tehnică a fiecărui feature.



---

##  6. Stare Etapă (de completat de student)

Această secțiune monitorizează progresul realizat în cadrul Etapei 3 pentru proiectul CNC-AI Toolbox:

- [x] **Structură repository configurată**: Folderele `data` și `src` sunt organizate modular conform arhitecturii proiectului.
- [x] **Dataset analizat (EDA realizată)**: Statisticile descriptive și corelațiile dintre parametrii de așchiere au fost validate.
- [x] **Date preprocesate**: Scalarea și label encoding-ul au fost aplicate cu succes pe datele de intrare.
- [x] **Seturi train/val/test generate**: Datele au fost salvate în subseturi separate pentru a asigura o evaluare obiectivă.
- [x] **Documentație actualizată**: README-ul principal și fișierul de descriere a datelor reflectă realitatea tehnică a Etapei 3.

---
