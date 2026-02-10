# Documentația Datelor - CNC-AI Toolbox

Acest director conține documentația detaliată și vizualizările aferente seturilor de date utilizate în proiect.

## Conținutul Folderului

*  **[dataset_description.md](./dataset_description.md)**: Dicționarul complet al datelor (descrierea coloanelor, tipuri de date, unități de măsură).
*  **[schema_dataset.png](./schema_dataset.png)**: O reprezentare vizuală a fluxului de date și a structurii tabelelor.
*  **`figures/`**: Conține grafice generate în etapa de Analiză Exploratorie (EDA), cum ar fi:
    * Distribuția rugozității ($R_a$).
    * Matricea de corelație (heatmap).
    * Scatter plots pentru relația Avans vs. Rugozitate.

## Locația Datelor Reale
Fișierele `.csv` propriu-zise se află în directorul `data/` din rădăcina proiectului:
* Date brute: `../../data/raw/dataset_simulare.csv`
* Date antrenare: `../../data/train/train.csv`
* Date testare: `../../data/test/test.csv`

## Mod de Generare
Datele sunt sintetice și au fost generate rulând scriptul:
`python src/data_acquisition/generate_simulation.py`