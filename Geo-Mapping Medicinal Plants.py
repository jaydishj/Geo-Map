import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, Fullscreen

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="Medicinal Plant GIS",
    page_icon="🌿",
    layout="wide"
)

# =====================================
# LOAD DATA
# =====================================
df = pd.read_excel(
    r"geopmappig.xlsx"
)

df.columns = df.columns.str.strip()

# Convert coordinates
df["Latitude"] = pd.to_numeric(
    df["Latitude"],
    errors="coerce"
)

df["Longitude"] = pd.to_numeric(
    df["Longitude"],
    errors="coerce"
)

df["Place"] = df["Place"].fillna("Unknown")

df = df.dropna(
    subset=["Latitude", "Longitude"]
)

# =====================================
# HEADER
# =====================================
st.title("🌿 AI Medicinal Plant Geo Mapping System")

st.markdown(
"""
Interactive Geographic Information System
for Medicinal Plant Distribution Mapping
"""
)

# =====================================
# SIDEBAR FILTERS
# =====================================
st.sidebar.header("🔍 Filters")

place = st.sidebar.selectbox(
    "Select Place",
    ["All"] + sorted(df["Place"].unique())
)

if place != "All":
    filtered_df = df[df["Place"] == place]
else:
    filtered_df = df.copy()

# =====================================
# STATISTICS
# =====================================
c1, c2, c3 = st.columns(3)

c1.metric(
    "🌱 Total Plants",
    len(filtered_df)
)

c2.metric(
    "📍 Locations",
    filtered_df["Place"].nunique()
)

c3.metric(
    "🗺️ Records",
    len(filtered_df)
)

# =====================================
# GOOGLE STYLE MAP
# =====================================
st.subheader("🗺️ Plant Distribution Map")

m = folium.Map(
    location=[20, 0],
    zoom_start=2,
    tiles=None
)

# OpenStreetMap
folium.TileLayer(
    "OpenStreetMap",
    name="Street Map"
).add_to(m)

# Satellite
folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    attr="Google",
    name="Google Satellite"
).add_to(m)

# Hybrid
folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google",
    name="Google Hybrid"
).add_to(m)

# Terrain
folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
    attr="Google",
    name="Google Terrain"
).add_to(m)

# Fullscreen
Fullscreen().add_to(m)

# Marker Cluster
marker_cluster = MarkerCluster().add_to(m)

# Add Plant Markers
for _, row in filtered_df.iterrows():

    popup = f"""
    <h4>{row['Plant_Name']}</h4>

    <b>Scientific Name:</b>
    {row['Scientific_Name']}<br>

    <b>Place:</b>
    {row['Place']}<br>

    <b>Latitude:</b>
    {row['Latitude']}<br>

    <b>Longitude:</b>
    {row['Longitude']}
    """

    folium.Marker(
        location=[
            row["Latitude"],
            row["Longitude"]
        ],
        popup=popup,
        tooltip=row["Plant_Name"],
        icon=folium.Icon(
            color="green",
            icon="leaf"
        )
    ).add_to(marker_cluster)

# Auto Zoom
if len(filtered_df) > 0:

    bounds = [
        [
            filtered_df["Latitude"].min(),
            filtered_df["Longitude"].min()
        ],
        [
            filtered_df["Latitude"].max(),
            filtered_df["Longitude"].max()
        ]
    ]

    m.fit_bounds(bounds)

# Layer Control
folium.LayerControl().add_to(m)

# Display Map
st_folium(
    m,
    height=700,
    width=None
)

# =====================================
# PLANT SEARCH
# =====================================
st.subheader("🌿 Plant Information")

selected_plant = st.selectbox(
    "Select Plant",
    sorted(filtered_df["Plant_Name"].unique())
)

plant = filtered_df[
    filtered_df["Plant_Name"] == selected_plant
].iloc[0]

st.markdown(f"""
### {plant['Plant_Name']}

**Plant ID:** {plant['Plant_ID']}

**Scientific Name:** {plant['Scientific_Name']}

**Place:** {plant['Place']}

**Latitude:** {plant['Latitude']}

**Longitude:** {plant['Longitude']}
""")

# =====================================
# DATA TABLE
# =====================================
st.subheader("📋 Complete Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True
)
