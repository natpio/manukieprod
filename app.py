import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Manufaktura ERP", layout="wide", initial_sidebar_state="expanded")

# --- SUROWY, INDUSTRIALNY CSS (Matowa czerń + Drewno) ---
st.markdown("""
<style>
    /* Tło całej aplikacji - głęboki, matowy węgiel */
    .stApp {
        background-color: #121212;
    }
    
    /* Wymuszenie czytelności tekstu (jasny szary) */
    p, label, span, .st-emotion-cache-1629p8f {
        color: #e0e0e0 !important;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Tło paska bocznego - ciemny grafit */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #333;
    }
    
    /* Stylowanie przycisków - akcenty w kolorze drewna orzechowego */
    button[kind="primary"] {
        background-color: #8B5A2B !important; 
        border: 1px solid #5C3A21 !important;
        border-radius: 4px;
        color: #ffffff !important;
        font-weight: bold;
        transition: 0.2s;
    }
    button[kind="primary"]:hover {
        background-color: #A0522D !important;
        border-color: #8B5A2B !important;
    }
    
    /* Ukrycie standardowych ozdobników Streamlita */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- POŁĄCZENIE Z BAZĄ DANYCH (Google Sheets) ---
ID_ARKUSZA = "TWÓJ_NOWY_ID_ARKUSZA" # <-- TUTAJ WKLEJ ID NOWEGO ARKUSZA

@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

client = init_connection()

# --- MENU BOCZNE (Nawigacja ERP) ---
st.sidebar.title("🪓 Manufaktura Kiełbas")
st.sidebar.markdown("---")
wybrany_modul = st.sidebar.radio(
    "Panel Sterowania",
    ["📦 Magazyn (Stany)", "📖 Przepisy (Karty)", "🏭 Produkcja", "💰 Finanse i Koszty"]
)

# ==========================================
#          MODUŁ 1: MAGAZYN
# ==========================================
if wybrany_modul == "📦 Magazyn (Stany)":
    st.title("📦 Magazyn Surowców")
    st.markdown("Zarządzaj dostawami i aktualnymi stanami magazynowymi.")
    
    try:
        sheet_magazyn = client.open_by_key(ID_ARKUSZA).worksheet("Magazyn")
        # Pobieramy dane
        dane_magazynu = sheet_magazyn.get_all_records()
        df_magazyn = pd.DataFrame(dane_magazynu)
        
        # Jeśli arkusz jest pusty, tworzymy puste kolumny do wyświetlenia
        if df_magazyn.empty:
            df_magazyn = pd.DataFrame(columns=["ID", "Surowiec", "Ilosc_kg", "Cena_za_kg", "Data_Waznosci", "Nr_Partii_Dostawcy"])
        
        # Wyświetlamy interaktywną tabelę
        st.subheader("Aktualne stany")
        
        # st.data_editor pozwala na edytowanie komórek prosto z interfejsu aplikacji!
        zmieniony_df = st.data_editor(
            df_magazyn,
            num_rows="dynamic", # Pozwala na dodawanie nowych wierszy (dostaw) plusem
            use_container_width=True,
            hide_index=True
        )
        
        # Przycisk zapisu zmian z aplikacji z powrotem do Google Sheets
        if st.button("💾 Zapisz zmiany w bazie", type="primary"):
            with st.spinner("Aktualizowanie bazy danych..."):
                # Czyścimy arkusz z zachowaniem nagłówków
                sheet_magazyn.clear()
                # Przygotowujemy dane do wgrania (nagłówki + wiersze)
                dane_do_wgrania = [zmieniony_df.columns.values.tolist()] + zmieniony_df.values.tolist()
                sheet_magazyn.update("A1", dane_do_wgrania)
            st.success("Magazyn zaktualizowany pomyślnie!")
            
    except Exception as e:
        st.error(f"Błąd połączenia z Arkuszem: {e}")

# ==========================================
#          ZALĄŻKI POZOSTAŁYCH MODUŁÓW
# ==========================================
elif wybrany_modul == "📖 Przepisy (Karty)":
    st.title("📖 Karty Technologiczne")
    st.info("Ten moduł zakodujemy w następnym kroku.")

elif wybrany_modul == "🏭 Produkcja":
    st.title("🏭 Dziennik Produkcyjny")
    st.info("Ten moduł zakodujemy w następnym kroku.")
    
elif wybrany_modul == "💰 Finanse i Koszty":
    st.title("💰 Rentowność i Koszty (Food Cost)")
    st.info("Ten moduł zakodujemy w następnym kroku.")
