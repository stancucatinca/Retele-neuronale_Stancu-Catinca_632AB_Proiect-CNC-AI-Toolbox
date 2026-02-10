import pandas as pd
import numpy as np
import json
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

with open('config/settings.json', 'r') as f:
    config = json.load(f)

def preprocesare():
    print("Incepere preprocesare...")
    
    # 1. Incarcare
    if not os.path.exists(config['data_raw']):
        print("Eroare: Nu exista date raw. Ruleaza generate_simulation.py intai.")
        return

    df = pd.read_csv(config['data_raw'])
    
    # 2. Selectie Features (X) si Target (y)
    # Input: V, f, ap, D, material
    X = df[['V', 'f', 'ap', 'D', 'work_material']].values
    # Target: Prezice doar Ra cu AI (timpul e formula matematica)
    y = df[['Ra']].values

    # 3. Scalare (Standardizare)
    scaler_x = StandardScaler()
    scaler_y = StandardScaler()
    
    X_scaled = scaler_x.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y)
    
    # 4. Impartire Train (70%) / Validation (15%) / Test (15%)
    X_train, X_temp, y_train, y_temp = train_test_split(X_scaled, y_scaled, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    
    # 5. Salvare date procesate
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('data/train', exist_ok=True)
    os.makedirs('data/validation', exist_ok=True)
    os.makedirs('data/test', exist_ok=True)
    
    # Salvare CSV-uri pentru verificare usoara
    pd.DataFrame(np.hstack((X_train, y_train))).to_csv(config['data_train'], index=False, header=False)
    pd.DataFrame(np.hstack((X_val, y_val))).to_csv(config['data_val'], index=False, header=False)
    pd.DataFrame(np.hstack((X_test, y_test))).to_csv(config['data_test'], index=False, header=False)
    
    # Salvare Scalerele pentru a le folosi la predictie
    joblib.dump(scaler_x, config['scaler_x'])
    joblib.dump(scaler_y, config['scaler_y'])
    
    print("Preprocesare completa. Datele si scalerele au fost salvate.")

if __name__ == "__main__":
    preprocesare()