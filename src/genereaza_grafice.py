import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# --- Configurare Căi ---
# 1. Unde sunt eu acum? (în folderul 'src')
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Urcăm UN SINGUR nivel pentru a ajunge în 'RN' (root)
# (src -> RN)
project_root = os.path.abspath(os.path.join(current_dir, '..'))

print(f"DEBUG: Directorul proiectului detectat este: {project_root}")

# Cai Fisiere Intrare
data_path_raw = os.path.join(project_root, 'data', 'raw', 'dataset_simulare.csv')
data_path_history = os.path.join(project_root, 'results', 'training_history.csv')

# Cai Salvare Imagini
save_dir_dataset = os.path.join(project_root, 'docs', 'datasets', 'figures')
save_dir_docs = os.path.join(project_root, 'docs')

# Asigură-te că există folderele de salvare
os.makedirs(save_dir_dataset, exist_ok=True)
os.makedirs(save_dir_docs, exist_ok=True)

# ==========================================
# PARTEA 1: Grafice Analiză Date (EDA)
# ==========================================
if os.path.exists(data_path_raw):
    print("--- Generare Grafice Dataset (EDA) ---")
    try:
        df = pd.read_csv(data_path_raw)

        # 1. Histograma Ra
        plt.figure(figsize=(8, 5))
        sns.histplot(df['Ra'], bins=30, kde=True, color='blue')
        plt.title('Distribuția Rugozității (Ra) în Dataset')
        plt.xlabel('Rugozitate Ra (µm)')
        plt.ylabel('Frecvență')
        save_path = os.path.join(save_dir_dataset, 'distributie_Ra.png')
        plt.savefig(save_path)
        print(f"Generat: {save_path}")
        plt.close()

        # 2. Heatmap Corelații
        plt.figure(figsize=(8, 6))
        # Selectăm doar coloane numerice pentru corelație
        numeric_df = df.select_dtypes(include=['float64', 'int64'])
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Matricea de Corelație a Parametrilor')
        save_path = os.path.join(save_dir_dataset, 'heatmap_corelatii.png')
        plt.savefig(save_path)
        print(f"Generat: {save_path}")
        plt.close()

        # 3. Scatter Plot (Avans vs Ra)
        plt.figure(figsize=(8, 5))
        sns.scatterplot(x='f', y='Ra', data=df, hue='work_material', palette='deep')
        plt.title('Relația dintre Avans (f) și Rugozitate (Ra)')
        plt.xlabel('Avans f (mm/rot)')
        plt.ylabel('Rugozitate Ra (µm)')
        save_path = os.path.join(save_dir_dataset, 'relatie_f_Ra.png')
        plt.savefig(save_path)
        print(f"Generat: {save_path}")
        plt.close()
    except Exception as e:
        print(f"Eroare la generarea graficelor EDA: {e}")
else:
    print(f"ATENȚIE: Nu am găsit {data_path_raw}. Graficele EDA nu au fost generate.")

# ==========================================
# PARTEA 2: Grafic Antrenare Model (Loss Curve)
# ==========================================
if os.path.exists(data_path_history):
    print("\n--- Generare Grafic Antrenare (Loss Curve) ---")
    try:
        history_df = pd.read_csv(data_path_history)
        
        plt.figure(figsize=(10, 6))
        plt.plot(history_df['epoch'], history_df['train_loss'], label='Antrenare (Train Loss)', linewidth=2)
        plt.plot(history_df['epoch'], history_df['val_loss'], label='Validare (Validation Loss)', linestyle='--', linewidth=2)
        
        plt.title('Curba de Învățare - Regresie Ra', fontsize=14)
        plt.xlabel('Epoci', fontsize=12)
        plt.ylabel('Eroare (MSE)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Salvăm direct în folderul docs (așa cum cere Etapa 5)
        save_path = os.path.join(save_dir_docs, 'loss_curve.png')
        plt.savefig(save_path)
        print(f"Generat: {save_path}")
        plt.close()
    except Exception as e:
        print(f"Eroare la generarea curbei de învățare: {e}")
else:
    print(f"ATENȚIE: Nu am găsit {data_path_history}. Rulează întâi 'train_model.py'!")

print("\nToate operațiunile grafice finalizate.")