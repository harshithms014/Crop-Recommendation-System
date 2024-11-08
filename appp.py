import requests
from flask import Flask, request, render_template
import numpy as np
import pandas
import sklearn
import pickle
import json
from geopy.geocoders import Nominatim
import time

# importing model
model = pickle.load(open('model.pkl', 'rb'))
sc = pickle.load(open('standscaler.pkl', 'rb'))
ms = pickle.load(open('minmaxscaler.pkl', 'rb'))

# creating flask app
app = Flask(__name__)

features_list = []


@app.route('/')
def index():
    return render_template("index.html")



def predict():
    try:
        N = request.form["Nitrogen"]
        P = request.form["phosphorous"]
        K = request.form["potassium"]
        features_list = [N, P, K]
        features_list.append("temp")
        features_list.append("humidity")
        features_list.append("ph")

        features_list
        pred = np.array(features_list).reshape(1, -1)
        sc_features = ms.transform(pred)
        fi_features = sc.transform(sc_features)
        prediction = model.predict(fi_features)

        crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                     8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                     14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                     19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}

        if prediction[0] in crop_dict:
            crop = crop_dict[prediction[0]]
            result = f"{crop} is recommended"
        else:
            result = "No recommendation available at this time."
        return render_template("index.html", result=result)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return render_template("index.html", result="An error occurred during prediction.")


global dist_val, temp, humidity


@app.route("/showWeather", methods=['POST'])
def showWeather():
    try:
        api_key = "afc6adb7ffbfa53c9c59c26918fb5480"

        dist_val = request.form['district']
        zip_code = request.form['zip_code']

        weather_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + dist_val + '&appid=' + api_key

        response = requests.get(weather_url)
        weather_info = response.json()

        if weather_info['cod'] == 200:
            kelvin = 273
            temp = int(weather_info["main"]["temp"] - kelvin)
            humidity = int(weather_info["main"]["humidity"])
        else:
            print("We couldn't fetch temperature")

        global latitude, longitude
        geolocator = Nominatim(user_agent="agrirecomendation")

        location = geolocator.geocode(f"{dist_val}, {zip_code}")
        if location:
            latitude = location.latitude
            longitude = location.longitude
            PH = fetch_soil_information(latitude, longitude)
            if PH is not None:
                return predict()
            else:
                return render_template('index.html', message="No data available for ph.")
        else:
            print("Couldn't Access the Pincode")
        return render_template("index.html")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return render_template("index.html", result="An error occurred during weather information retrieval.")


def fetch_soil_information(latitude, longitude):
    # Soilgrids API endpoint for soil data
    soilgrids_endpoint = 'https://rest.soilgrids.org/query?'

    # Parameters for the request (depth and variables)
    params = {
        'lon': longitude,
        'lat': latitude,
        'attributes': 'phh2o,cec',  # Example soil attributes (you can modify these)
        'depths': '0-5cm',
    }

    # Making a GET request to the Soilgrids API
    response = requests.get(soilgrids_endpoint, params=params)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if response.status_code == 200:
                soil_data = response.json()
                # Extract the soil data and return it
                global ph
                ph = soil_data['properties']['phh2o']
                return ph
            else:
                return print("Failed to fetch soil data. Status code:", response.status_code)
        except requests.exceptions.RequestException as e:
            print(f"Failed attempt {attempt + 1}/{max_retries}. Error: {e}")
            time.sleep(1)  # Add a delay between attempts

    print("Failed to fetch soil data after multiple attempts.")
    return None


# python main
if __name__ == "__main__":
    app.run(debug=True)
