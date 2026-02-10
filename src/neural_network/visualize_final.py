import matplotlib.pyplot as plt
import pandas as pd
import torch
import joblib
import json
import os
import sys
import numpy as np

# Path fix
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path: sys.path.insert(0, project_root)

from src.neural_network.model_regression import CNCModel

def analyze_performance():
    config_path = os.path.join(project_root, 'config', 'settings.json')
    with open(config_path, 'r') as f: config = json.load(f)
    
    # Load Test Data
    test_data = pd.read_csv(os.path.join(project_root, config['data_test']), header=None).values
    X_test = torch.FloatTensor(test_data[:, :-1])
    y_test_scaled = test_data[:, -1]
    
    # --- ÎNCĂRCARE MODEL OPTIMIZAT ---
    # Încercăm să încărcăm cu 128 neuroni (dacă a câștigat Exp 3) sau 64 (standard)
    # Pentru a fi siguri, verificăm mărimea fișierului sau încercăm ambele
    try:
        model = CNCModel(config['input_size'], 128, config['output_size'])
        model.load_state_dict(torch.load(os.path.join(project_root, 'models', 'optimized_model.pkl')))
        print("Încărcat model cu 128 neuroni.")
    except:
        model = CNCModel(config['input_size'], 64, config['output_size'])
        model.load_state_dict(torch.load(os.path.join(project_root, 'models', 'optimized_model.pkl')))
        print("Încărcat model cu 64 neuroni.")

    model.eval()
    
    # Predict
    with torch.no_grad():
        preds_scaled = model(X_test).numpy().flatten()
        
    # Unscale (sa vedem microni reali)
    scaler_y = joblib.load(os.path.join(project_root, config['scaler_y']))
    y_real = scaler_y.inverse_transform(y_test_scaled.reshape(-1, 1)).flatten()
    y_pred = scaler_y.inverse_transform(preds_scaled.reshape(-1, 1)).flatten()
    
    # --- 1. GENERARE GRAFIC (Confusion Matrix Equivalent) ---
    plt.figure(figsize=(8, 8))
    plt.scatter(y_real, y_pred, alpha=0.6, c='blue', edgecolors='k')
    plt.plot([min(y_real), max(y_real)], [min(y_real), max(y_real)], 'r--', lw=2, label='Ideal')
    plt.title(f"Performanță Model Optimizat (Predicție vs Real)")
    plt.xlabel("Rugozitate Reală (Ra µm)")
    plt.ylabel("Rugozitate Prezisa (Ra µm)")
    plt.legend()
    plt.grid(True)
    
    save_plot = os.path.join(project_root, 'docs', 'confusion_matrix_optimized.png')
    plt.savefig(save_plot)
    print(f"Grafic salvat: {save_plot}")
    
    # --- 2. ANALIZA TOP 5 ERORI ---
    errors = np.abs(y_real - y_pred)
    df_errors = pd.DataFrame({
        'Real_Ra': y_real,
        'Pred_Ra': y_pred,
        'Eroare_Abs': errors
    })
    
    top5 = df_errors.sort_values(by='Eroare_Abs', ascending=False).head(5)
    print("\n TOP 5 ERORI MAJORE:")
    print(top5)
    
    top5.to_csv(os.path.join(project_root, 'results', 'top5_errors.csv'), index=False)

if __name__ == "__main__":
    analyze_performance()