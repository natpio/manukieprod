import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from theme import zaladuj_styl  # Import naszego nowego modułu!

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Manufaktura ERP", layout="wide", initial_sidebar_state="expanded")

# --- ZAŁADOWANIE WIZUALIZACJI ---
zaladuj_styl()

# --- POŁĄCZENIE Z BAZĄ DANYCH ---
ID_ARKUSZA = "1zr3fL2b6-KwDXoGC5EDfYpf0b1pgh6_-126TrSm4wZo"

# ... (tutaj zaczyna się funkcja init_connection() i reszta kodu z modułami, nic więcej nie musisz zmieniać) ...
