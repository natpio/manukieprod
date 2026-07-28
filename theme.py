import streamlit as st
import base64
import os

def pobierz_base64(nazwa_pliku):
    """Odczytuje plik graficzny i konwertuje go do formatu Base64 używanego w CSS."""
    try:
        with open(nazwa_pliku, "rb") as plik:
            dane = plik.read()
        return base64.b64encode(dane).decode()
    except FileNotFoundError:
        return ""

def zaladuj_styl():
    # Pobieranie tekstur
    tlo_stal = pobierz_base64("stal.jpg")
    tlo_drewno = pobierz_base64("drewno.png")
    
    # Renderowanie głównego logo na samej górze panelu bocznego
    if os.path.exists("kiel1.png"):
        st.sidebar.image("kiel1.png", use_column_width=True)
    
    # Wstrzykiwanie potężnego, industrialnego CSS
    css = f"""
    <style>
        /* Tło główne - szczotkowana stal/żeliwo */
        .stApp {{
            background-image: url("data:image/jpeg;base64,{tlo_stal}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        
        /* Tło panelu bocznego - deska sztorcowa */
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{tlo_drewno}");
            background-size: cover;
            border-right: 3px solid #1a1a1a;
            box-shadow: 5px 0px 15px rgba(0,0,0,0.7);
        }}
        
        /* Półprzezroczyste tło dla czytelności zawartości na stali */
        .stDataFrame {{ 
            background-color: rgba(20, 20, 20, 0.85) !important; 
            border: 2px solid #333;
            border-radius: 5px;
            box-shadow: 0px 5px 15px rgba(0,0,0,0.8);
        }}
        
        /* Typografia z efektem cienia (odcięcie tekstu od tła) */
        h1, h2, h3, p, label, span, .st-emotion-cache-1629p8f {{
            color: #f0f0f0 !important;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.9);
        }}
        
        /* Przyciski z efektem fizycznego wciśnięcia (Drewno w metalowej ramie) */
        button[kind="primary"] {{
            background: linear-gradient(180deg, #6B4226 0%, #4A2E1B 100%) !important;
            border: 2px solid #2a1a0f !important;
            border-radius: 4px;
            color: #ffffff !important;
            font-weight: bold;
            letter-spacing: 1px;
            text-shadow: 1px 1px 2px black;
            box-shadow: 0px 4px 5px rgba(0,0,0,0.8);
            transition: all 0.2s ease;
        }}
        
        button[kind="primary"]:hover {{
            background: linear-gradient(180deg, #8B5A2B 0%, #5C3A21 100%) !important;
            transform: translateY(2px);
            box-shadow: 0px 2px 3px rgba(0,0,0,0.8);
        }}
        
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
