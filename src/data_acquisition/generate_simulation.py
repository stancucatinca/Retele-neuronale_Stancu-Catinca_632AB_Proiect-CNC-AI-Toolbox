import os
import pandas as pd
import numpy as np
import json

# Încărcare config pentru calea de salvare
with open('config/settings.json', 'r') as f:
    config = json.load(f)

def genereaza_dataset(n_samples=1000):
    print("Generare date simulate...")
    np.random.seed(42)
    
    # 1. Generare parametri intrare
    V = np.random.uniform(100, 350, n_samples)       # Viteza (m/min)
    f = np.random.uniform(0.05, 0.35, n_samples)     # Avans (mm/rot)
    ap = np.random.uniform(0.5, 4.0, n_samples)      # Adancime (mm)
    D = np.random.choice([10, 12, 16, 20], n_samples)# Diametru scula (mm)
    
    # Material piesa: 0 = Otel, 1 = Aluminiu, 2 = Fonta
    material_code = np.random.randint(0, 3, n_samples)
    
    # 2. Simulare Iesire (Ra) pe baza unei formule empirice + zgomot
    # Formula aproximativa: Ra ~ f^2 / D (teoretic)
    ra_base = (f**2 * 1000) / (4 * D) * 35 
    
    # Ajustari pentru realism (viteza mare scade Ra, materialul influenteaza)
    ra_adjust = ra_base * (1 - (V - 100)/1500)
    
    # Factori material: Aluminiu (1) e cel mai fin, Otel (0) mediu, Fonta (2) rugos
    mat_factor = np.choose(material_code, [1.2, 0.8, 1.4])
    
    Ra = np.abs((ra_adjust * mat_factor) + np.random.normal(0, 0.15, n_samples))
    
    # Calcul Timp (matematic): L=100mm / (RPM * f)
    rpm = (1000 * V) / (3.14 * D)
    vf = rpm * f
    timp = (100 / vf) * 60 # in secunde
    
    df = pd.DataFrame({
        'V': V, 'f': f, 'ap': ap, 'D': D, 
        'work_material': material_code,
        'Ra': Ra,
        'timp': timp
    }).round(4)
    
    # Asigurare directoare
    os.makedirs(os.path.dirname(config['data_raw']), exist_ok=True)
    
    df.to_csv(config['data_raw'], index=False)
    print(f"Dataset salvat in: {config['data_raw']}")

if __name__ == "__main__":
    genereaza_dataset()