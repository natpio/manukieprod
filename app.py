import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Manufaktura ERP", layout="wide", initial_sidebar_state="expanded")

# --- SUROWY, INDUSTRIALNY CSS (Matowa czerń + Drewno) ---
st.markdown("""
<style>
    .stApp { background-color: #121212; }
    p, label, span, .st-emotion-cache-1629p8f { color: #e0e0e0 !important; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 600; }
    [data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 1px solid #333; }
    
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
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Ciemne tło dla tabel i ramek */
    .stDataFrame { background-color: #1e1e1e !important; }
</style>
""", unsafe_allow_html=True)

# --- POŁĄCZENIE Z BAZĄ DANYCH ---
ID_ARKUSZA = "1zr3fL2b6-KwDXoGC5EDfYpf0b1pgh6_-126TrSm4wZo"

@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

client = init_connection()

# --- MENU BOCZNE ---
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
        dane_magazynu = sheet_magazyn.get_all_records()
        df_magazyn = pd.DataFrame(dane_magazynu)
        if df_magazyn.empty:
            df_magazyn = pd.DataFrame(columns=["ID", "Surowiec", "Ilosc_kg", "Cena_za_kg", "Data_Waznosci", "Nr_Partii_Dostawcy"])
        
        zmieniony_df = st.data_editor(df_magazyn, num_rows="dynamic", use_container_width=True, hide_index=True)
        
        if st.button("💾 Zapisz zmiany w bazie", type="primary"):
            with st.spinner("Aktualizowanie bazy..."):
                sheet_magazyn.clear()
                dane_do_wgrania = [zmieniony_df.columns.values.tolist()] + zmieniony_df.values.tolist()
                sheet_magazyn.update("A1", dane_do_wgrania)
            st.success("Magazyn zaktualizowany!")
    except Exception as e:
        st.error(f"Błąd połączenia z Arkuszem: {e}")

# ==========================================
#          MODUŁ 2: PRZEPISY
# ==========================================
elif wybrany_modul == "📖 Przepisy (Karty)":
    st.title("📖 Karty Technologiczne")
    st.markdown("Określ procentowy udział przypraw w stosunku do wagi mięsa (np. wpisz 1.5 dla soli peklującej, jeśli dajesz 15g na 1kg mięsa).")
    
    try:
        sheet_przepisy = client.open_by_key(ID_ARKUSZA).worksheet("Przepisy")
        dane_przepisy = sheet_przepisy.get_all_records()
        df_przepisy = pd.DataFrame(dane_przepisy)
        if df_przepisy.empty:
            df_przepisy = pd.DataFrame(columns=["ID", "Nazwa_Kielbasy", "Skladnik", "Procent_Wagi_Miesa"])
        
        zmieniony_przepis = st.data_editor(df_przepisy, num_rows="dynamic", use_container_width=True, hide_index=True)
        
        if st.button("💾 Zapisz receptury", type="primary"):
            with st.spinner("Zapisywanie receptur..."):
                sheet_przepisy.clear()
                dane_do_wgrania = [zmieniony_przepis.columns.values.tolist()] + zmieniony_przepis.values.tolist()
                sheet_przepisy.update("A1", dane_do_wgrania)
            st.success("Przepisy zapisane pomyślnie!")
    except Exception as e:
        st.error(f"Błąd połączenia z Arkuszem: {e}")

# ==========================================
#          MODUŁ 3: PRODUKCJA
# ==========================================
elif wybrany_modul == "🏭 Produkcja":
    st.title("🏭 Dziennik Produkcyjny")
    
    try:
        # Pobieranie receptur, aby wiedzieć, co produkujemy
        sheet_przepisy = client.open_by_key(ID_ARKUSZA).worksheet("Przepisy")
        df_przepisy = pd.DataFrame(sheet_przepisy.get_all_records())
        
        sheet_produkcja = client.open_by_key(ID_ARKUSZA).worksheet("Produkcja")
        
        if df_przepisy.empty:
            st.warning("Brak przepisów w bazie. Najpierw dodaj recepturę w zakładce Przepisy.")
        else:
            unikalne_kielbasy = df_przepisy['Nazwa_Kielbasy'].unique().tolist()
            
            # Panel konfiguracyjny partii
            col1, col2 = st.columns(2)
            with col1:
                wybrana_kielbasa = st.selectbox("Wybierz produkt:", unikalne_kielbasy)
                waga_miesa = st.number_input("Waga głównego wsadu mięsnego (kg):", min_value=0.0, step=0.5, value=10.0)
            
            with col2:
                # Automatyczne generowanie numeru partii na podstawie dzisiejszej daty
                dzisiaj = datetime.now()
                nr_partii_propozycja = f"MK-{dzisiaj.strftime('%y%m%d')}-01"
                nr_partii = st.text_input("Numer Partii:", value=nr_partii_propozycja)
                
                # Zdefiniowany precyzyjnie Twój sprzęt do zachowania powtarzalności
                sprzet = st.selectbox("Użyty sprzęt i konfiguracja:", [
                    "Maszynka: Serie 6 (2100W) - Sitko 8mm",
                    "Maszynka: Serie 6 (2100W) - Sitko 4mm",
                    "Maszynka: Serie 6 (2100W) - Szarpak",
                    "Mieszarka ręczna",
                    "Nadziewarka pionowa"
                ])
                
            st.markdown("### 🧪 Wymagane przyprawy (obliczone z receptury)")
            # Filtrujemy bazę tylko dla wybranej kiełbasy
            przepis_filtr = df_przepisy[df_przepisy['Nazwa_Kielbasy'] == wybrana_kielbasa].copy()
            
            # Zamiana przecinków na kropki i konwersja na liczby dla pewności obliczeń
            przepis_filtr['Procent_Wagi_Miesa'] = przepis_filtr['Procent_Wagi_Miesa'].astype(str).str.replace(',', '.').astype(float)
            
            # Obliczenie potrzebnych gramatur (Waga mięsa w kg * 1000 = gramy * procent)
            przepis_filtr['Potrzebna_Ilosc'] = (waga_miesa * 1000) * (przepis_filtr['Procent_Wagi_Miesa'] / 100)
            przepis_filtr['Potrzebna_Ilosc'] = przepis_filtr['Potrzebna_Ilosc'].round(1).astype(str) + " g"
            
            st.dataframe(przepis_filtr[['Skladnik', 'Potrzebna_Ilosc']], use_container_width=True, hide_index=True)
            
            if st.button("🚀 Rozpocznij i zapisz partię", type="primary"):
                with st.spinner("Zapisywanie w Dzienniku Produkcyjnym..."):
                    nowy_wiersz = [nr_partii, dzisiaj.strftime('%Y-%m-%d'), wybrana_kielbasa, waga_miesa, sprzet, "W toku"]
                    sheet_produkcja.append_row(nowy_wiersz)
                st.success(f"Partia {nr_partii} została zapisana w systemie!")

    except Exception as e:
        st.error(f"Błąd modułu produkcji: {e}")

# ==========================================
#          MODUŁ 4: FINANSE
# ==========================================
elif wybrany_modul == "💰 Finanse i Koszty":
    st.title("💰 Rentowność i Koszty")
    st.info("Ten moduł zaprogramujemy w kolejnym kroku, gdy zapiszesz już pierwsze partie testowe.")
