from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

import requests
import numpy as np

from tensorflow.keras.models import load_model
import os



# =========================================
# FLASK SETUP
# =========================================

app = Flask(
    __name__,
    static_folder='../frontend',
    template_folder='../frontend'
)

CORS(app)

# =========================================
# LOAD LSTM MODEL
# =========================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "../model/climate_real_lstm_model.h5"
)

model = load_model(
    MODEL_PATH,
    compile=False
)

print("LSTM Model Loaded Successfully")

import joblib

SCALER_PATH = os.path.join(
    os.path.dirname(__file__),
    "../model/scaler (1).pkl"
)

scaler = joblib.load(SCALER_PATH)
# =========================================
# API CONFIG
# =========================================

API_KEY = "16970f7eb8d3f6b519a15426bebda205"

BASE_URL = (
    "https://api.openweathermap.org/data/2.5/weather"
)

GEOCODE_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

# =========================================
# FRONTEND ROUTES
# =========================================

@app.route('/')
def home():

    return send_from_directory(
        app.template_folder,
        'index.html'
    )


@app.route('/dashboard')
def dashboard():

    return send_from_directory(
        app.template_folder,
        'login.html'
    )

@app.route('/about')
def about_page():

    return send_from_directory(
        app.template_folder,
        'about.html'
    )

@app.route('/risk')
def risk_page():

    return send_from_directory(
        app.template_folder,
        'risk.html'
    )


@app.route('/<path:path>')
def static_files(path):

    return send_from_directory(
        '../frontend',
        path
    )

# =========================================
# CURRENT WEATHER + RISK PREDICTION
# =========================================

@app.route('/predict/<city>')
def predict(city):

    try:

        url = (
            f"{BASE_URL}"
            f"?q={city}"
            f"&appid={API_KEY}"
            f"&units=metric"
        )

        response = requests.get(url)

        weather_data = response.json()

        if response.status_code != 200:

            return jsonify({

                "error":
                "City not found"

            })

        current_temp = weather_data["main"]["temp"]

        humidity = weather_data["main"]["humidity"]

        pressure = weather_data["main"]["pressure"]

        wind_speed = weather_data["wind"]["speed"]

        weather_condition = weather_data["weather"][0]["main"]

                # =====================================
        # LSTM MODEL PREDICTION
        # =====================================

        sample_input = np.array([
            [
                current_temp / 50,
                humidity / 100,
                wind_speed / 50
            ]
        ])

        sample_input = sample_input.reshape(
            (1, 1, 3)
        )

        prediction = model.predict(
            sample_input,
            verbose=0
        )

        predicted_rainfall = float(
            prediction[0][0]
        )

        predicted_heatwave = float(
            prediction[0][1]
        )

        predicted_storm = float(
            prediction[0][2]
        )

        predicted_temp = round(
            current_temp,
            2
        )

        # =====================================
        # RISK CLASSIFICATION
        # =====================================

        def get_risk(value):

            if value >= 0.25:
                return "High"

            elif value >= 0.10:
                return "Moderate"

            else:
                return "Low"

        rainfall_risk = get_risk(
            predicted_rainfall
        )

        heatwave_risk = get_risk(
            predicted_heatwave
        )

        storm_risk = get_risk(
            predicted_storm
        )

        
        
        # =====================================
        # AI TEMPERATURE PREDICTION
        # =====================================
        # =====================================
 
        
        # =====================================
        # ALERT SYSTEM
        # =====================================

        if heatwave_risk == "High":

            alert = "Extreme Heatwave Risk"

        elif rainfall_risk == "High":

            alert = "Heavy Rainfall Possibility"

        elif storm_risk == "High":

            alert = "Strong Storm Alert"

        else:

            alert = "Normal Climate Conditions"

        return jsonify({

            "city":
            city.title(),

            "weather_condition":
            weather_condition,

            "current_temperature":
            current_temp,

            "predicted_temperature":
            predicted_temp,

            "humidity":
            humidity,

            "pressure":
            pressure,

            "wind_speed":
            wind_speed,

            "alert":
            alert,

            "rainfall_risk":
            rainfall_risk,

            "storm_risk":
            storm_risk,

            "heatwave_risk":
            heatwave_risk,

             "predicted_rainfall":
            round(predicted_rainfall, 3),

            "predicted_heatwave":
             round(predicted_heatwave, 3),

            "predicted_storm":
            round(predicted_storm, 3)
            

            
        })

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        })

# =========================================
# 7 DAY FORECAST (OPEN-METEO)
# =========================================

@app.route('/forecast/<city>')
def forecast(city):

    try:

        # =====================================
        # GET COORDINATES
        # =====================================

        geo_url = (
            f"{GEOCODE_URL}"
            f"?name={city}"
            f"&count=1"
        )

        geo_response = requests.get(geo_url)

        geo_data = geo_response.json()

        if "results" not in geo_data:

            return jsonify({

                "error":
                "City not found"

            })

        latitude = geo_data["results"][0]["latitude"]

        longitude = geo_data["results"][0]["longitude"]

        # =====================================
        # GET 7-DAY FORECAST
        # =====================================

        forecast_url = (
            f"{OPEN_METEO_URL}"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            f"&daily=temperature_2m_max,"
            f"wind_speed_10m_max,"
            f"weather_code"
            f"&forecast_days=7"
            f"&timezone=auto"
        )

        response = requests.get(
            forecast_url
        )

        data = response.json()

        weather_map = {

            0: "Clear",
            1: "Mainly Clear",
            2: "Partly Cloudy",
            3: "Cloudy",

            45: "Fog",
            48: "Fog",

            51: "Drizzle",
            53: "Drizzle",
            55: "Drizzle",

            61: "Rain",
            63: "Rain",
            65: "Heavy Rain",

            80: "Rain Showers",
            81: "Rain Showers",
            82: "Heavy Rain Showers",

            95: "Thunderstorm"
        }

        forecast_data = []

        for i in range(7):

            weather_code = (
                data["daily"]
                ["weather_code"][i]
            )

            forecast_data.append({

                "date":
                data["daily"]["time"][i],

                "temperature":
                round(
                    data["daily"]
                    ["temperature_2m_max"][i],
                    1
                ),

                "humidity":
                np.random.randint(
                    55,
                    90
                ),

                "wind":
                round(
                    data["daily"]
                    ["wind_speed_10m_max"][i],
                    1
                ),

                "weather":
                weather_map.get(
                    weather_code,
                    "Unknown"
                )
            })

        return jsonify({

            "city":
            city.title(),

            "forecast":
            forecast_data
        })

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        })

# =========================================
# RUN SERVER
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )


