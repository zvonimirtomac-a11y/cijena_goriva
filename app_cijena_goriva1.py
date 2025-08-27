import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from st_aggrid import AgGrid, GridOptionsBuilder

st.title("⛽ Cijena goriva")
st.markdown("Autor: ZT")

boje = {
    "Benzin": "#008000",
    "Dizel": "#222222",
    "Auto plin": "#00BFFF",
    "Lož ulje": "#800000",
    "Plavi dizel": "#008080",
    "Plinske boce": "#FFA500"
}

url = "https://www.hak.hr/info/cijene-goriva/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

tables = pd.read_html(str(soup))
df_all = pd.concat(tables, ignore_index=True)

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

df_all['Gorivo_normalizirano'] = df_all['Gorivo'].apply(normalize_text)

def kategoriziraj_gorivo(naziv):
    if 'eurodizel plavi' in naziv or 'plavi dizel' in naziv:
        return 'Plavi dizel'
    elif 'dizel' in naziv:
        return 'Dizel'
    elif 'eurosuper' in naziv:
        return 'Benzin'
    elif 'autoplin' in naziv:
        return 'Autoplin'
    elif 'lož ulje' in naziv:
        return 'Lož ulje'
    elif 'unp' in naziv:
        return 'Plinske boce'
    else:
        return None

df_all['Kategorija'] = df_all['Gorivo_normalizirano'].apply(kategoriziraj_gorivo)

kategorije_kljucne = {
    "Benzin": "eurosuper",
    "Dizel": "dizel",
    "Autoplin": "autoplin",
    "Lož ulje": "lož ulje",
    "Plavi dizel": "plavi dizel",
    "Plinske boce": "unp"
}

df_all = df_all[df_all['Kategorija'].notnull()]

izbor_kategorije = st.selectbox(
    "Odaberi kategoriju goriva:",
    list(kategorije_kljucne.keys()),
    key="kategorija_select"
)

filtered = df_all[df_all['Kategorija'] == izbor_kategorije]

filtered_reset = filtered.drop(columns=['Gorivo_normalizirano',"Medijan"]).reset_index(drop=True)

gb = GridOptionsBuilder.from_dataframe(filtered_reset)
gb.configure_default_column(resizable=True, filter=True, sortable=True)
gb.configure_grid_options(domLayout='normal')
grid_options = gb.build()

AgGrid(filtered_reset, gridOptions=grid_options, enable_enterprise_modules=False, fit_columns_on_grid_load=True)

footer_text = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f0f2f6;
    color: #555;
    text-align: center;
    padding: 5px;
    font-size: 12px;
}
</style>
<div class="footer">
    Podaci o cijenama goriva preuzeti su s web stranice Hrvatskog autokluba (www.hak.hr) i portala Ministarstva gospodarstva (www.mzoe-gor.hr). Podaci su informativnog karaktera.
    Razvoj aplikacije podržan uz pomoć AI asistenta (Perplexity AI)
</div>
"""

st.markdown(footer_text, unsafe_allow_html=True)

