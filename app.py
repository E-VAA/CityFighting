import pandas as pd
import requests
import folium
import streamlit as st
from streamlit_folium import st_folium
from streamlit_folium import folium_static
from bs4 import BeautifulSoup
import geopandas as gpd
import plotly.graph_objects as go
import pydeck as pdk
import os

################################################################################
### TITRE DE L'APPLICATION ###
st.set_page_config(layout="wide")
st.title("City Fighting - Comparaison des villes")
st.write("Liste des villes restreintes à celles de plus 20000 habitants")

################################################################################
### CHARGEMENT DES DONNÉES ###
df_villes = pd.read_csv("data/communes-france-2025.csv", sep=';', encoding='utf-8',dtype={"code_insee": str}) 
evol = pd.read_csv("data/data_age_graph.csv", sep=';', encoding='utf-8', dtype={"code_insee": str}) 
climat = gpd.read_file("data/Communes.geojson")
Logements = pd.read_csv("data/base-ic-logement-2021.CSV", sep=";", encoding='ISO-8859-1')
lieux_visite = pd.read_csv("data/base-des-lieux-et-des-equipements-culturels.csv", sep=";")
salaires = pd.read_csv("data/salaireNET.csv", sep=";")

################################################################################
### FONCTION : RÉCUPÉRATION DES DONNÉES ###
@st.cache_data
def get_wikipedia_data(city):
    url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{city}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        city_data = {
            "titre": data.get("title", "N/A"),
            "description": data.get("description", "N/A"),
            "extrait": data.get("extract", "N/A"),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", "N/A"),
        }

        # Scraping des informations complémentaires
        page_url = city_data["url"]
        page_response = requests.get(page_url)
        
        if page_response.status_code == 200:
            soup = BeautifulSoup(page_response.text, "html.parser")
            infobox = soup.find("table", {"class": "infobox"})
            if infobox:
                rows = infobox.find_all("tr")
                for row in rows:
                    header = row.find("th")
                    value = row.find("td")
                    if header and value:
                        header_text = header.get_text(strip=True)
                        value_text = value.get_text(strip=True)
                        if header_text == "Région":
                            city_data["region"] = value_text
                        elif header_text == "Département":
                            city_data["department"] = value_text
                        elif header_text == "Superficie":
                            city_data["area"] = value_text
                        elif header_text == "Coordonnées":
                            city_data["coordinates"] = value_text
        return city_data
    else:
        return {"error": "Ville non trouvée sur Wikipedia"}

def get_weather(city):
    city = city.lower().replace(" ", "-")  # Adapter le nom de la ville pour l'API
    url = f"https://prevision-meteo.ch/services/json/{city}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "errors" not in data:
            forecast_data = {
                "temp": data["current_condition"]["tmp"],
                "humidity": data["current_condition"]["humidity"],
                "wind_speed": data["current_condition"]["wnd_spd"],
                "wind_dir": data["current_condition"]["wnd_dir"],
                "pressure": data["current_condition"]["pressure"],
                "condition": data["current_condition"]["condition"],
                "icon": data["current_condition"]["icon"],
                "sunrise": data["city_info"]["sunrise"],
                "sunset": data["city_info"]["sunset"],
            }
            for i in range(1, 4):  # Prévisions J+1 à J+3
                day_key = f"fcst_day_{i}"
                if day_key in data:
                    forecast_data[day_key] = data[day_key]
            return forecast_data
    return None
def display_weather(city, weather_data, col):
    if weather_data:
        with col:
            st.markdown(f"### 🌤️ {city}")
            icone_col, cond_col = st.columns([1, 3])
            with icone_col:
                st.image(weather_data["icon"], width=60)
            with cond_col:
                st.markdown(f"**☁️ Conditions :** _{weather_data['condition'].capitalize()}_")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🌡 Température", f"{weather_data['temp']} °C")
                st.metric("💨 Vent", f"{weather_data['wind_speed']} km/h")
                st.metric("💧 Humidité", f"{weather_data['humidity']}%")
            with col2:
                st.metric("🌅 Lever du soleil", weather_data['sunrise'])
                st.metric("🌇 Coucher du soleil", weather_data['sunset'])
    else:
        with col:
            st.error(f"❌ Météo non disponible pour {city}.")           
def display_forecast(city, weather_data, col):
    if weather_data:
        with col:
            st.markdown(f"### 📆 Prévisions - {city}")
            for day in range(1, 4):
                day_key = f"fcst_day_{day}"
                if day_key in weather_data:
                    day_data = weather_data[day_key]
                    st.markdown(
                        f"""
                        <div style="border: 1px solid #ccc; border-radius: 10px; padding: 10px; margin-bottom: 15px; background-color: #f9f9f9;">
                            <h4 style="margin-bottom: 5px;">📅 {day_data['day_long']} ({day_data['date']})</h4>
                            <img src="{day_data['icon']}" width="50" style="margin-bottom: 10px;" />
                            <p>🌡️ <b>Température</b> : {day_data['tmin']} °C → {day_data['tmax']} °C</p>
                            <p>📝 <b>Conditions</b> : {day_data['condition']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True)
    else:
        with col:
            st.warning(f"Pas de prévisions disponibles pour {city}.")
def display_forecasts_for_two_cities(city1, weather1, city2, weather2):
    col1, col_mid, col2 = st.columns([5, 1, 5])
    # On passe bien col1 et col2 ici 👇
    display_forecast(city1, weather1, col1)
    with col_mid:
        st.markdown(
            """
            <div style="height: 100%; width: 2px; background-color: #ccc; margin: auto;"></div>
            """,
            unsafe_allow_html=True,)
    display_forecast(city2, weather2, col2)

def get_commune_data(code_insee):
    url = f"https://geo.api.gouv.fr/communes?code={code_insee}&fields=code,nom,contour,centre"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            commune_data = data[0]
            contour = commune_data.get('contour', {}).get('coordinates', None)
            centre = commune_data.get('centre', {}).get('coordinates', None)
            if contour:
                if isinstance(contour[0][0][0], list):  # Vérifier si c'est un MultiPolygon
                    contour = contour[0][0]  # Prendre le premier polygone
                elif isinstance(contour[0][0], list):  # Vérifier si c'est un Polygon
                    contour = contour[0]  # Retourner directement le polygone
            return contour, centre
    return None, None


################################################################################
### CRÉATION DES ONGLETS ###
tabs = st.tabs(["Données Générales", "Météo et Climat", "Logements", "Emploi", "Culture et Tourisme", "Sources"])

### ONGLET 1 : Données Générales et Données Météo ###
### INTERFACE : SÉLECTION DES VILLES ###
with tabs[0]:
    df_villes['code_insee'] = df_villes['code_insee'].apply(lambda x: x.zfill(5) if len(x) == 4 else x)
    villes_filtre = df_villes[df_villes['population'] > 20000]
    villes_disponibles = villes_filtre['nom_standard'].unique()

    col1, col2 = st.columns(2)
    with col1:
        ville1 = st.selectbox("Sélectionnez la première ville", villes_disponibles)

    ville2_options = [v for v in villes_disponibles if v != ville1]
    with col2:
        ville2 = st.selectbox("Sélectionnez la deuxième ville", ville2_options)

    # Stockage de l'état du bouton "Comparer"
    if "compare_clicked" not in st.session_state:
        st.session_state.compare_clicked = False

    if st.button("Comparer"):
        st.session_state.compare_clicked = True

    st.markdown("---")
    st.subheader("Données Générales")

    if not st.session_state.compare_clicked:
        st.info("Veuillez sélectionner deux villes pour afficher les données des deux villes.")
    else:
        ### RÉCUPÉRATION DES DONNÉES ###
        info_v1 = get_wikipedia_data(ville1)
        info_v2 = get_wikipedia_data(ville2)

        pop_ville1 = df_villes[df_villes['nom_standard'] == ville1]['population'].values[0]
        pop_ville2 = df_villes[df_villes['nom_standard'] == ville2]['population'].values[0]

        col1, col2 = st.columns(2)

        ### AFFICHAGE DES INFORMATIONS ET DES CARTES ###
        with col1:
            st.subheader(ville1)
            code_v1 = df_villes[df_villes['nom_standard'] == ville1]["code_insee"].values[0]
            if "error" not in info_v1:
                st.write(f"**Code géographique INSEE :** {code_v1}")
                st.write(f"**Région**: {info_v1.get('region', 'Non disponible')}")
                st.write(f"**Département**: {info_v1.get('department', 'Non disponible')}")
                st.write(f"**Superficie**: {info_v1.get('area', 'Non disponible')}")
                st.write(f"**Population**: {pop_ville1 if pop_ville1 != 'NaN' else 'Non disponible'}")
                st.markdown(f"[Voir sur Wikipedia]({info_v1['url']})")

            code_insee_v1 = code_v1
            contour_1, centre_1 = get_commune_data(code_insee_v1)
            if contour_1 and centre_1:
                m_1 = folium.Map(location=[centre_1[1], centre_1[0]], zoom_start=11)
                folium.Polygon(locations=[[coord[1], coord[0]] for coord in contour_1], color="darkred", fill=True, fill_opacity=0.2).add_to(m_1)
                folium_static(m_1, width=700, height=400)

        with col2:
            st.subheader(ville2)
            code_v2 = df_villes[df_villes['nom_standard'] == ville2]["code_insee"].values[0]
            if "error" not in info_v2:
                st.write(f"**Code géographique INSEE :** {code_v2}")
                st.write(f"**Région**: {info_v2.get('region', 'Non disponible')}")
                st.write(f"**Département**: {info_v2.get('department', 'Non disponible')}")
                st.write(f"**Superficie**: {info_v2.get('area', 'Non disponible')}")
                st.write(f"**Population**: {pop_ville2 if pop_ville2 != 'NaN' else 'Non disponible'}")
                st.markdown(f"[Voir sur Wikipedia]({info_v2['url']})")

            code_insee_v2 = code_v2
            contour_2, centre_2 = get_commune_data(code_insee_v2)
            if contour_2 and centre_2:
                m_2 = folium.Map(location=[centre_2[1], centre_2[0]], zoom_start=11)
                folium.Polygon(locations=[[coord[1], coord[0]] for coord in contour_2], color="darkred", fill=True, fill_opacity=0.2).add_to(m_2)
                folium_static(m_2, width=700, height=400)
    
        # Ajout du graphique d'évolution de la population
        st.markdown("---")
        st.subheader("📈 Évolution de la population")

        evol['code_insee'] = evol['code_insee'].apply(lambda x: x.zfill(5) if len(x) == 4 else x)
        evol_ville1 = evol[evol['code_insee'] == code_v1]
        evol_ville2 = evol[evol['code_insee'] == code_v2]

        annees = [str(annee) for annee in evol_ville1.columns if annee.isdigit()]
    
        pop_ville1 = [float(evol_ville1[annee].values[0]) if not pd.isna(evol_ville1[annee].values[0]) else None for annee in annees]
        pop_ville2 = [float(evol_ville2[annee].values[0]) if not pd.isna(evol_ville2[annee].values[0]) else None for annee in annees]

        # Tracer le graphique de l'évolution de la population
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=annees, y=pop_ville1, mode='lines+markers', name=ville1, line=dict(color='royalblue')))
        fig.add_trace(go.Scatter(x=annees, y=pop_ville2, mode='lines+markers', name=ville2, line=dict(color='firebrick')))

        fig.update_layout(
            title="Évolution de la population (1876 - 2022)",
            xaxis_title="Année",
            yaxis_title="Population",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

################################################################################
### ONGLET 2 : Données Météologiques et Climatiques ###
with tabs[1]:
    st.subheader("Météo actuelle dans chaque ville")
    
    if not st.session_state.get("compare_clicked", False):
        st.info("Veuillez d'abord sélectionner deux villes pour afficher les données météo.")
    else:
        col1, col2 = st.columns(2)

        # Récupération des données météo
        col1, col2 = st.columns(2)

        weather_v1 = get_weather(ville1)
        weather_v2 = get_weather(ville2)

        display_weather(ville1, weather_v1, col1)
        display_weather(ville2, weather_v2, col2)

        st.markdown("---")
        st.subheader("Prévisions sur 3 jours")
        display_forecasts_for_two_cities(ville1, weather_v1, ville2, weather_v2)
        
        st.markdown("---")
        st.subheader("Climat")
        #Légende 
        st.markdown("""
        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; padding: 10px; font-size: 14px; background-color: #f9f9f9; border: 1px solid #ccc; border-radius: 8px;">
            <div><i style="background: #CD5C5C; width: 18px; height: 18px; display: inline-block;"></i> Méditerranéen</div>
            <div><i style="background: #FF8C00; width: 18px; height: 18px; display: inline-block;"></i> Bassin du Sud-Ouest</div>
            <div><i style="background: #B3E59A; width: 18px; height: 18px; display: inline-block;"></i> Méditerranéen altéré</div>
            <div><i style="background: #4E9F3D; width: 18px; height: 18px; display: inline-block;"></i> Océanique</div>
            <div><i style="background: #66CDAA; width: 18px; height: 18px; display: inline-block;"></i> Océanique altéré</div>
            <div><i style="background: #97FFFF; width: 18px; height: 18px; display: inline-block;"></i> Océanique dégradé</div>
            <div><i style="background: #00BFFF; width: 18px; height: 18px; display: inline-block;"></i> Semi-continental</div>
            <div><i style="background: #00008B; width: 18px; height: 18px; display: inline-block;"></i> Montagne</div>
            <div><i style="background: red; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> Ville étudiée</div>
            <div><i style="background: blue; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> Ville de comparaison</div>
        </div>
        """, unsafe_allow_html=True)

        # carte
        cols = {
            "8": "#CD5C5C",
            "7": "#FF8C00",
            "6": "#B3E59A",
            "5": "#4E9F3D",
            "4": "#66CDAA",
            "3": "#97FFFF",
            "2": "#00BFFF",
            "1": "#00008B"
        }

        m = folium.Map(location=[46.8, 2.5], zoom_start=6)

        folium.GeoJson(
            climat,
            style_function=lambda feature: {
                'fillColor': cols.get(str(feature['properties']['Type']), '#ffffff'),
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            }
        ).add_to(m)

        # Villes
        folium.Marker(
            location=[centre_1[1], centre_1[0]],
            popup=f"<b>{ville1}</b>",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

        folium.Marker(
            location=[centre_2[1], centre_2[0]],
            popup=f"<b>{ville2}</b>",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

        # affichage
        st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
        st_folium(m, width=700, height=500)
        st.markdown("</div>", unsafe_allow_html=True)

################################################################################
### ONGLET 3 : Données Logements ###
### ONGLET 3 : Données Logements ###
with tabs[2]:
    st.subheader("Logements")

    if not st.session_state.get("compare_clicked", False):
        st.info("Veuillez d'abord sélectionner deux villes pour afficher les logements.")
    else:
        Logements['CODGEO'] = Logements['CODGEO'].apply(lambda x: str(x).zfill(5) if len(str(x)) == 4 else str(x))
        logement_ville1 = Logements[Logements['CODGEO'] == code_v1]
        logement_ville2 = Logements[Logements['CODGEO'] == code_v2]

        if not logement_ville1.empty and not logement_ville2.empty:
            v1 = logement_ville1.iloc[0]
            v2 = logement_ville2.iloc[0]

            with st.expander("🏘️ Répartition des logements par catégorie"):
                data_cat = pd.DataFrame({
                    "Catégorie": ["Résidences principales", "Résidences secondaires / occasionnels", "Logements vacants"],
                    ville1: [v1["P21_RP"], v1["P21_RSECOCC"], v1["P21_LOGVAC"]],
                    ville2: [v2["P21_RP"], v2["P21_RSECOCC"], v2["P21_LOGVAC"]],
                })
                st.dataframe(data_cat)

            with st.expander("🏗️ Répartition des logements par type"):
                data_type = pd.DataFrame({
                    "Type": ["Maison", "Appartement"],
                    ville1: [v1["P21_MAISON"], v1["P21_APPART"]],
                    ville2: [v2["P21_MAISON"], v2["P21_APPART"]],
                })
                st.dataframe(data_type)

            with st.expander("📐 Répartition des logements par superficie"):
                data_surf = pd.DataFrame({
                    "Superficie": [
                        "Moins de 30 m²", "30 à 40 m²", "40 à 60 m²",
                        "60 à 80 m²", "80 à 100 m²", "100 à 120 m²", "120 m² ou plus"
                    ],
                    ville1: [
                        v1["P21_RP_M30M2"], v1["P21_RP_3040M2"], v1["P21_RP_4060M2"],
                        v1["P21_RP_6080M2"], v1["P21_RP_80100M2"], v1["P21_RP_100120M2"], v1["P21_RP_120M2P"]
                    ],
                    ville2: [
                        v2["P21_RP_M30M2"], v2["P21_RP_3040M2"], v2["P21_RP_4060M2"],
                        v2["P21_RP_6080M2"], v2["P21_RP_80100M2"], v2["P21_RP_100120M2"], v2["P21_RP_120M2P"]
                    ]
                })
                st.dataframe(data_surf)

            with st.expander("🧱 Répartition des logements par nombre de pièces"):
                data_pieces = pd.DataFrame({
                    "Nombre de pièces": ["1", "2", "3", "4", "5 ou +"],
                    ville1: [v1["P21_RP_1P"], v1["P21_RP_2P"], v1["P21_RP_3P"], v1["P21_RP_4P"], v1["P21_RP_5PP"]],
                    ville2: [v2["P21_RP_1P"], v2["P21_RP_2P"], v2["P21_RP_3P"], v2["P21_RP_4P"], v2["P21_RP_5PP"]],
                })
                st.dataframe(data_pieces)
        else:
            st.warning("Aucune donnée logement disponible pour au moins une des deux villes sélectionnées.")
        

################################################################################
### ONGLET 4 : Données Emploi ###
with tabs[3]:
    st.subheader("Emploi")

    if not st.session_state.get("compare_clicked", False):
        st.info("Veuillez d'abord sélectionner deux villes pour afficher les données sur l'emploi.")
    else:
        # Mapping ville -> CODGEO
        codgeo_ville1 = code_v1  # à implémenter
        codgeo_ville2 = code_v2
        row_v1 = salaires[salaires["CODGEO"] == code_v1]
        row_v2 = salaires[salaires["CODGEO"] == code_v2]

        if row_v1.empty or row_v2.empty:
            st.warning("Pas de données d'emploi disponibles pour une des deux villes.")
        else:
            st.markdown("### 💰 Salaires horaires nets moyens")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"{ville1}", f"{row_v1['SNHM22'].values[0]:.2f} € / h")
            with col2:
                st.metric(f"{ville2}", f"{row_v2['SNHM22'].values[0]:.2f} € / h")

            # Salaire par genre
            with st.expander("👥 Salaire par genre"):
                fig_sexe = go.Figure(data=[
                    go.Bar(name=ville1, x=["Femmes", "Hommes"], y=[row_v1["SNHMF22"].values[0], row_v1["SNHMH22"].values[0]]),
                    go.Bar(name=ville2, x=["Femmes", "Hommes"], y=[row_v2["SNHMF22"].values[0], row_v2["SNHMH22"].values[0]])
                ])
                fig_sexe.update_layout(
                    barmode='group',
                    title="Salaire par sexe (€ / h)",
                    xaxis_title="Sexe",
                    yaxis_title="Salaire net horaire (€)",
                    template="plotly_white"
                )
                st.plotly_chart(fig_sexe)

            # Salaire par tranche d'âge
            with st.expander("👴 Salaire par tranche d'âge"):
                fig_age = go.Figure(data=[
                    go.Bar(name=ville1, x=["18-25 ans", "26-50 ans", "50 ans et +"], y=[
                        row_v1["SNHM1822"].values[0], row_v1["SNHM2622"].values[0], row_v1["SNHM5022"].values[0]
                    ]),
                    go.Bar(name=ville2, x=["18-25 ans", "26-50 ans", "50 ans et +"], y=[
                        row_v2["SNHM1822"].values[0], row_v2["SNHM2622"].values[0], row_v2["SNHM5022"].values[0]
                    ])
                ])
                fig_age.update_layout(
                    barmode='group',
                    title="Salaire par tranche d'âge (€ / h)",
                    xaxis_title="Tranche d'âge",
                    yaxis_title="Salaire net horaire (€)",
                    template="plotly_white"
                )
                st.plotly_chart(fig_age)

            # Salaire par catégorie socioprofessionnelle
            with st.expander("💼 Salaire par catégorie socioprofessionnelle"):
                categories = ["Cadres", "Prof. intermédiaires", "Employés", "Ouvriers"]
                v1_cats = [row_v1["SNHMC22"].values[0], row_v1["SNHMP22"].values[0],
                        row_v1["SNHME22"].values[0], row_v1["SNHMO22"].values[0]]
                v2_cats = [row_v2["SNHMC22"].values[0], row_v2["SNHMP22"].values[0],
                        row_v2["SNHME22"].values[0], row_v2["SNHMO22"].values[0]]

                fig_cat = go.Figure(data=[
                    go.Bar(name=ville1, x=categories, y=v1_cats),
                    go.Bar(name=ville2, x=categories, y=v2_cats)
                ])
                fig_cat.update_layout(
                    barmode='group',
                    title="Salaire par catégorie socioprofessionnelle (€ / h)",
                    xaxis_title="Catégorie",
                    yaxis_title="Salaire net horaire (€)",
                    template="plotly_white"
                )
                st.plotly_chart(fig_cat)
        

################################################################################    
### ONGLET 5 : Données Culture et Données Tourisme ###
with tabs[4]:
    st.subheader("Culture et Tourisme")

    if not st.session_state.get("compare_clicked", False):
        st.info("Veuillez d'abord sélectionner deux villes pour afficher les lieux culturels.")
    else:
        if ville1 and ville2 and 'centre_1' in locals() and 'centre_2' in locals():
            # Filtrer les lieux par ville
            cult_ville1 = lieux_visite[lieux_visite['code_insee'] == code_v1]
            cult_ville2 = lieux_visite[lieux_visite['code_insee'] == code_v2]

            col1, col2 = st.columns(2)

            # --- Carte pour Ville 1 ---
            with col1:
                if not cult_ville1.empty:
                    st.subheader(f"Lieux culturels à {ville1}")
                    m_ville1 = folium.Map(location=[centre_1[1], centre_1[0]], zoom_start=12)
                    for _, lieu in cult_ville1.iterrows():
                        if pd.notnull(lieu['Latitude']) and pd.notnull(lieu['Longitude']):
                            folium.Marker(
                                location=[lieu['Latitude'], lieu['Longitude']],
                                popup=lieu['Nom'],
                                icon=folium.Icon(color='blue', icon='info-sign')
                            ).add_to(m_ville1)
                    folium_static(m_ville1, width=600, height=400)

                    # Sélecteur et infos
                    lieu_select = st.selectbox(f"Sélectionnez un lieu à {ville1}", cult_ville1['Nom'].unique())
                    lieu_info = cult_ville1[cult_ville1['Nom'] == lieu_select].iloc[0]

                    st.markdown(f"**Adresse** : {lieu_info['Adresse']}")
                    fonctions = [lieu_info.get(f'Fonction_{i}') for i in range(1, 5) if pd.notnull(lieu_info.get(f'Fonction_{i}'))]
                    if fonctions:
                        st.markdown("**Fonction(s)** : " + ", ".join(fonctions))

                    if pd.notnull(lieu_info.get('Type_de_cinema')):
                        st.markdown("🎬 **Cinéma**")
                        st.write(f"Type : {lieu_info['Type_de_cinema']}")
                        st.write(f"Multiplexe : {lieu_info['Multiplexe']}")
                        st.write(f"Fauteuils : {lieu_info['Nombre_fauteuils_de_cinema']}")
                        st.write(f"Écrans : {lieu_info['Nombre_ecrans']}")
                    elif pd.notnull(lieu_info.get('Organisme_Siege_du_theatre')):
                        st.markdown("🎭 **Théâtre**")
                        st.write(f"Organisme : {lieu_info['Organisme_Siege_du_theatre']}")
                        st.write(f"Salles : {lieu_info['Nombre_de_salles_de_theatre']}")
                        st.write(f"Jauge : {lieu_info['Jauge_du_theatre']}")
                    elif pd.notnull(lieu_info.get("Code_du_reseau_de_Bibliotheques")):
                        st.markdown("📚 **Bibliothèque**")
                        st.write(f"Réseau : {lieu_info['Nom_du_Reseau_de_Bibliotheques']}")
                        st.write(f"Code réseau : {lieu_info['Code_du_reseau_de_Bibliotheques']}")

                else:
                    st.info(f"Aucun lieu culturel trouvé pour {ville1}.")

            # --- Carte pour Ville 2 ---
            with col2:
                if not cult_ville2.empty:
                    st.subheader(f"Lieux culturels à {ville2}")
                    m_ville2 = folium.Map(location=[centre_2[1], centre_2[0]], zoom_start=12)
                    for _, lieu in cult_ville2.iterrows():
                        if pd.notnull(lieu['Latitude']) and pd.notnull(lieu['Longitude']):
                            folium.Marker(
                                location=[lieu['Latitude'], lieu['Longitude']],
                                popup=lieu['Nom'],
                                icon=folium.Icon(color='green', icon='info-sign')
                            ).add_to(m_ville2)
                    folium_static(m_ville2, width=600, height=400)

                    # Sélecteur et infos
                    lieu_select = st.selectbox(f"Sélectionnez un lieu à {ville2}", cult_ville2['Nom'].unique())
                    lieu_info = cult_ville2[cult_ville2['Nom'] == lieu_select].iloc[0]

                    st.markdown(f"**Adresse** : {lieu_info['Adresse']}")
                    fonctions = [lieu_info.get(f'Fonction_{i}') for i in range(1, 5) if pd.notnull(lieu_info.get(f'Fonction_{i}'))]
                    if fonctions:
                        st.markdown("**Fonction(s)** : " + ", ".join(fonctions))

                    if pd.notnull(lieu_info.get('Type_de_cinema')):
                        st.markdown("🎬 **Cinéma**")
                        st.write(f"Type : {lieu_info['Type_de_cinema']}")
                        st.write(f"Multiplexe : {lieu_info['Multiplexe']}")
                        st.write(f"Fauteuils : {lieu_info['Nombre_fauteuils_de_cinema']}")
                        st.write(f"Écrans : {lieu_info['Nombre_ecrans']}")
                    elif pd.notnull(lieu_info.get('Organisme_Siege_du_theatre')):
                        st.markdown("🎭 **Théâtre**")
                        st.write(f"Organisme : {lieu_info['Organisme_Siege_du_theatre']}")
                        st.write(f"Salles : {lieu_info['Nombre_de_salles_de_theatre']}")
                        st.write(f"Jauge : {lieu_info['Jauge_du_theatre']}")
                    elif pd.notnull(lieu_info.get("Code_du_reseau_de_Bibliotheques")):
                        st.markdown("📚 **Bibliothèque**")
                        st.write(f"Réseau : {lieu_info['Nom_du_Reseau_de_Bibliotheques']}")
                        st.write(f"Code réseau : {lieu_info['Code_du_reseau_de_Bibliotheques']}")
                else:
                    st.info(f"Aucun lieu culturel trouvé pour {ville2}.")
        else:
            st.warning("Veuillez d'abord sélectionner deux villes pour afficher les lieux culturels.")

################################################################################
### ONGLET 6 : Sources ###
with tabs[5]:
    st.subheader("Sources")
    st.write("Voici les sources utilisées pour alimenter les données affichées dans cette application :")
    st.markdown("---")

    ####################
    # Donnéess Générales
    st.subheader("🌐 Données Générales")
    st.markdown("""
    - **Population et Évolution (communes-france-2025 / data_age_graph)**  
    Source : INSEE  

    - **Données des villes**  
    API Wikipédia  
    (https://fr.wikipedia.org/api/rest_v1/page/summary/{city})- A la place de "city", rentrer le nom d'une ville

    - **Contours des communes**  
    API geo.api.gouv.fr  
    (https://geo.api.gouv.fr/communes?code={CODGEO}&fields=code,nom,contour,centre)- A la place de "CODGEO", rentrer le code INSEE d'une ville
    """)

    #################
    # Météo et Climat
    st.subheader("⛅ Météo et Climat")
    st.markdown("""
    - **Météo actuelle**  
    API : prevision-meteo.ch  
    (https://prevision-meteo.ch/services/json/{city}) - A la place de "city", rentrer le nom d'une ville
    """)

    ###########
    # Logements
    st.subheader("🏘️ Logements")
    st.markdown("""
    - **Données logement (base-ic-logement-2021)**  
    INSEE  
    (https://www.insee.fr/fr/statistiques/8268838)
    """)

    ########
    # Emploi
    st.subheader("💼 Emploi")
    st.markdown("""
    - **Salaires nets par commune (cc_bases-tous-salaries_2022_COM)**  
    Source : INSEE  
    (https://www.insee.fr/fr/statistiques/2021266)
    """)

    #####################
    # Culture et Tourisme
    st.subheader("🎭 Culture et Tourisme")
    st.markdown("""
    - **Lieux et équipements culturels (base-des-lieux-et-des-equipements-culturels)**  
    Source : data.gouv  
    (https://www.data.gouv.fr/fr/datasets/base-des-lieux-et-equipements-culturels-basilic/)
    """)