import streamlit as st
from pyowm import OWM
from pyowm.utils.config import get_default_config
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.express as px

# Streamlit Page Config
st.set_page_config(page_title="Weather Forecaster", page_icon="🌦", layout="wide")

# API Configuration
API_KEY = "925b8beec4c885e67e2f0db6eb3f4a4a"  # Replace with your actual API key
config = get_default_config()
config["language"] = "en"
owm = OWM(API_KEY, config)
mgr = owm.weather_manager()

# Helper Functions
def get_weather_data(city_name):
    try:
        observation = mgr.weather_at_place(city_name)
        forecast = mgr.forecast_at_place(city_name, "3h").forecast
        return observation.weather, forecast
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None

def convert_unit(temp, unit):
    return temp if unit == "Celsius" else temp * 9/5 + 32

def plot_graph(df, y_label, title, graph_type):
    fig = px.line(df, x="Date", y="Value", title=title, markers=True) if graph_type == "Line" else px.bar(df, x="Date", y="Value", title=title)
    fig.update_layout(template="plotly_dark" if st.session_state.dark_mode else "plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# Streamlit UI
def main():
    st.title("🌦 Weather Forecaster")
    st.sidebar.header("🔍 Input Options")
    
    city_name = st.sidebar.text_input("🏙 Enter City Name:", "")
    temp_unit = st.sidebar.radio("🌡 Temperature Unit:", ("Celsius", "Fahrenheit"))
    graph_type = st.sidebar.radio("📊 Graph Type:", ("Bar", "Line"))
    dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode", value=False)
    
    st.session_state.dark_mode = dark_mode
    
    if st.sidebar.button("🔎 Get Weather"):
        if not city_name:
            st.warning("⚠️ Please enter a city name.")
            return
        
        weather, forecast = get_weather_data(city_name)
        if not weather or not forecast:
            return

        # Display Weather Info
        st.subheader(f"🌍 Current Weather in {city_name.capitalize()}")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("🌡 Temperature", f"{convert_unit(weather.temperature('celsius')['temp'], temp_unit):.2f}°{temp_unit[0]}")
        col2.metric("💨 Wind Speed", f"{weather.wind()['speed']} m/s")
        col3.metric("🌡 Humidity", f"{weather.humidity}%")
        
        st.write(f"**📖 Status:** {weather.detailed_status.capitalize()}")
        st.write(f"**🌅 Sunrise:** {datetime.utcfromtimestamp(weather.sunrise_time()).strftime('%H:%M:%S')} UTC")
        st.write(f"**🌇 Sunset:** {datetime.utcfromtimestamp(weather.sunset_time()).strftime('%H:%M:%S')} UTC")

        # Forecast Data
        forecast_data = []
        for weather_item in forecast:
            date = datetime.utcfromtimestamp(weather_item.reference_time()).date()
            temp = convert_unit(weather_item.temperature('celsius')['temp'], temp_unit)
            humidity = weather_item.humidity
            forecast_data.append((date, temp, humidity))

        df = pd.DataFrame(forecast_data, columns=["Date", "Temperature", "Humidity"]).groupby("Date").mean().reset_index()

        # Temperature Graph
        st.subheader("🌡 Temperature Forecast")
        temp_df = df[["Date", "Temperature"]].rename(columns={"Temperature": "Value"})
        plot_graph(temp_df, f"Temperature (°{temp_unit[0]})", "5-Day Temperature Forecast", graph_type)

        # Humidity Graph
        st.subheader("💧 Humidity Forecast")
        humidity_df = df[["Date", "Humidity"]].rename(columns={"Humidity": "Value"})
        plot_graph(humidity_df, "Humidity (%)", "5-Day Humidity Forecast", graph_type)

if __name__ == "__main__":
    main()