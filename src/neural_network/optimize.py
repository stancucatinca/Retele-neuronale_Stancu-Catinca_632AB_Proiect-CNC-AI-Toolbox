import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import json
import os
import sys
import copy
from sklearn.metrics import r2_score, mean_squared_error

# --- Configurare Căi ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.neural_network.model_regression import CNCModel

def run_experiment(exp_name, lr, batch_size, hidden_size, epochs=200):
    print(f"🚀 Rulare {exp_name} (LR={lr}, Batch={batch_size}, Hidden={hidden_size})...")
    
    # 1. Load Data
    config_path = os.path.join(project_root, 'config', 'settings.json')
    with open(config_path, 'r') as f: config = json.load(f)
    
    train_df = pd.read_csv(os.path.join(project_root, config['data_train']), header=None)
    test_df = pd.read_csv(os.path.join(project_root, config['data_test']), header=None)
    
    X_train = torch.FloatTensor(train_df.iloc[:, :-1].values)
    y_train = torch.FloatTensor(train_df.iloc[:, -1].values.reshape(-1, 1))
    X_test = torch.FloatTensor(test_df.iloc[:, :-1].values)
    y_test = torch.FloatTensor(test_df.iloc[:, -1].values.reshape(-1, 1))
    
    # 2. Setup Model
    model = CNCModel(config['input_size'], hidden_size, config['output_size'])
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    
    # 3. Training Loop Simplificat
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X_train) # Full batch pentru rapiditate in experiment
        loss = criterion(output, y_train)
        loss.backward()
        optimizer.step()
        
    # 4. Evaluare
    model.eval()
    with torch.no_grad():
        preds = model(X_test).numpy()
        real = y_test.numpy()
        
    r2 = r2_score(real, preds)
    mse = mean_squared_error(real, preds)
    
    return {
        "Nume": exp_name,
        "Learning Rate": lr,
        "Batch Size": batch_size,
        "Hidden Neurons": hidden_size,
        "R2 Score": round(r2, 4),
        "MSE": round(mse, 5),
        "Model_State": copy.deepcopy(model.state_dict())
    }

def main():
    experiments = []
    
    # --- DEFINIREA CELOR 4 EXPERIMENTE ---
    # Exp 1: Baseline (Configuratia veche)
    experiments.append(run_experiment("Exp 1 (Baseline)", 0.01, 32, 64))
    
    # Exp 2: Learning Rate mic (Fine Tuning)
    experiments.append(run_experiment("Exp 2 (Fine Tuning)", 0.001, 32, 64))
    
    # Exp 3: Arhitectură Complexă (Mai mulți neuroni)
    experiments.append(run_experiment("Exp 3 (Complex)", 0.005, 32, 128))
    
    # Exp 4: Batch Mare
    experiments.append(run_experiment("Exp 4 (Batch 64)", 0.01, 64, 64))
    
    # --- SALVARE REZULTATE TABEL ---
    results_df = pd.DataFrame(experiments).drop(columns=['Model_State'])
    csv_path = os.path.join(project_root, 'results', 'optimization_experiments.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    results_df.to_csv(csv_path, index=False)
    
    print("\n📊 REZULTATE COMPARATIVE:")
    print(results_df)
    
    # --- SALVARE MODEL OPTIMIZAT SI CONFIGURATIE ---
    # Alegem cel mai bun R2 Score
    best_exp = max(experiments, key=lambda x: x['R2 Score'])
    print(f"\n🏆 Cel mai bun model: {best_exp['Nume']} cu R2={best_exp['R2 Score']}")
    print(f"⚠️ NOTĂ: Acest model are {best_exp['Hidden Neurons']} neuroni ascunși.")
    
    # 1. Salvare Greutati (.pkl)
    save_path = os.path.join(project_root, 'models', 'optimized_model.pkl')
    torch.save(best_exp['Model_State'], save_path)
    print(f"✅ Model optimizat salvat în: {save_path}")

    # 2. Salvare Configuratie (.json) - PARTEA NOUA
    config_save_path = os.path.join(project_root, 'models', 'model_config.json')
    config_data = {
        "input_size": 5, 
        "hidden_size": best_exp['Hidden Neurons'],  # Salvam automat cat a avut castigatorul
        "output_size": 1
    }
    with open(config_save_path, 'w') as f:
        json.dump(config_data, f)
    print(f"✅ Configurație salvată în: {config_save_path}")

if __name__ == "__main__":
    main()