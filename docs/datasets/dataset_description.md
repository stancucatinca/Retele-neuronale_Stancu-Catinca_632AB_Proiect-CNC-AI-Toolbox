# Descrierea Setului de Date (Data Dictionary)

## 1. Prezentare Generală
Setul de date `dataset_simulare.csv` conține 1000 de înregistrări simulate care modelează procesul de frezare CNC. Aceste date sunt utilizate pentru a antrena o rețea neuronală capabilă să prezică rugozitatea suprafeței ($R_a$) pe baza parametrilor de așchiere.

* **Sursă:** Generat sintetic folosind scriptul `src/data_acquisition/generate_simulation.py`.
* **Format:** CSV (Comma Separated Values).
* **Dimensiune:** 1000 rânduri, 7 coloane.

## 2. Variabile (Coloane)

### Variabile de Intrare (Features - X)
Acestea sunt parametrii setați la mașina CNC:

| Nume Coloană | Tip Date | Unitate | Descriere Detaliată | Domeniu de Valori |
| :--- | :--- | :--- | :--- | :--- |
| **`V`** | `float` | m/min | **Viteza de așchiere.** Viteza periferică a sculei. Influențează temperatura și uzura. | $100.0 - 350.0$ |
| **`f`** | `float` | mm/rot | **Avansul.** Distanța parcursă de sculă la o rotație completă. Cel mai mare impact asupra $R_a$. | $0.05 - 0.35$ |
| **`ap`** | `float` | mm | **Adâncimea de așchiere.** Grosimea stratului de material îndepărtat. | $0.5 - 4.0$ |
| **`D`** | `int` | mm | **Diametrul sculei.** Dimensiunea frezei utilizate. | $\{10, 12, 16, 20\}$ |
| **`work_material`** | `int` | - | **Codul Materialului.** Codificarea tipului de material prelucrat. | `0` = Oțel<br>`1` = Aluminiu<br>`2` = Fontă |

### Variabile de Ieșire (Targets - y)
Acestea sunt rezultatele procesului:

| Nume Coloană | Tip Date | Unitate | Descriere Detaliată | Observații |
| :--- | :--- | :--- | :--- | :--- |
| **`Ra`** | `float` | µm | **Rugozitatea medie aritmetică.** Indicatorul principal de calitate a suprafeței. | Generat cu formula teoretică + zgomot gaussian. |
| **`timp`** | `float` | s | **Timpul de prelucrare.** Timpul necesar pentru a parcurge o lungime de referință $L=100mm$. | Calculat matematic: $T = \frac{L \cdot 60}{RPM \cdot f}$ |

## 3. Relații și Dependențe
Datele au fost generate respectând următoarele principii tehnologice:
1.  **$R_a \propto f^2$**: O creștere a avansului duce la o creștere exponențială a rugozității.
2.  **$R_a \propto 1/D$**: Un diametru mai mare al sculei tinde să reducă rugozitatea.
3.  **$V$ vs $R_a$**: Vitezele mai mari de așchiere tind să îmbunătățească ușor suprafața (reduc $R_a$).
4.  **Material**: Aluminiul (cod 1) obține cele mai bune suprafețe, urmat de Oțel (0) și Fontă (2).

---
**Notă:** Valorile sunt normalizate (scalate) înainte de a intra în rețeaua neuronală folosind `StandardScaler`, iar obiectele de scalare sunt salvate în `data/processed/`.