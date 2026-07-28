import streamlit as st
import base64
import os

def pobierz_base64(nazwa_pliku):
    try:
        with open(nazwa_pliku, "rb") as plik:
            dane = plik.read()
        return base64.b64encode(dane).decode()
    except FileNotFoundError:
        return ""

def zaladuj_styl():
    tlo_stal = pobierz_base64("stal.jpg")
    tlo_drewno = pobierz_base64("drewno.png")
    
    css = f"""
    <style>
        /* Całkowite ukrycie paska bocznego (Sidebar) */
        [data-testid="stSidebar"] {{ display: none !important; }}
        [data-testid="collapsedControl"] {{ display: none !important; }}
        
        /* Tło główne - żeliwo */
        .stApp {{
            background-image: url("data:image/jpeg;base64,{tlo_stal}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        
        /* Ciemne tło pod tabelami */
        .stDataFrame {{ 
            background-color: rgba(20, 20, 20, 0.85) !important; 
            border: 2px solid #333;
            border-radius: 5px;
        }}
        
        /* Typografia ogólna */
        h1, h2, h3, p, label, span, .st-emotion-cache-1629p8f {{
            color: #f0f0f0 !important;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.9);
        }}
        
        /* =========================================
           STYLIZACJA ZAKŁADEK GÓRNYCH (TABS)
           ========================================= */
        /* Kontener na zakładki z teksturą drewna */
        div[data-baseweb="tab-list"] {{
            background-image: url("data:image/png;base64,{tlo_drewno}");
            background-size: cover;
            border-radius: 8px;
            padding: 8px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.8);
            gap: 10px;
        }}
        
        /* Pojedyncza, nieaktywna zakładka */
        button[role="tab"] {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            border: 1px solid #222 !important;
            border-radius: 5px;
            color: #ccc !important;
            font-weight: bold;
            padding: 10px 20px !important;
            flex-grow: 1; /* Zakładki równomiernie wypełnią ekran */
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        /* Najedzienie myszką na zakładkę */
        button[role="tab"]:hover {{
            background-color: rgba(50, 50, 50, 0.9) !important;
            color: #fff !important;
        }}
        
        /* AKTYWNA zakładka (wciśnięty przycisk) */
        button[role="tab"][aria-selected="true"] {{
            background: linear-gradient(180deg, #8B5A2B 0%, #5C3A21 100%) !important;
            border-color: #a05a2c !important;
            color: #fff !important;
            box-shadow: inset 0px 4px 6px rgba(0,0,0,0.6);
        }}
        
        /* Ukrycie standardowej kreski podkreślającej zakładki w Streamlit */
        div[data-baseweb="tab-highlight"] {{ display: none; }}
        
        /* Przyciski operacyjne (Zapisz, Rozpocznij) */
        button[kind="primary"] {{
            background: linear-gradient(180deg, #6B4226 0%, #4A2E1B 100%) !important;
            border: 2px solid #2a1a0f !important;
            border-radius: 4px;
            color: #ffffff !important;
            font-weight: bold;
        }}
        button[kind="primary"]:hover {{
            background: linear-gradient(180deg, #8B5A2B 0%, #5C3A21 100%) !important;
        }}
        
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
