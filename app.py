import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Manufaktura ERP", layout="wide", initial_sidebar_state="expanded")

# --- SUROWY, INDUSTRIALNY CSS ---
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
    .stDataFrame { background-color: #1e1e1e !important; }
    
    /* Stylowanie wskaźników metryk finansowych */
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
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
    try:
        sheet_magazyn = client.open_by_key(ID_ARKUSZA).worksheet("Magazyn")
        df_magazyn = pd.DataFrame(sheet_magazyn.get_all_records())
        if df_magazyn.empty:
            df_magazyn = pd.DataFrame(columns=["ID", "Surowiec", "Ilosc_kg", "Cena_za_kg", "Data_Waznosci", "Nr_Partii_Dostawcy"])
        
        zmieniony_df = st.data_editor(df_magazyn, num_rows="dynamic", use_container_width=True, hide_index=True)
        
        if st.button("💾 Zapisz zmiany w bazie", type="primary"):
            with st.spinner("Aktualizowanie bazy..."):
                sheet_magazyn.clear()
                sheet_magazyn.update("A1", [zmieniony_df.columns.values.tolist()] + zmieniony_df.values.tolist())
            st.success("Magazyn zaktualizowany!")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# ==========================================
#          MODUŁ 2: PRZEPISY
# ==========================================
elif wybrany_modul == "📖 Przepisy (Karty)":
    st.title("📖 Karty Technologiczne")
    try:
        sheet_przepisy = client.open_by_key(ID_ARKUSZA).worksheet("Przepisy")
        df_przepisy = pd.DataFrame(sheet_przepisy.get_all_records())
        if df_przepisy.empty:
            df_przepisy = pd.DataFrame(columns=["ID", "Nazwa_Kielbasy", "Kategoria", "Skladnik", "Procent_Wagi_Miesa"])
        
        zmieniony_przepis = st.data_editor(
            df_przepisy, 
            num_rows="dynamic", 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Kategoria": st.column_config.SelectboxColumn("Kategoria", options=["Mięso", "Przyprawa", "Dodatek (Woda/Jelita)"], required=True)
            }
        )
        
        if st.button("💾 Zapisz receptury", type="primary"):
            with st.spinner("Zapisywanie receptur..."):
                sheet_przepisy.clear()
                sheet_przepisy.update("A1", [zmieniony_przepis.columns.values.tolist()] + zmieniony_przepis.values.tolist())
            st.success("Przepisy zapisane pomyślnie!")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# ==========================================
#          MODUŁ 3: PRODUKCJA
# ==========================================
elif wybrany_modul == "🏭 Produkcja":
    st.title("🏭 Dziennik Produkcyjny")
    try:
        sheet_przepisy = client.open_by_key(ID_ARKUSZA).worksheet("Przepisy")
        df_przepisy = pd.DataFrame(sheet_przepisy.get_all_records())
        sheet_produkcja = client.open_by_key(ID_ARKUSZA).worksheet("Produkcja")
        
        if df_przepisy.empty:
            st.warning("Brak przepisów w bazie.")
        else:
            unikalne_kielbasy = df_przepisy['Nazwa_Kielbasy'].unique().tolist()
            col1, col2 = st.columns(2)
            with col1:
                wybrana_kielbasa = st.selectbox("Wybierz produkt:", unikalne_kielbasy)
                waga_miesa = st.number_input("Całkowita waga docelowego wsadu mięsnego (kg):", min_value=0.0, step=0.5, value=10.0)
            with col2:
                dzisiaj = datetime.now()
                nr_partii = st.text_input("Numer Partii:", value=f"MK-{dzisiaj.strftime('%y%m%d')}-01")
                sprzet = st.selectbox("Użyty sprzęt i konfiguracja:", ["Maszynka: Serie 6 (2100W) - Sitko 8mm", "Maszynka: Serie 6 (2100W) - Sitko 4mm", "Maszynka: Serie 6 (2100W) - Szarpak", "Mieszarka ręczna", "Nadziewarka pionowa"])
                
            przepis_filtr = df_przepisy[df_przepisy['Nazwa_Kielbasy'] == wybrana_kielbasa].copy()
            przepis_filtr['Procent_Wagi_Miesa'] = przepis_filtr['Procent_Wagi_Miesa'].astype(str).str.replace(',', '.').astype(float)
            
            st.markdown("---")
            col_mieso, col_przyprawy = st.columns(2)
            with col_mieso:
                st.markdown("### 🥩 Wymagane klasy mięsa")
                df_mieso = przepis_filtr[przepis_filtr['Kategoria'] == 'Mięso'].copy()
                if not df_mieso.empty:
                    df_mieso['Potrzebna_Ilosc'] = (waga_miesa * (df_mieso['Procent_Wagi_Miesa'] / 100))
                    df_mieso['Potrzebna_Ilosc'] = df_mieso['Potrzebna_Ilosc'].round(2).astype(str) + " kg"
                    st.dataframe(df_mieso[['Skladnik', 'Potrzebna_Ilosc']], use_container_width=True, hide_index=True)
            with col_przyprawy:
                st.markdown("### 🧪 Wymagane przyprawy")
                df_przyp = przepis_filtr[przepis_filtr['Kategoria'] != 'Mięso'].copy()
                if not df_przyp.empty:
                    df_przyp['Potrzebna_Ilosc'] = (waga_miesa * 1000) * (df_przyp['Procent_Wagi_Miesa'] / 100)
                    df_przyp['Potrzebna_Ilosc'] = df_przyp['Potrzebna_Ilosc'].round(1).astype(str) + " g"
                    st.dataframe(df_przyp[['Skladnik', 'Potrzebna_Ilosc']], use_container_width=True, hide_index=True)
            
            if st.button("🚀 Rozpocznij i zapisz partię", type="primary"):
                sheet_produkcja.append_row([nr_partii, dzisiaj.strftime('%Y-%m-%d'), wybrana_kielbasa, waga_miesa, sprzet, "W toku"])
                st.success(f"Partia {nr_partii} zapisana!")
    except Exception as e:
        st.error(f"Błąd: {e}")

# ==========================================
#          MODUŁ 4: FINANSE
# ==========================================
elif wybrany_modul == "💰 Finanse i Koszty":
    st.title("💰 Rozliczenie Partii (Food Cost)")
    st.markdown("Wybierz partię z Dziennika Produkcyjnego, aby wyliczyć jej opłacalność po obróbce termicznej.")
    
    try:
        # Pobieranie danych z 3 zakładek
        sheet_produkcja = client.open_by_key(ID_ARKUSZA).worksheet("Produkcja")
        sheet_przepisy = client.open_by_key(ID_ARKUSZA).worksheet("Przepisy")
        sheet_magazyn = client.open_by_key(ID_ARKUSZA).worksheet("Magazyn")
        sheet_finanse = client.open_by_key(ID_ARKUSZA).worksheet("Finanse")
        
        df_produkcja = pd.DataFrame(sheet_produkcja.get_all_records())
        df_przepisy = pd.DataFrame(sheet_przepisy.get_all_records())
        df_magazyn = pd.DataFrame(sheet_magazyn.get_all_records())
        
        if df_produkcja.empty or df_przepisy.empty or df_magazyn.empty:
            st.warning("Brakuje danych w Magazynie, Przepisach lub Produkcji do przeprowadzenia kalkulacji.")
        else:
            # Wybór partii do analizy
            lista_partii = df_produkcja['Nr_Partii'].unique().tolist()
            lista_partii.reverse() # Najnowsze na górze
            wybrana_partia = st.selectbox("Wybierz numer partii do rozliczenia:", lista_partii)
            
            # Pobieranie informacji o wybranej partii
            dane_partii = df_produkcja[df_produkcja['Nr_Partii'] == wybrana_partia].iloc[0]
            nazwa_kielbasy = dane_partii['Rodzaj_Kielbasy']
            waga_surowego_miesa = float(str(dane_partii['Waga_Miesa_kg']).replace(',', '.'))
            
            # Pobranie receptury
            przepis = df_przepisy[df_przepisy['Nazwa_Kielbasy'] == nazwa_kielbasy].copy()
            przepis['Procent_Wagi_Miesa'] = przepis['Procent_Wagi_Miesa'].astype(str).str.replace(',', '.').astype(float)
            
            # Łączenie receptury z cenami z magazynu
            # Tworzymy słownik cen z magazynu (uśredniamy cenę, jeśli surowiec wpisano kilka razy)
            df_magazyn['Cena_za_kg'] = df_magazyn['Cena_za_kg'].astype(str).str.replace(',', '.').astype(float)
            ceny_surowcow = df_magazyn.groupby('Surowiec')['Cena_za_kg'].mean().to_dict()
            
            calkowity_koszt_partii = 0.0
            
            # Obliczanie wagi i kosztu dla każdego składnika
            szczegoly_kosztow = []
            for index, row in przepis.iterrows():
                skladnik = row['Skladnik']
                kategoria = row['Kategoria']
                procent = row['Procent_Wagi_Miesa']
                
                # Obliczamy wagę składnika w KG
                if kategoria == 'Mięso':
                    waga_skladnika_kg = waga_surowego_miesa * (procent / 100)
                else:
                    # Przyprawy - liczone jako naddatek do 100% mięsa, zamieniamy gramy na kg
                    waga_skladnika_kg = (waga_surowego_miesa * (procent / 100))
                
                # Szukamy ceny w magazynie (niewrażliwe na wielkość liter)
                cena_za_kg = 0.0
                for klucz_magazyn, cena in ceny_surowcow.items():
                    if klucz_magazyn.strip().lower() == skladnik.strip().lower():
                        cena_za_kg = cena
                        break
                        
                koszt_skladnika = waga_skladnika_kg * cena_za_kg
                calkowity_koszt_partii += koszt_skladnika
                
                szczegoly_kosztow.append({
                    "Składnik": skladnik,
                    "Zużycie (kg)": round(waga_skladnika_kg, 3),
                    "Cena z Magazynu (zł/kg)": round(cena_za_kg, 2),
                    "Koszt (zł)": round(koszt_skladnika, 2)
                })
            
            st.markdown("### 📊 Kalkulacja Kosztów Produkcji")
            st.dataframe(pd.DataFrame(szczegoly_kosztow), use_container_width=True, hide_index=True)
            
            if calkowity_koszt_partii == 0:
                st.error("⚠️ Błąd krytyczny: Żaden ze składników przepisu nie został znaleziony w Magazynie. Sprawdź, czy nazwy (np. 'Łopatka wieprzowa') są identyczne w obu zakładkach.")
            else:
                st.markdown("---")
                st.markdown("### ⚖️ Rozliczenie po obróbce i sprzedaż")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    waga_gotowa = st.number_input("Waga gotowego wyrobu (po pieczeniu/parzeniu w kg):", min_value=0.1, value=waga_surowego_miesa * 0.85, step=0.1)
                with col2:
                    cena_sprzedazy = st.number_input("Planowana cena sprzedaży (zł / kg):", min_value=1.0, value=55.0, step=1.0)
                
                # Obliczenia finansowe
                koszt_1kg_gotowego = calkowity_koszt_partii / waga_gotowa
                przychody_calkowite = waga_gotowa * cena_sprzedazy
                zysk_netto = przychody_calkowite - calkowity_koszt_partii
                marza_procent = (zysk_netto / przychody_calkowite) * 100 if przychody_calkowite > 0 else 0
                ubytek_procent = ((waga_surowego_miesa - waga_gotowa) / waga_surowego_miesa) * 100
                
                st.markdown("### 📈 Podsumowanie Finansowe")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Koszt całkowity surowców", f"{calkowity_koszt_partii:.2f} zł")
                m2.metric("Rzeczywisty koszt wytworzenia 1 kg", f"{koszt_1kg_gotowego:.2f} zł/kg", delta=f"Ubytek wagi: {ubytek_procent:.1f}%", delta_color="inverse")
                m3.metric("Całkowity zysk z partii", f"{zysk_netto:.2f} zł")
                m4.metric("Marża brutto", f"{marza_procent:.1f} %")
                
                if st.button("💾 Zapisz rozliczenie do raportów", type="primary"):
                    sheet_finanse.append_row([
                        wybrana_partia, nazwa_kielbasy, round(calkowity_koszt_partii, 2), 
                        round(waga_surowego_miesa, 2), round(waga_gotowa, 2), 
                        round(koszt_1kg_gotowego, 2), round(cena_sprzedazy, 2), round(zysk_netto, 2)
                    ])
                    st.success(f"Rozliczenie partii {wybrana_partia} zostało zapisane!")
                    
    except Exception as e:
        st.error(f"Błąd modułu finansowego: {e}")
