# app/utils.py
import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta


def fetch_weather_features(date: pd.Timestamp):
    """
    Fetch weather data for Sydney from Open-Meteo API for a single date.
    """
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude=-33.8678&longitude=151.2073"
        f"&start_date={date.strftime('%Y-%m-%d')}"
        f"&end_date={date.strftime('%Y-%m-%d')}"
        "&daily=temperature_2m_min,temperature_2m_max,"
        "precipitation_sum,weathercode,daylight_duration,"
        "sunshine_duration,et0_fao_evapotranspiration,"
        "precipitation_hours,wind_direction_10m_dominant,"
        "wind_gusts_10m_max"
        "&timezone=Australia%2FSydney"
    )

    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        raise Exception(f"Weather API request failed: {response.text}")

    data = response.json()
    if "daily" not in data:
        raise ValueError(f"No weather data available for {date.strftime('%Y-%m-%d')}")
    return data["daily"]


def _encode_cyclic(val, max_val):
    """Helper to encode cyclical features"""
    return np.sin(2 * np.pi * val / max_val), np.cos(2 * np.pi * val / max_val)


def engineer_rain_features(weather_data, date: pd.Timestamp):
    """
    Generate rain model features.
    """
    get = lambda key, default=0: weather_data.get(key, [default])[0]

    temperature_2m_min = get("temperature_2m_min")
    temperature_2m_max = get("temperature_2m_max")
    daylight_duration = get("daylight_duration")
    sunshine_duration = get("sunshine_duration")
    precipitation_hours = get("precipitation_hours")
    et0_fao_evapotranspiration = get("et0_fao_evapotranspiration")
    weather_code = get("weathercode")
    wind_direction_10m_dominant = get("wind_direction_10m_dominant")
    wind_gusts_10m_max = get("wind_gusts_10m_max")

    temp_range = temperature_2m_max - temperature_2m_min
    sunshine_ratio = sunshine_duration / daylight_duration if daylight_duration > 0 else 0.0

    month_sin, month_cos = _encode_cyclic(date.month, 12)
    doy_sin, doy_cos = _encode_cyclic(date.dayofyear, 365)
    dow_sin, dow_cos = _encode_cyclic(date.dayofweek, 7)

    return pd.DataFrame([{
        "weather_code": weather_code,
        "temperature_2m_min": temperature_2m_min,
        "temperature_2m_max": temperature_2m_max,
        "daylight_duration": daylight_duration,
        "sunshine_duration": sunshine_duration,
        "precipitation_hours": precipitation_hours,
        "et0_fao_evapotranspiration": et0_fao_evapotranspiration,
        "wind_direction_10m_dominant": wind_direction_10m_dominant,
        "wind_gusts_10m_max": wind_gusts_10m_max,
        "temp_range": temp_range,
        "sunshine_ratio": sunshine_ratio,
        "month_sin": month_sin,
        "month_cos": month_cos,
        "dayofyear_sin": doy_sin,
        "dayofyear_cos": doy_cos,
        "dayofweek_sin": dow_sin,
        "dayofweek_cos": dow_cos
    }])


def engineer_precip_features(weather_data, date: pd.Timestamp):
    """
    Generate precipitation model features.
    """
    get = lambda key, default=0: weather_data.get(key, [default])[0]

    temperature_2m_min = get("temperature_2m_min")
    temperature_2m_max = get("temperature_2m_max")
    daylight_duration = get("daylight_duration")
    sunshine_duration = get("sunshine_duration")
    et0_fao_evapotranspiration = get("et0_fao_evapotranspiration")
    wind_gusts_10m_max = get("wind_gusts_10m_max")
    wind_direction_10m_dominant = get("wind_direction_10m_dominant")

    temp_range = temperature_2m_max - temperature_2m_min
    wind_dir_sin = np.sin(np.deg2rad(wind_direction_10m_dominant))
    wind_dir_cos = np.cos(np.deg2rad(wind_direction_10m_dominant))

    month_sin, month_cos = _encode_cyclic(date.month, 12)
    doy_sin, doy_cos = _encode_cyclic(date.dayofyear, 365)
    dow_sin, dow_cos = _encode_cyclic(date.dayofweek, 7)

    return pd.DataFrame([{
        "temperature_2m_min": temperature_2m_min,
        "temperature_2m_max": temperature_2m_max,
        "daylight_duration": daylight_duration,
        "sunshine_duration": sunshine_duration,
        "et0_fao_evapotranspiration": et0_fao_evapotranspiration,
        "wind_gusts_10m_max": wind_gusts_10m_max,
        "temp_range": temp_range,
        "wind_dir_sin": wind_dir_sin,
        "wind_dir_cos": wind_dir_cos,
        "month_sin": month_sin,
        "month_cos": month_cos,
        "dayofyear_sin": doy_sin,
        "dayofyear_cos": doy_cos,
        "dayofweek_sin": dow_sin,
        "dayofweek_cos": dow_cos
    }])
