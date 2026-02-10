import streamlit as st
import pandas as pd
import torch
import numpy as np
import joblib
import json
import os
import sys
import matplotlib.pyplot as plt

# --- 1. CONFIGURARE CĂI (Path Fix) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Urcam 2 niveluri: app -> src -> RN
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.neural_network.model_regression import CNCModel

# --- 2. FUNCȚII DE ÎNCĂRCARE (Backend) ---
@st.cache_resource
def load_resources():
    config_path = os.path.join(project_root, 'config', 'settings.json')
    
    # Verificare existenta config general
    if not os.path.exists(config_path):
        return None, None, None, "Nu am găsit fisierul config/settings.json"

    with open(config_path, 'r') as f:
        config = json.load(f)
        
    # Cai catre fisierele modelului
    model_path = os.path.join(project_root, 'models', 'optimized_model.pkl')
    model_config_path = os.path.join(project_root, 'models', 'model_config.json') # Config dinamic
    scaler_x_path = os.path.join(project_root, config['scaler_x'])
    scaler_y_path = os.path.join(project_root, config['scaler_y'])

    # Verificăm dacă modelul optimizat există
    if not os.path.exists(model_path):
        return None, None, None, "Lipseste 'optimized_model.pkl'. Ruleaza intai 'optimize.py'!"

    # --- MODIFICARE: Citim configuratia dinamica (nr. neuroni) ---
    if os.path.exists(model_config_path):
        with open(model_config_path, 'r') as f:
            model_config = json.load(f)
        hidden_size = model_config.get("hidden_size", 64) # Citim din fisier
    else:
        hidden_size = 64 # Valoare default daca fisierul lipseste

    # Inițializare Model cu marimea corecta
    model = CNCModel(config['input_size'], hidden_size, config['output_size'])
    
    try:
        model.load_state_dict(torch.load(model_path))
        model.eval()
    except Exception as e:
        return None, None, None, f"Eroare la încărcarea modelului: {e}"

    # Încărcare Scalere
    try:
        sc_x = joblib.load(scaler_x_path)
        sc_y = joblib.load(scaler_y_path)
    except:
        return None, None, None, "Lipsesc scalerele. Ruleaza 'preprocess.py'!"
    
    return model, sc_x, sc_y, None

# Logica de business
def calculate_time(V, f, D, L=100):
    rpm = (1000 * V) / (3.14159 * D)
    vf = rpm * f 
    if vf <= 0: return 9999.0
    return (L / vf) * 60 

def select_tool(material, diameter):
    if material == "Otel":
        return "Freza Endmill (TiAlN)", "Carbura"
    elif material == "Aluminiu":
        return "Freza High Helix (Polished)", "Carbura"
    else:
        return "Freza Carbura K (TiCN)", "Carbura"

# --- 3. INTERFAȚA GRAFICĂ (Frontend) ---

# Configurare Pagină
st.set_page_config(page_title="CNC-AI Toolbox (Optimizat)", layout="wide")

# Titlu
st.title(" CNC-AI Toolbox ")
st.markdown("### Optimizare Parametri de Așchiere cu Rețele Neuronale (Versiune Finală)")
st.markdown("---")

# Încărcăm resursele
model, sc_x, sc_y, err = load_resources()

if err:
    st.error(f" Eroare {err}")
    st.stop()

# --- SIDEBAR (INPUTURI) ---
st.sidebar.header("1. Configurare Proces")

# Status Model
st.sidebar.success("Model Activ: Optimizat (v2)")

material = st.sidebar.selectbox("Material Piesă", ["Otel", "Aluminiu", "Fonta"])
diametru = st.sidebar.selectbox("Diametru Sculă (mm)", [10, 12, 16, 20])
ra_target = st.sidebar.slider("Rugozitate Țintă Ra (µm)", 0.4, 6.0, 1.6, 0.1)

st.sidebar.subheader("Limite Mașină")
rpm_max = st.sidebar.number_input("Turație Maximă (RPM)", 1000, 12000, 4000)

btn_optimize = st.sidebar.button(" Generează Soluții Optime", type="primary")

# --- ZONA PRINCIPALĂ ---

if btn_optimize:
    # 1. Recomandare Scula
    scula_tip, scula_mat = select_tool(material, diametru)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f" **Scula Recomandată:** {scula_tip}")
    with col2:
        st.success(f" **Material Sculă:** {scula_mat}")
        
    # 2. Rulare AI (Generare Soluții)
    with st.spinner('AI-ul analizează 2000 de scenarii posibile...'):
        # Mapare material
        mat_map = {"Otel": 0, "Aluminiu": 1, "Fonta": 2}
        mat_code = mat_map.get(material, 0) # Simplificat
        
        # Generare 2000 combinații random
        n_sim = 2000
        V_cand = np.random.uniform(100, 300, n_sim)
        f_cand = np.random.uniform(0.05, 0.3, n_sim)
        ap_cand = np.random.uniform(0.5, 3.0, n_sim)
        D_cand = np.full(n_sim, diametru)
        mat_cand = np.full(n_sim, mat_code)
        
        # Predicție AI
        X_cand = np.column_stack((V_cand, f_cand, ap_cand, D_cand, mat_cand))
        X_cand_scaled = sc_x.transform(X_cand)
        
        with torch.no_grad():
            ra_pred_scaled = model(torch.FloatTensor(X_cand_scaled)).numpy()
        
        ra_pred = sc_y.inverse_transform(ra_pred_scaled).flatten()
        
        # Filtrare Soluții
        results = []
        for i in range(n_sim):
            if ra_pred[i] <= ra_target:
                rpm = (1000 * V_cand[i]) / (3.14159 * D_cand[i])
                if rpm <= rpm_max:
                    t = calculate_time(V_cand[i], f_cand[i], D_cand[i])
                    results.append({
                        "V (m/min)": round(float(V_cand[i]), 1),
                        "f (mm/rot)": round(float(f_cand[i]), 3),
                        "ap (mm)": round(float(ap_cand[i]), 1),
                        "Ra Predis (µm)": round(float(ra_pred[i]), 3),
                        "Timp (s)": round(float(t), 1)
                    })
        
        # Sortare și Top 5
        df_res = pd.DataFrame(results)
        
        if not df_res.empty:
            df_res = df_res.sort_values(by="Timp (s)").head(5).reset_index(drop=True)
            
            st.subheader("Soluții Optime Identificate (Pareto)")
            st.dataframe(df_res.style.highlight_min(subset=["Timp (s)"], color="#d1e7dd"), use_container_width=True)
            
            # Grafic
            st.subheader("Vizualizare Compromis Calitate vs. Timp")
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Plotam punctele gasite
            ax.scatter(df_res["Timp (s)"], df_res["Ra Predis (µm)"], color='red', s=100, label='Top 5 Optime', zorder=5)
            # Putem plota si cateva puncte gri pentru context (optional, daca aveam intregul set filtrat)
            
            ax.set_xlabel("Timp de Prelucrare (s)")
            ax.set_ylabel("Rugozitate Prezisa (µm)")
            ax.set_title(f"Frontul Pareto pentru {material} (D={diametru}mm)")
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend()
            
            st.pyplot(fig)
            
        else:
            st.warning("Nu am găsit soluții care să respecte limita de rugozitate și turație. Încearcă să crești Ra Target sau Turația Maximă.")
else:
    st.info("Setează parametrii din meniul stânga și apasă 'Generează Soluții'!")