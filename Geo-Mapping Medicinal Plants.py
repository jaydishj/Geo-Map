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
df = pd.read_excel(r"geopmappig.xlsx")
df.columns = df.columns.str.strip()

# Convert coordinates
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df["Place"] = df["Place"].fillna("Unknown")
df = df.dropna(subset=["Latitude", "Longitude"])

# =====================================
# AUTO DETECT FAMILY COLUMN
# =====================================
family_col = None
possible_names = ["Family", "family", "Family_Name", "Plant_Family", 
                 "Taxonomic_Family", "Family Name"]

for col in df.columns:
    if any(name.lower() in col.lower() for name in possible_names):
        family_col = col
        break

# =====================================
# HEADER
# =====================================
st.title("🌿 AI Medicinal Plant Geo Mapping System")
st.markdown("Interactive Geographic Information System for Medicinal Plant Distribution Mapping")

# =====================================
# SIDEBAR FILTERS
# =====================================
st.sidebar.header("🔍 Filters")

# Place Filter
place = st.sidebar.selectbox(
    "Select Place",
    ["All"] + sorted(df["Place"].unique())
)

# Family Filter (Top 20)
if family_col:
    family_counts = df[family_col].value_counts().head(20)
    top_20_families = sorted(family_counts.index.dropna().astype(str).tolist())
    
    selected_families = st.sidebar.multiselect(
        f"Select Family (Top 20) - [{family_col}]",
        options=top_20_families,
        default=[],
        help=f"Using column: {family_col}"
    )
else:
    selected_families = []
    st.sidebar.warning("⚠️ Family column not detected. Add one of: Family, Family_Name, etc.")

# Plant Name Search
plant_search = st.sidebar.text_input("🔎 Search Plant Name", placeholder="Type plant name...")

# =====================================
# APPLY FILTERS
# =====================================
filtered_df = df.copy()

if place != "All":
    filtered_df = filtered_df[filtered_df["Place"] == place]

if selected_families and family_col:
    filtered_df = filtered_df[filtered_df[family_col].isin(selected_families)]

if plant_search:
    filtered_df = filtered_df[
        filtered_df["Plant_Name"].str.contains(plant_search, case=False, na=False)
    ]

# =====================================
# STATISTICS
# =====================================
c1, c2, c3 = st.columns(3)
c1.metric("🌱 Total Plants", len(filtered_df))
c2.metric("📍 Locations", filtered_df["Place"].nunique())
c3.metric("🗺️ Records", len(filtered_df))

# =====================================
# MAP
# =====================================
st.subheader("🗺️ Plant Distribution Map")
m = folium.Map(location=[20, 0], zoom_start=2, tiles=None)

folium.TileLayer("OpenStreetMap", name="Street Map").add_to(m)
folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google", name="Google Satellite").add_to(m)
folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google", name="Google Hybrid").add_to(m)
folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}", attr="Google", name="Google Terrain").add_to(m)

Fullscreen().add_to(m)
marker_cluster = MarkerCluster().add_to(m)

for _, row in filtered_df.iterrows():
    family_val = row.get(family_col, 'N/A') if family_col else 'N/A'
    popup = f"""
    <h4>{row['Plant_Name']}</h4>
    <b>Scientific Name:</b> {row.get('Scientific_Name', 'N/A')}<br>
    <b>Family:</b> {family_val}<br>
    <b>Place:</b> {row['Place']}<br>
    <b>Lat:</b> {row['Latitude']} | <b>Lon:</b> {row['Longitude']}
    """
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=popup,
        tooltip=row["Plant_Name"],
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(marker_cluster)

if len(filtered_df) > 0:
    bounds = [
        [filtered_df["Latitude"].min(), filtered_df["Longitude"].min()],
        [filtered_df["Latitude"].max(), filtered_df["Longitude"].max()]
    ]
    m.fit_bounds(bounds)

folium.LayerControl().add_to(m)
st_folium(m, height=700, width=None)

# Rest of the code (Plant Info + Table) remains same
st.subheader("🌿 Plant Information")
if len(filtered_df) > 0:
    selected_plant = st.selectbox("Select Plant", sorted(filtered_df["Plant_Name"].unique()))
    plant = filtered_df[filtered_df["Plant_Name"] == selected_plant].iloc[0]
    family_val = plant.get(family_col, 'N/A') if family_col else 'N/A'
    
    st.markdown(f"""
    ### {plant['Plant_Name']}
    **Scientific Name:** {plant.get('Scientific_Name', 'N/A')}  
    **Family:** {family_val}  
    **Place:** {plant['Place']}
    """)
else:
    st.warning("No plants found matching your filters.")

st.subheader("📋 Complete Dataset")
st.dataframe(filtered_df, use_container_width=True)
