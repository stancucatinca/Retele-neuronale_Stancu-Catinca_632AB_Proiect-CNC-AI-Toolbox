import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import json
import os
import sys
import csv
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# --- BLOC DE FIXARE A CĂII (PATH FIX) ---
# 1. Unde se afla (train_model.py)
current_file_path = os.path.abspath(__file__)
# 2. Folderul parinte (neural_network)
current_dir = os.path.dirname(current_file_path)
# 3. Urc 2 nivele mai sus pentru a ajunge la folderul radacina 'RN'
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
# 4. Adaug aceasta cale in lista unde cauta Python
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ----------------------------------------

from src.neural_network.model_regression import CNCModel

# Cale absoluta catre config
config_path = os.path.join(project_root, 'config', 'settings.json')

with open(config_path, 'r') as f:
    config = json.load(f)

def antreneaza():
    print("Initializare antrenare...")
    
    # 1. Setup Cai Fisiere
    train_path = os.path.join(project_root, config['data_train'])
    val_path = os.path.join(project_root, config['data_val'])
    test_path = os.path.join(project_root, config['data_test']) # Necesar pentru evaluare finala
    model_save_path = os.path.join(project_root, config['model_save_path'])
    
    # Folder pentru rezultate (istoric si metrici)
    results_dir = os.path.join(project_root, 'results')
    os.makedirs(results_dir, exist_ok=True)
    history_csv_path = os.path.join(results_dir, 'training_history.csv')
    metrics_json_path = os.path.join(results_dir, 'test_metrics.json')

    # 2. Incarcare Date
    try:
        train_data = pd.read_csv(train_path, header=None).values
        val_data = pd.read_csv(val_path, header=None).values
        test_data = pd.read_csv(test_path, header=None).values
    except FileNotFoundError:
        print(f"Nu gasesc datele! Verifica daca ai rulat preprocess.py.")
        return

    # Conversie la Tensori PyTorch
    # Inputurile sunt toate coloanele in afara de ultima. Targetul este ultima coloana.
    X_train = torch.FloatTensor(train_data[:, :-1])
    y_train = torch.FloatTensor(train_data[:, -1].reshape(-1, 1))
    
    X_val = torch.FloatTensor(val_data[:, :-1])
    y_val = torch.FloatTensor(val_data[:, -1].reshape(-1, 1))

    X_test = torch.FloatTensor(test_data[:, :-1])
    y_test = torch.FloatTensor(test_data[:, -1].reshape(-1, 1))

    # 3. Initializare Model
    model = CNCModel(config['input_size'], config['hidden_size'], config['output_size'])
    criterion = nn.MSELoss() # Folosim Mean Squared Error pentru regresie
    optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'])
    
    # --- Configurare Early Stopping ---
    patience = 20           # Cate epoci asteptam fara imbunatatire
    patience_counter = 0    # Contor curent
    best_val_loss = float('inf') # Cea mai buna eroare gasita (initial infinit)

    # 4. Bucla de Antrenare (Training Loop)
    epochs = config['epochs']
    
    # Deschidem fisierul CSV pentru a scrie istoricul
    with open(history_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['epoch', 'train_loss', 'val_loss']) # Antet tabel
        
        print(f"Incepem antrenarea pentru {epochs} epoci...")
        
        for epoch in range(epochs):
            # A. Pasul de Antrenare
            model.train()
            optimizer.zero_grad()
            outputs = model(X_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()
            
            # B. Pasul de Validare (fara antrenare)
            model.eval()
            with torch.no_grad():
                val_pred = model(X_val)
                val_loss = criterion(val_pred, y_val)
            
            # C. Salvare in Istoric
            writer.writerow([epoch+1, loss.item(), val_loss.item()])
            
            # Afisare progres
            if (epoch+1) % 50 == 0:
                print(f'Epoch {epoch+1}/{epochs} | Train Loss: {loss.item():.4f} | Val Loss: {val_loss.item():.4f}')
            
            # D. Early Stopping & Salvarea celui mai bun model
            # Daca eroarea de validare scade, salvam modelul ca fiind "cel mai bun"
            if val_loss.item() < best_val_loss:
                best_val_loss = val_loss.item()
                patience_counter = 0 # Resetam contorul
                
                # Salvam fizic modelul
                os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
                torch.save(model.state_dict(), model_save_path)
            else:
                # Daca eroarea nu scade, incrementam contorul
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early Stopping: Antrenarea s-a oprit la epoca {epoch+1} (nu mai invata).")
                    break

    print(f"Cel mai bun model a fost salvat in: {model_save_path}")
    print(f"Istoricul antrenarii salvat in: {history_csv_path}")

    # 5. Evaluare Finala pe Setul de Test (pentru Readme)
    # Incarcam cea mai buna versiune a modelului salvat
    model.load_state_dict(torch.load(model_save_path))
    model.eval()
    
    with torch.no_grad():
        test_predictions = model(X_test).numpy()
        y_test_numpy = y_test.numpy()
        
        # Calculam metricile cerute
        mse = mean_squared_error(y_test_numpy, test_predictions)
        mae = mean_absolute_error(y_test_numpy, test_predictions)
        r2 = r2_score(y_test_numpy, test_predictions)
        
    print("\n=== REZULTATE FINALE PE TEST SET ===")
    print(f"MSE (Eroare Patratica Medie): {mse:.4f}")
    print(f"MAE (Eroare Absoluta Medie):  {mae:.4f}")
    print(f"R2 Score (Coeficient de determinare): {r2:.4f}")
    
    # Salvam metricile
    metrics = {
        "test_mse": round(mse, 4),
        "test_mae": round(mae, 4),
        "test_r2_score": round(r2, 4)
    }
    with open(metrics_json_path, 'w') as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__":
    antreneaza()