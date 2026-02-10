import torch
import numpy as np
import joblib
import json
import sys
import os
import csv
from datetime import datetime

# --- BLOC DE FIXARE A CĂII (PATH FIX) ---
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ----------------------------------------

from src.neural_network.model_regression import CNCModel

# Incarcare config
config_path = os.path.join(project_root, 'config', 'settings.json')
with open(config_path, 'r') as f:
    config = json.load(f)

# --- Functii Ajutatoare ---

def load_resources():
    """Incarca modelul antrenat si scalerele folosind cai absolute."""
    model_path = os.path.join(project_root, config['model_save_path'])
    scaler_x_path = os.path.join(project_root, config['scaler_x'])
    scaler_y_path = os.path.join(project_root, config['scaler_y'])

    model = CNCModel(config['input_size'], config['hidden_size'], config['output_size'])
    
    try:
        model.load_state_dict(torch.load(model_path))
    except FileNotFoundError:
        raise Exception("Modelul nu a fost gasit! Ruleaza intai 'train_model.py'.")
        
    model.eval()
    
    sc_x = joblib.load(scaler_x_path)
    sc_y = joblib.load(scaler_y_path)
    return model, sc_x, sc_y

def select_tool_rule_based(material_name, diameter):
    tool = {
        "type": "Unknown", 
        "material": "Carbura", 
        "coating": "None", 
        "diameter": diameter
    }
    
    if material_name.lower() == "otel":
        tool["type"] = "Freza Cilindro-Frontala (Endmill)"
        tool["coating"] = "TiAlN (Titan-Aluminiu-Nitrid)"
    elif material_name.lower() == "aluminiu":
        tool["type"] = "Freza pentru Aluminiu (High Helix)"
        tool["coating"] = "ZrN sau Neacoperita (Polished)"
    elif material_name.lower() == "fonta":
        tool["type"] = "Freza Carbura K"
        tool["coating"] = "TiCN"
        
    return tool

def calculate_time(V, f, D, L=100):
    rpm = (1000 * V) / (3.14159 * D)
    vf = rpm * f 
    if vf <= 0: return 9999
    return (L / vf) * 60 

def optimize_pareto(input_req):
    model, sc_x, sc_y = load_resources()
    
    mat_map = {"otel": 0, "aluminiu": 1, "fonta": 2}
    mat_code = mat_map.get(input_req['work_material'].lower(), 0)
    
    print(f"\nCautare solutii optime pentru: {input_req['work_material']}, Ra Tinta: {input_req['Ra_target']}...")
    
    # Generare Candidati
    n_sim = 2000
    V_cand = np.random.uniform(100, 300, n_sim)
    f_cand = np.random.uniform(0.05, 0.3, n_sim)
    ap_cand = np.random.uniform(0.5, 3.0, n_sim)
    D_cand = np.full(n_sim, input_req['tool_stock'])
    mat_cand = np.full(n_sim, mat_code)
    
    X_cand = np.column_stack((V_cand, f_cand, ap_cand, D_cand, mat_cand))
    X_cand_scaled = sc_x.transform(X_cand)
    
    with torch.no_grad():
        ra_pred_scaled = model(torch.FloatTensor(X_cand_scaled)).numpy()
    
    ra_pred = sc_y.inverse_transform(ra_pred_scaled).flatten()
    
    results = []
    for i in range(n_sim):
        if ra_pred[i] <= input_req['Ra_target']:
            rpm = (1000 * V_cand[i]) / (3.14 * D_cand[i])
            if rpm <= input_req['machine_limits']['rpm_max']:
                t = calculate_time(V_cand[i], f_cand[i], D_cand[i])
                
                # Convertim la float python standard pentru a evita erori JSON/CSV
                results.append({
                    "V (m/min)": round(float(V_cand[i]), 1),
                    "f (mm/rot)": round(float(f_cand[i]), 3),
                    "ap (mm)": round(float(ap_cand[i]), 1),
                    "Ra_pred (um)": round(float(ra_pred[i]), 3),
                    "Timp_est (s)": round(float(t), 1)
                })
    
    results.sort(key=lambda x: x['Timp_est (s)'])
    return results[:5] # Returnam top 5 solutii

def salveaza_rezultate(output_data):
    # 1. Cream folderul de rapoarte daca nu exista
    reports_dir = os.path.join(project_root, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # --- A. Salvare Raport TXT (Human Readable) ---
    txt_filename = os.path.join(reports_dir, f"Raport_Optimizare_{timestamp}.txt")
    with open(txt_filename, "w") as f:
        f.write("=== RAPORT OPTIMIZARE CNC-AI TOOLBOX ===\n")
        f.write(f"Data: {datetime.now()}\n\n")
        
        f.write("1. RECOMANDARE SCULA\n")
        f.write("-" * 20 + "\n")
        tool = output_data["tool_recommended"]
        for k, v in tool.items():
            f.write(f"{k.capitalize()}: {v}\n")
            
        f.write("\n2. SOLUTII PARETO (Top Optiuni)\n")
        f.write("-" * 20 + "\n")
        if output_data["pareto_solutions"]:
            # Cap de tabel
            headers = list(output_data["pareto_solutions"][0].keys())
            f.write(" | ".join(headers) + "\n")
            for sol in output_data["pareto_solutions"]:
                vals = [str(sol[k]) for k in headers]
                f.write(" | ".join(vals) + "\n")
        else:
            f.write("Nu au fost gasite solutii care sa respecte constrangerile.\n")
            
        f.write(f"\nNote: {output_data['notes']}\n")

    print(f"\n[OK] Raport TXT salvat: {txt_filename}")

    # --- B. Salvare Solutii CSV (Excel Ready) ---
    if output_data["pareto_solutions"]:
        csv_filename = os.path.join(reports_dir, f"Solutii_Pareto_{timestamp}.csv")
        keys = output_data["pareto_solutions"][0].keys()
        with open(csv_filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(output_data["pareto_solutions"])
        print(f"[OK] Date CSV salvate: {csv_filename}")

def testare_manuala(V, f, ap, D, material):
    """
    Funcție pentru a testa manual o singură combinație de parametri.
    """
    model, sc_x, sc_y = load_resources()
    
    # 1. Transformăm materialul în număr (0, 1 sau 2)
    mat_map = {"otel": 0, "aluminiu": 1, "fonta": 2}
    mat_code = mat_map.get(material.lower(), 0) # Default Otel
    
    # 2. Pregătim datele pentru AI (Vectorul [V, f, ap, D, mat])
    input_values = np.array([[V, f, ap, D, mat_code]])
    
    # 3. Scalăm datele (le aducem la formatul înțeles de AI)
    input_scaled = sc_x.transform(input_values)
    input_tensor = torch.FloatTensor(input_scaled)
    
    # 4. Facem predicția
    with torch.no_grad():
        ra_scaled = model(input_tensor).numpy()
        
    # 5. Transformăm rezultatul înapoi în um (de-scalare)
    ra_pred = sc_y.inverse_transform(ra_scaled).flatten()[0]
    
    # 6. Calculăm și timpul matematic
    timp = calculate_time(V, f, D)
    
    print(f"\n>>> REZULTAT TEST MANUAL <<<")
    print(f"Material: {material} | V: {V} m/min | f: {f} mm/rot | ap: {ap} mm")
    print(f"PREDICȚIE AI -> Rugozitate (Ra): {ra_pred:.4f} um")
    print(f"CALCUL MATEMATIC -> Timp: {timp:.2f} secunde")
    print("-" * 30)

# --- Main ---
if __name__ == "__main__":
    
    # --- 1. RULARE TEST MANUAL ---
    # Poți comenta linia de mai jos dacă vrei doar optimizare
    try:
        testare_manuala(V=150, f=0.2, ap=2.0, D=16, material="Aluminiu")
    except Exception as e:
        print(f"Eroare la testul manual: {e}")

    # --- 2. RULARE OPTIMIZARE AUTOMATA ---
    # INPUT DE LA UTILIZATOR (Simulat)
    request = {
        "operation": "frezare",
        "work_material": "Otel",
        "tool_stock": 16,
        "Ra_target": 1.6,
        "machine_limits": {"rpm_max": 4000, "power_kW": 5.5}
    }
    
    try:
        # Recomandare Scula
        tool_info = select_tool_rule_based(request['work_material'], request['tool_stock'])
        
        # Optimizare Parametri
        pareto_solutions = optimize_pareto(request)
        
        # Structura Date Finala
        output = {
            "tool_recommended": tool_info,
            "pareto_solutions": pareto_solutions,
            "constraints_ok": len(pareto_solutions) > 0,
            "notes": "Solutiile respecta rugozitatea tinta si limitele de turatie."
        }
        
        # Afisare la consola (JSON)
        print(json.dumps(output, indent=4))
        
        # Salvare in fisiere
        salveaza_rezultate(output)
        
    except Exception as e:
        print(f"\nEROARE: {e}")
        print("Asigura-te ca ai rulat 'train_model.py' inainte!")