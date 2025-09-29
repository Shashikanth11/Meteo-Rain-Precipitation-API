import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# === CONFIG ===
# IMPORTANT: Adjust this URL if your FastAPI runs on a different port/host
FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="centered")
st.title("🌦 Rain & Precipitation Prediction")

st.markdown("Select a date and click a button to predict rain or precipitation.")

# Date picker
# API only supports up to yesterday
yesterday = (datetime.today() - timedelta(days=1)).date()

date_input = st.date_input(
    "Select a date",
    # Default to a safe historical date to enable API fetch by default
    value=yesterday - timedelta(days=2),
    min_value=datetime(1940, 1, 1).date(),
)
selected_date = date_input.strftime("%Y-%m-%d")


# Check if the date is too recent for historical API
invalid_date = date_input >= yesterday

if invalid_date:
    st.error("❌ The selected date is too recent for the historical API. Enter details manually.")
    manual_mode = True
else:
    st.success("✅ Historical data available. Use API Values Predict buttons below to Predict using values from Open-Meteo API .")
    manual_mode = False

st.markdown("---")
# === API Mode ===
if not manual_mode:
    st.subheader("☁️ Prediction (using values from Open-Meteo API)")

    col1, col2 = st.columns(2) 

    with col1:
        if st.button("Predict Rain (API Values)"):
            with st.spinner(f"Fetching historical weather data for {selected_date} and predicting..."):
                try:
                    # API Fetch uses the original GET endpoint
                    resp = requests.get(f"{FASTAPI_URL}/predict/rain", params={"date": selected_date})
                    if resp.status_code == 200:
                        result = resp.json()["prediction"]
                        st.subheader("🌧 Rain Prediction (+7 days)")
                        st.write(f"Date: {result['date']}")
                        st.write(f"Will Rain: **{'🌧 Yes' if result['will_rain'] else '☀ No'}**")
                        if result.get("probability_of_rain") is not None:
                            st.write(f"Probability: {result['probability_of_rain']*100:.2f}%")
                    else:
                        st.error(f"Rain prediction failed. Status: {resp.status_code}. Detail: {resp.text}")
                except Exception as e:
                    st.error(f"Network Error: Could not connect to FastAPI at {FASTAPI_URL}. Details: {e}")

    with col2:
         if st.button("Predict Precipitation (API Values)"):
             with st.spinner(f"Fetching historical weather data for {selected_date} and predicting..."):
                 try:
                     # API Fetch uses the original GET endpoint
                     resp = requests.get(f"{FASTAPI_URL}/predict/precipitation/fall", params={"date": selected_date})
                     if resp.status_code == 200:
                         result = resp.json()["prediction"]
                         st.subheader("💧 Precipitation Prediction (Next 3 days)")
                         st.write(f"Start Date: {result['start_date']}, End Date: {result['end_date']}")
                         st.write(f"Predicted Precipitation: **{result['precipitation_fall']:.2f} mm**")
                     else:
                         st.error(f"Precipitation prediction failed. Status: {resp.status_code}. Detail: {resp.text}")
                 except Exception as e:
                     st.error(f"Network Error: Could not connect to FastAPI at {FASTAPI_URL}. Details: {e}")
st.markdown("---")


# === Manual Fill Section ===
st.subheader("✍ Manual Input of Weather Features")
with st.form("manual_input_form"):
    # Input fields remain the same
    weather_code = st.number_input("🌤 Weather Code", value=0, help="0 = Clear sky", key="m_wc")
    temperature_min = st.number_input("🌡 Min Temperature (°C)", value=15.0, key="m_tmin")
    temperature_max = st.number_input("🌡 Max Temperature (°C)", value=25.0, key="m_tmax")
    daylight_duration = st.number_input("☀ Daylight Duration (s)", value=36000, key="m_dd")
    sunshine_duration = st.number_input("☀ Sunshine Duration (s)", value=30000, key="m_sd")
    precipitation_hours = st.number_input("🌧 Precipitation Hours", value=0, key="m_ph")
    et0_fao = st.number_input("🌱 Evapotranspiration", value=3.5, key="m_et0")
    wind_dir = st.number_input("🧭 Wind Direction 10m (deg)", value=180, key="m_wd")
    wind_gusts = st.number_input("💨 Max Wind Gusts (m/s)", value=10.0, key="m_wg")
    st.markdown("----")

    st.subheader("☁️ Prediction (using User filled values)")

    col1, col2 = st.columns(2)
    submitted_rain = col1.form_submit_button("Predict Rain (User Inputs)")
    submitted_precip = col2.form_submit_button("Predict Precipitation (User Inputs)")
    st.markdown("----")

    # Raw features dictionary (used for payload)
    raw_features = {
        "weathercode": weather_code, # Note: Renamed to match API response/engineer function expectations
        "temperature_2m_min": temperature_min,
        "temperature_2m_max": temperature_max,
        "daylight_duration": daylight_duration,
        "sunshine_duration": sunshine_duration,
        "precipitation_hours": precipitation_hours,
        "et0_fao_evapotranspiration": et0_fao,
        "wind_direction_10m_dominant": wind_dir,
        "wind_gusts_10m_max": wind_gusts,
    }


    if submitted_rain:
        with st.spinner(f"Predicting Rain for {selected_date} using manual inputs..."):
            try:
                # CORRECT: Use the /manual POST endpoint and pass data in the 'json' body
                payload = {"date": selected_date, "features": raw_features}
                resp = requests.post(f"{FASTAPI_URL}/predict/rain/manual", json=payload)
                
                if resp.status_code == 200:
                    result = resp.json()["prediction"]
                    st.subheader("🌧 Rain Prediction (+7 days)")
                    st.write(f"Date: {result['date']}")
                    st.write(f"Will Rain: **{'🌧 Yes' if result['will_rain'] else '☀ No'}**")
                    if result.get("probability_of_rain") is not None:
                        st.write(f"Probability: {result['probability_of_rain']*100:.2f}%")
                else:
                    st.error(f"Rain prediction failed. Status: {resp.status_code}. Detail: {resp.text}")
            except Exception as e:
                st.error(f"Network Error: Could not connect to FastAPI at {FASTAPI_URL}. Is the server running? Details: {e}")

    if submitted_precip:
        with st.spinner(f"Predicting Precipitation for {selected_date} using manual inputs..."):
            try:
                # CORRECT: Use the /manual POST endpoint and pass data in the 'json' body
                payload = {"date": selected_date, "features": raw_features}
                resp = requests.post(f"{FASTAPI_URL}/predict/precipitation/manual", json=payload)
                
                if resp.status_code == 200:
                    result = resp.json()["prediction"]
                    st.subheader("💧 Precipitation Prediction (Next 3 days)")
                    st.write(f"Start Date: {result['start_date']}, End Date: {result['end_date']}")
                    st.write(f"Predicted Precipitation: **{result['precipitation_fall']:.2f} mm**")
                else:
                    st.error(f"Precipitation prediction failed. Status: {resp.status_code}. Detail: {resp.text}")
            except Exception as e:
                st.error(f"Network Error: Could not connect to FastAPI at {FASTAPI_URL}. Is the server running? Details: {e}")


