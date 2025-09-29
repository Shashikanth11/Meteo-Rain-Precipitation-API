from fastapi import FastAPI, Body, HTTPException
from starlette.responses import JSONResponse
from joblib import load
import pandas as pd
from datetime import timedelta

# Import utilities (assuming app.util is correctly set up)
from app.utils import fetch_weather_features, engineer_rain_features, engineer_precip_features

app = FastAPI(title="Rain Prediction API")

# Load models (NOTE: These files must exist in the models directory)
try:
    rain_model = load("models/rain_or_not/best_xgboost_classifier.joblib")
    precip_model = load("models/precipitation_fall/best_randomforest_regression.joblib")
except FileNotFoundError as e:
    raise HTTPException(status_code=500, detail=f"Model loading failed: {e}")


@app.get("/")
def read_root():
    return {"message": "Welcome to Rain Prediction API"}


@app.get("/health")
def healthcheck():
    return {"status": "Model is ready"}


# --- API Fetch (GET) Endpoint ---
@app.get("/predict/rain")
def predict_rain_fetch(date: str):
    """Fetches data from Open-Meteo API and predicts rain."""
    try:
        dt = pd.to_datetime(date)
        # Fetch data from API (already in {k: [v]} format)
        weather_data = fetch_weather_features(dt)
        features = engineer_rain_features(weather_data, dt)
        
        pred = rain_model.predict(features)[0]
        proba = rain_model.predict_proba(features)[0, 1] if hasattr(rain_model, "predict_proba") else None

        return JSONResponse({
            "input_date": date,
            "prediction": {
                "date": (dt + pd.Timedelta(days=7)).strftime("%Y-%m-%d"),
                "will_rain": bool(pred),
                "probability_of_rain": float(proba) if proba is not None else None
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API Fetch prediction failed: {e}")

# --- API Fetch (GET) Endpoint ---
@app.get("/predict/precipitation/fall")
def predict_precipitation_fetch(date: str):
    """Fetches data from Open-Meteo API and predicts precipitation."""
    try:
        dt = pd.to_datetime(date)
        # Fetch data from API (already in {k: [v]} format)
        weather_data = fetch_weather_features(dt)
        features = engineer_precip_features(weather_data, dt)

        prediction = precip_model.predict(features)[0]

        return JSONResponse({
            "input_date": date,
            "prediction": {
                "start_date": (dt + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (dt + pd.Timedelta(days=3)).strftime("%Y-%m-%d"),
                "precipitation_fall": float(prediction)
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API Fetch prediction failed: {e}")


# --- Manual Input (POST) Endpoint for Rain ---
@app.post("/predict/rain/manual")
def predict_rain_manual(date: str = Body(..., embed=True), features: dict = Body(..., embed=True)):
    """Receives raw features and date, runs feature engineering, and predicts rain."""
    try:
        dt = pd.to_datetime(date)
        
        # Format the features to the expected {k: [v]} structure for engineering
        weather_data = {k: [v] for k, v in features.items()}
        
        # Engineer the features (needs the date for cyclic features)
        engineered_features = engineer_rain_features(weather_data, dt)

        pred = rain_model.predict(engineered_features)[0]
        proba = rain_model.predict_proba(engineered_features)[0, 1] if hasattr(rain_model, "predict_proba") else None

        return JSONResponse({
            "input_date": date,
            "prediction": {
                "date": (dt + pd.Timedelta(days=7)).strftime("%Y-%m-%d"),
                "will_rain": bool(pred),
                "probability_of_rain": float(proba) if proba is not None else None
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual Rain prediction failed: {e}")


# --- Manual Input (POST) Endpoint for Precipitation ---
@app.post("/predict/precipitation/manual")
def predict_precipitation_manual(date: str = Body(..., embed=True), features: dict = Body(..., embed=True)):
    """Receives raw features and date, runs feature engineering, and predicts precipitation."""
    try:
        dt = pd.to_datetime(date)
        
        # Format the features to the expected {k: [v]} structure for engineering
        weather_data = {k: [v] for k, v in features.items()}
        
        # Engineer the features (needs the date for cyclic features)
        engineered_features = engineer_precip_features(weather_data, dt)

        prediction = precip_model.predict(engineered_features)[0]

        return JSONResponse({
            "input_date": date,
            "prediction": {
                "start_date": (dt + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (dt + pd.Timedelta(days=3)).strftime("%Y-%m-%d"),
                "precipitation_fall": float(prediction)
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual Precipitation prediction failed: {e}")
