# app/main.py
from fastapi import FastAPI, Query, HTTPException
from starlette.responses import JSONResponse
from joblib import load
import pandas as pd
from datetime import timedelta
from .utils import fetch_weather_features, engineer_rain_features, engineer_precip_features

app = FastAPI(title="Meteo Rain & Precipitation Prediction API")

# Load models
try:
    rain_model = load("models/rain_or_not/best_xgboost_classifier.joblib")
    precip_model = load("models/precipitation_fall/best_randomforest_regression.joblib")
except FileNotFoundError as e:
    raise HTTPException(status_code=500, detail=f"Model loading failed: {e}")


@app.get("/")
def root():
    """Project overview endpoint."""
    try:
        with open("github.txt", "r") as f:
            github_link = f.read().strip()
    except FileNotFoundError:
        github_link = "Not available"

    return {
        "project": "Meteo Rain & Precipitation Prediction API",
        "description": "API to predict rain in 7 days and precipitation in next 3 days.",
        "endpoints": [
            "/health/",
            "/predict/rain/?date=YYYY-MM-DD",
            "/predict/precipitation/fall/?date=YYYY-MM-DD"
        ],
        "github": github_link
    }


@app.get("/health/")
def health():
    return {"status": "API is healthy and ready."}


@app.get("/predict/rain/")
def predict_rain(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    try:
        dt = pd.to_datetime(date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    try:
        weather_data = fetch_weather_features(dt)
        features = engineer_rain_features(weather_data, dt)

        pred = rain_model.predict(features)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    return JSONResponse({
        "input_date": date,
        "prediction": {
            "date": (dt + timedelta(days=7)).strftime("%Y-%m-%d"),
            "will_rain": bool(pred)
        }
    })


@app.get("/predict/precipitation/fall/")
def predict_precipitation(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    try:
        dt = pd.to_datetime(date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    try:
        weather_data = fetch_weather_features(dt)
        features = engineer_precip_features(weather_data, dt)

        prediction = precip_model.predict(features)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    return JSONResponse({
        "input_date": date,
        "prediction": {
            "start_date": (dt + timedelta(days=1)).strftime("%Y-%m-%d"),
            "end_date": (dt + timedelta(days=3)).strftime("%Y-%m-%d"),
            "precipitation_fall": float(prediction)
        }
    })
