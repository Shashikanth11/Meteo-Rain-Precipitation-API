---

# 🌦️ Meteo Rain Precipitation API

A FastAPI-based microservice that fetches and processes weather forecast data (temperature, precipitation, wind, sunshine duration, etc.) from the **Open-Meteo API**.
The API is containerized with **Docker** and comes with built-in **Swagger UI** for testing and integration.

---

## 🚀 Features

* REST API built with **FastAPI**
* Weather data retrieval from **Open-Meteo API**
* Returns JSON response with key weather features
* Interactive API docs via **Swagger UI** (`/docs`) and **ReDoc** (`/redoc`)
* Containerized with **Docker** for easy deployment
* Ready for deployment on **Render / Docker / Cloud**

---

## 📂 Project Structure

```
app/
 ├── main.py              # FastAPI entry point  
 ├── utils.py             # Helper functions (fetch weather features)  
 ├── routers/             # (Optional) Modular routers if extended  
 └── __init__.py  
requirements.txt          # Python dependencies  
Dockerfile                # Container build  
README.md                 # Project documentation  
```

---

## ⚡ Local Development

### 1️⃣ Clone the repo

```bash
git clone https://github.com/your-username/Meteo-Rain-Precipitation-API.git
cd Meteo-Rain-Precipitation-API
```

### 2️⃣ Create a virtual environment & install dependencies

```bash
python3 -m venv venv
source venv/bin/activate   # (on Mac/Linux)
venv\Scripts\activate      # (on Windows)

pip install -r requirements.txt
```

### 3️⃣ Run FastAPI app

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at:
👉 Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
👉 ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🐳 Run with Docker

### 1️⃣ Build Docker image

```bash
docker build -t weather-api .
```

### 2️⃣ Run container

```bash
docker run -d -p 8000:8000 weather-api
```

Now access:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ☁️ Deployment on Render

1. Push your repo to GitHub.
2. Go to [Render](https://render.com).
3. Create a new **Web Service** → Connect GitHub repo.
4. In the **Settings**:

   * **Environment**: `Docker`
   * **Port**: `$PORT` (Render auto-sets this)
5. Deploy 🚀

---

## 📡 Example API Usage

### Request

```http
GET /weather?latitude=-33.8688&longitude=151.2093
Host: localhost:8000
```

### Response

```json
{
  "time": ["2025-09-30"],
  "temperature_2m_min": [13.0],
  "temperature_2m_max": [30.0],
  "weathercode": [45],
  "daylight_duration": [44593.46],
  "sunshine_duration": [41597.7],
  "et0_fao_evapotranspiration": [5.22],
  "precipitation_hours": [0.0],
  "wind_direction_10m_dominant": [19],
  "wind_gusts_10m_max": [38.2]
}
```

---

## 🛠️ Tech Stack

* [FastAPI](https://fastapi.tiangolo.com/)
* [Uvicorn](https://www.uvicorn.org/)
* [Open-Meteo API](https://open-meteo.com/)
* [Docker](https://www.docker.com/)

---

## 📜 License

MIT License © 2025 Shashikanth

---
