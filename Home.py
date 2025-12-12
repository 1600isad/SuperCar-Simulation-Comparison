# Car Project Application (gang gang by Isaac Acuna hahahahahahahaaa)

import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
#////////////////////CSS styling for the app//////////////////////
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=GoLane:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'GoLane', sans-serif;
        letter-spacing: 0.5px;
    }

    /* Optional: tweak Streamlit elements for a sleeker car-dashboard feel */
    .stApp {
        background-color: #0A0A0A;
        color: #EAEAEA;
    }

    .stSidebar {
        background-color: #121212;
    }

    .stButton>button {
        background-color: #00BFFF;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #0099CC;
    }
    </style>
""", unsafe_allow_html=True)
#///////////////////////////////////////////////////////////////

st.set_page_config(page_title="Car Performance Visualizer", page_icon="🏎", layout="wide")

# ---------------------------
# Load and cache data
# ---------------------------
@st.cache_data
def load_data():
    return pd.read_csv("cars.csv")

cars = load_data()

# ---------------------------
# Sidebar — select cars
# ---------------------------
st.sidebar.header("Compare Cars")
car1_name = st.sidebar.selectbox("Select Car 1", cars["name"])
car2_name = st.sidebar.selectbox("Select Car 2", cars["name"], index=1)

car1 = cars[cars["name"] == car1_name].iloc[0]
car2 = cars[cars["name"] == car2_name].iloc[0]



    

# ---------------------------
# Car stats display
# ---------------------------
st.title("Sports Car Performance Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader(car1_name)
    st.metric("Horsepower", f"{car1['horsepower']} hp")
    st.metric("Weight", f"{car1['weight_lbs']:,} lbs")
    st.metric("Top Speed", f"{car1['top_speed_mph']} mph")
    st.metric("0–60 mph", f"{car1['acceleration_0_60']} s")

with col2:
    st.subheader(car2_name)
    st.metric("Horsepower", f"{car2['horsepower']} hp")
    st.metric("Weight", f"{car2['weight_lbs']:,} lbs")
    st.metric("Top Speed", f"{car2['top_speed_mph']} mph")
    st.metric("0–60 mph", f"{car2['acceleration_0_60']} s")

st.divider()

# ---------------------------
# Race Simulation (based on 0–60)
# ---------------------------
st.subheader("Acceleration Simulation")

race_placeholder = st.empty()

# Normalize speeds (shorter 0–60 = faster)
speed1 = 60 / car1["acceleration_0_60"]
speed2 = 60 / car2["acceleration_0_60"]

progress1, progress2 = 0.0, 0.0
race_duration = 5  # seconds

for _ in range(100):
    progress1 += speed1 / 100
    progress2 += speed2 / 100
    race_placeholder.progress(
        min(progress1 / max(progress1, progress2), 1.0),
        text=f"{car1_name} vs {car2_name}"
    )
    time.sleep(race_duration / 100)

winner = car1_name if speed1 > speed2 else car2_name
st.success(f" {winner} wins the 0–60 race!")

# ---------------------------
# Optional — data table
# ---------------------------
with st.expander("View all car data"):
    st.dataframe(cars, use_container_width=True)