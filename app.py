import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from folium import plugins

# === Configs ===
API_URL = 'https://google-maps-extractor2.p.rapidapi.com/autocomplete'
HEADERS = {
    'x-rapidapi-host': 'google-maps-extractor2.p.rapidapi.com',
    'x-rapidapi-key': '0afa000b92mshd9791e35141c16cp1ab413jsnc56434016629'
}
ICON_URLS = {
    'Yoda': 'https://upload.wikimedia.org/wikipedia/en/9/9b/Yoda_Empire_Strikes_Back.png',
    'Darth Vader': 'https://upload.wikimedia.org/wikipedia/en/7/76/Darth_Vader.jpg',
    'R2-D2': 'https://upload.wikimedia.org/wikipedia/en/3/39/R2-D2_Droid.png'
}

# === Service ===
def buscar_local(termo):
    params = {'query': termo, 'lang': 'en', 'country': 'us'}
    response = requests.get(API_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    return []

# === UI ===
st.set_page_config(page_title="StarWars Map Marker", layout="wide")
st.title("🛰️ StarWars Map Marker")

termo = st.text_input("🔍 Buscar local:", "Los Angeles")
icone_selecionado = st.selectbox("👾 Escolha um ícone StarWars:", list(ICON_URLS.keys()))
uploaded_image = st.file_uploader("📷 Enviar imagem de sobreposição (opcional)", type=['png', 'jpg', 'jpeg'])

locais = buscar_local(termo) if termo else []

# === Mapa ===
if locais:
    lat = locais[0]['latitude']
    lon = locais[0]['longitude']
    mapa = folium.Map(location=[lat, lon], zoom_start=13, tiles='Stamen Terrain')
    folium.TileLayer('Stamen Toner').add_to(mapa)
    folium.TileLayer('Stamen Watercolor').add_to(mapa)
    folium.LayerControl().add_to(mapa)

    if uploaded_image is not None:
        import base64
        from PIL import Image
        import io

        image = Image.open(uploaded_image)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        encoded = base64.b64encode(img_byte_arr.getvalue()).decode()
        image_url = f"data:image/png;base64,{encoded}"

        folium.raster_layers.ImageOverlay(
            image_url,
            bounds=[[lat - 0.02, lon - 0.02], [lat + 0.02, lon + 0.02]],
            opacity=0.6
        ).add_to(mapa)

    for loc in locais:
        folium.Marker(
            location=[loc['latitude'], loc['longitude']],
            popup=loc['title'],
            icon=folium.CustomIcon(
                icon_image=ICON_URLS[icone_selecionado],
                icon_size=(40, 40)
            )
        ).add_to(mapa)

    draw = plugins.Draw(export=True)
    draw.add_to(mapa)

    st_folium(mapa, width=1000, height=600)
else:
    st.info("🔍 Digite um termo para busca.")
