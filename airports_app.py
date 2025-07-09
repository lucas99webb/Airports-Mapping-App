import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk

# Cache the data loading
@st.cache_data
def load_data():
    regions = pd.read_csv('regions.csv')
    countries = pd.read_csv('countries.csv')
    airports = pd.read_csv('airports.csv')

    # Clean and join
    airports = airports.iloc[:, :-3]
    regions = regions.rename(columns={'name': 'RegionName', 'code': 'iso_region'})
    countries = countries.rename(columns={'name': 'CountryName', 'code': 'iso_country'})
    airports = airports.merge(regions[['iso_region', 'RegionName']], on='iso_region', how='left')
    airports = airports.merge(countries[['iso_country', 'CountryName']], on='iso_country', how='left')
    airports = airports[airports['type'].isin(['small_airport', 'medium_airport', 'large_airport'])]

    return airports


# Load data
airports = load_data()

# App UI
st.header('Airports App')

# Filter by airport type
st.subheader("Filter by Airport Type")
type_options = ['All'] + sorted(airports['type'].dropna().unique().tolist())
selected_type = st.selectbox("Select airport type:", type_options)

filtered_airports = airports if selected_type == 'All' else airports[airports['type'] == selected_type]
st.info(f"Found {len(filtered_airports)} airports" + (f" of type '{selected_type}'." if selected_type != 'All' else "."))
st.dataframe(filtered_airports)

# Map display button
if st.button("Show Airport Locations on Map"):
    st.subheader("Airport Locations on Map")
    map_data = filtered_airports.dropna(subset=['latitude_deg', 'longitude_deg'])

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position='[longitude_deg, latitude_deg]',
        get_radius=10000,
        get_fill_color=[225, 225, 0, 180],
        get_line_color=[0, 0, 0],
        line_width_min_pixels=1,
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(
        latitude=52,
        longitude=0,
        zoom=5,
        pitch=0
    )

    tooltip = {
        "html": "<b>{name}</b><br>IATA Code: {iata_code}",
        "style": {"backgroundColor": "white", "color": "black"}
    }

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip,
    map_style='mapbox://styles/mapbox/satellite-streets-v12'
    ))

