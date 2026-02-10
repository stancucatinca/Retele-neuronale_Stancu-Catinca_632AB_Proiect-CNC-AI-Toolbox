#  README – Etapa 5: Configurarea și Antrenarea Modelului RN

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Stancu Catinca Stefania   
**Proiect:** CNC-AI Toolbox – Predicția Rugozității Ra
---

## Scopul Etapei 5

Această etapă marchează antrenarea efectivă a modelului de tip MLP (Multi-Layer Perceptron) definit anterior. Am trecut de la un model "dummy" (cu greutăți aleatorii) la un sistem capabil să prezică rugozitatea suprafeței ($R_a$) cu o precizie ridicată, bazându-se pe parametrii tehnologici de așchiere.

---

## PREREQUISITE – Verificare Etapa 4

- [x] **State Machine** definit în `docs/state_machine.jpg` (Idle -> Acquire -> Preprocess -> Inference -> Decision -> Output).
- [x] **Contribuție 100% date originale** în `data/raw/dataset_simulare.csv`.
- [x] **Modul 1 (Data Logging)** funcțional - generator de simulare fizică.
- [x] **Modul 2 (RN)** definit în PyTorch (Arhitectură 5 -> 64 -> 64 -> 1).
- [x] **Modul 3 (UI)** funcțional (Streamlit).
---

## Pregătire Date pentru Antrenare 

Deoarece dataset-ul a fost finalizat în Etapa 4, am procedat la reprocesarea completă pentru a asigura consistența:
1. **Combinare:** S-au utilizat cele 1000 de instanțe originale.
2. **Split:** Datele au fost împărțite în:
   - **70% Train** (700 probe)
   - **15% Validation** (150 probe)
   - **15% Test** (150 probe)
3. **Normalizare:** S-a utilizat `StandardScaler` pentru toate caracteristicile numerice ($V, f, a_p, D$), parametrii fiind salvați în `data/processed/scaler_x.pkl`.

## Nivel 1 

### 1. Detalii Antrenare
Modelul a fost antrenat pe setul de 1000 de probe originale.
- **Epoci:** 200 (cu Early Stopping).
- **Batch size:** 32.

#### 2. Tabel Hiperparametri și Justificări

Modelul a fost antrenat respectând cerința de minimum 10 epoci și batch size între 8-32.

| **Hiperparametru** | **Valoare Aleasă** | **Justificare** |
|--------------------|-------------------|-----------------|
| Rata de învățare (Learning rate) | 0.001 | Valoare standard pentru Adam; permite o convergență stabilă fără a oscila periculos în jurul minimului. |
| Mărime batch (Batch size) | 32 | Compromis optim între stabilitatea gradientului și viteza de antrenare pentru cele 1000 de mostre. |
| Număr de epoci | 200 | Am setat un număr mare de epoci, dar am folosit *Early Stopping* pentru a opri antrenarea când `val_loss` nu mai scade. |
| Optimizator | Adam | Algoritm de optimizare adaptiv, ideal pentru probleme de regresie neliniară. |
| Funcția de pierdere (Loss) | MSE (Mean Squared Error) | Esențială pentru regresie; penalizează erorile mari de predicție a rugozității. |
| Funcții de activare | ReLU (straturi ascunse) | Permite rețelei să învețe relațiile complexe dintre avans/viteză și rugozitate. |

**Justificare detaliată batch size:**
Am ales `batch_size=32` deoarece avem $N=1000$ eșantioane. Această valoare asigură aproximativ 31 de iterații pe epocă. Aceasta oferă un echilibru între stabilitatea gradientului (evitând zgomotul specific batch-urilor foarte mici) și timpul de antrenare, permițând modelului să generalizeze bine pe setul de validare.

### 3. Metrici calculate pe test set
Fiind o problemă de regresie, am calculat indicatorii de eroare:
- **$R^2$ Score (Acuratețea regresiei):** **0.958** (Depășește pragul de 0.65).
- **MAE (Eroare Medie Absolută):** **0.095 µm** (Indică o precizie extremă sub-micron).
- **MSE:** **0.021**.

### 4. Salvare model
Modelul antrenat a fost salvat în folderul `models/` sub numele:
- **`models/model_v1.pkl`** (Modelul principal antrenat).
- **`models/model_config.json`** (Configurația arhitecturii).

---

**Resurse învățare rapidă:**
- Împărțire date: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html (video 3 min: https://youtu.be/1NjLMWSGosI?si=KL8Qv2SJ1d_mFZfr)  
- Antrenare simplă Keras: https://keras.io/examples/vision/mnist_convnet/ (secțiunea „Training”)  
- Antrenare simplă PyTorch: https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html#training-an-image-classifier (video 2 min: https://youtu.be/ORMx45xqWkA?si=FXyQEhh0DU8VnuVJ)  
- F1-score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html (video 4 min: https://youtu.be/ZQlEcyNV6wc?si=VMCl8aGfhCfp5Egi)


---

## Nivel 2 

1. **Early Stopping:** Antrenarea s-a oprit automat după ce eroarea de validare nu s-a mai îmbunătățit timp de 15 epoci.
2. **Grafic Loss:** Salvat în `docs/loss_curve.png`. Curba arată o scădere asimptotică sănătoasă, fără divergență între train și validation. Curba se genereaza la rularea `src/genereaza_grafice.py`.
3. **Analiză erori context industrial:**

### 1. Unde greșește cel mai mult modelul?
Modelul are erori ușor mai mari în zona rugozităților foarte mici ($R_a < 10 \mu m$), unde zgomotul gaussian de simulare (vibrațiile) are un impact procentual mai mare asupra semnalului util.

### 2. Ce caracteristici cauzează erori?
Combinațiile de turație foarte mare și avans minim tind să genereze erori mai mari, deoarece relația fizică devine puternic neliniară în acele puncte.

### 3. Ce implicații are pentru aplicația industrială?
- **Subestimarea $R_a$:** Eroare critică. Piesa trece de simulare dar este rebutată fizic.
- **Supraestimarea $R_a$:** Eroare "safe". Productivitate ușor redusă, dar piesa este conformă.

---

## Verificare Consistență cu State Machine

În interfața aplicației, fluxul respectă diagrama definită:
1. **IDLE:** Așteptare parametri material.
2. **PREPROCESS:** Aplicare `StandardScaler`.
3. **INFERENCE:** Încărcare model **`models/model_v1.pkl`** și calcul $R_a$.
4. **DECISION:** Filtrare soluții conform pragurilor de rugozitate și turație.
5. **OUTPUT:** Afișare rezultate (Inference reală).

**Screenshot inferență reală:** `docs/screenshots/inference_real.png`

---

## Structura Repository-ului la Finalul Etapei 5


```text
proiect-rn-stancu-catinca/
├── etapa3_analiza_date.md         # Documentație Etapa 3
├── etapa4_arhitectura_SIA.md      # Documentație Etapa 4
├── etapa5_antrenare_model.md      # Documentația curentă (Etapa 5)
├── README.md                      # Overview general proiect (Actualizat)
│
├── docs/
│   ├── state_machine.png          # Diagrama fluxului logic (Etapa 4)
│   ├── loss_curve.png             # NOU - Graficul MSE/Loss din antrenare
│   ├── datasets/
│   │   ├── README.md
│   │   ├── dataset_description.md
│   │   ├── schema_dataset.png
│   │   └── figures/
│   │       ├── distributie_Ra.png # Histograma rugozității
│   │       ├── heatmap_corelati.png # Matricea de corelație
│   │       └── relatie_f_Ra.png   # Scatter plot Avans vs Ra
│   └── screenshots/
│       └── inference_real.png     # Screenshot predicție reală 
│
├── data/
│   ├── raw/
│   │   └── dataset_simulare.csv   # Dataset 100% original
│   ├── processed/
│   │   └── scaler_x.pkl           # StandardScaler salvat (Actualizat)
│   ├── train/ 
│   ├── validation/ 
│   └── test/                      # Split-urile de date (Actualizate)
│
├── models/
│   ├── model_config.json          # Configurația arhitecturii RN
│   └── model_v1.pkl               # NOU - Modelul antrenat (Etapa 5)
│
├── results/                       # NOU - Folder rezultate antrenare
│   ├── training_history.csv       # OBLIGATORIU - Log-ul erorii pe epoci
│   └── final_metrics.json          # Metrici finale (R2, MSE, MAE)
│
├── src/
│   ├── data_acquisition/
│   │   └── generate_simulation.py # Modulul 1
│   ├── preprocessing/
│   │   └── preprocess.py           # Actualizat pentru dataset combinat
│   ├── neural_network/
│   │   ├── model_regression.py    # Modulul 2 (Definire)
│   │   ├── train_model.py               # NOU - Script antrenare
│   │   └── predict.py            # Script evaluare
│   └── app/
│       └── interface.py           # Modulul 3 (Actualizat cu model_v1.pkl)
│
├── requirements.txt               # Actualizat cu torch/tensorflow/etc.
└── genereaza_grafice.py           # Actualizat cu loss_curve

---

## Diferențe față de Etapa 4

Implementarea Etapei 5 a adus următoarele modificări structurale și funcționale sistemului SIA:

* **Modele:** În folderul `models/`, modelul neantrenat a fost înlocuit cu **`model_v1.pkl`**, care conține ponderile optimizate în urma procesului de învățare.
* **Rezultate:** A fost creat folderul **`results/`**, care stochează dovezile matematice ale antrenării: `training_history.csv` (evoluția erorii pe epoci) și `final_metrics.json` (performanța finală pe datele de test).
* **Cod Sursă:** Au fost adăugate scripturile **`train_model.py`** (pentru execuția antrenării).
* **Documentație Vizuală:** S-au generat fișierele **`loss_curve.png`** (pentru monitorizarea convergenței) și **`inference_real.png`** (demonstrația integrării modelului antrenat în interfața grafică).
* **Interfață (UI):** Scriptul `interface.py` a fost actualizat pentru a încărca modelul real, trecând de la o simplă prezentare vizuală la un sistem de inferență funcțional.

---

## Instrucțiuni de Utilizare (Etapa 5)

Această secțiune descrie pașii necesari pentru a reproduce procesul de antrenare și pentru a rula aplicația folosind modelul de inteligență artificială validat.

### Pasul 1: Pregătirea Mediului de Lucru
Asigurați-vă că toate bibliotecile necesare (PyTorch, Scikit-Learn, Pandas, Streamlit) sunt instalate:
```bash
pip install -r requirements.txt

### Pasul 2: Antrenarea Modelului RN
Rulați scriptul de antrenare pentru a genera ponderile optime ale rețelei. Acesta va prelucra datele din data/processed/ și va salva rezultatul în folderul models/:

Bash
python src/neural_network/train.py
Rezultat: Generarea fișierului models/model_v1.pkl și a istoricului results/training_history.csv.

### Pasul 3: Evaluarea Performanței și Generarea Metricilor
Rulați scriptul de evaluare pentru a verifica precizia modelului pe setul de date de test și pentru a genera graficele de performanță:

Bash
python src/neural_network/evaluate.py
Rezultat: Generarea fișierului results/test_metrics.json și a graficului docs/loss_curve.png.

### Pasul 4: Lansarea Interfeței Grafice (UI)
Porniți aplicația Streamlit. Aceasta este configurată să încarce automat modelul antrenat model_v1.pkl pentru a efectua inferențe reale:

Bash
streamlit run src/app/interface.py

---
