import streamlit as st #Car_info.py (Isaac Acuna)
import pandas as pd
import matplotlib.image as mpimg

st.set_page_config(page_title="Car Gallery", layout="wide")
@st.cache_data
def load_data():
    return pd.read_csv("cars.csv")

cars = load_data()


st.title("Car Gallery")

st.sidebar.header("Select Car")
car_name = st.sidebar.selectbox("Car", cars["name"])
car = cars[cars["name"] == car_name].iloc[0]
#big title to display car name
st.header(car_name)
#make videos watchable

def convert_youtube(url):
    if "watch?v=" in url:
        return url.replace("watch?v=", "embed/")
    return url
embed_url = convert_youtube(car['youtube_link'])





#prepare car data

st.video(embed_url)
st.image(car["google_image"])



