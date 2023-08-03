# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS  # Import the CORS module
import requests
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Initialize CORS with your Flask app

def fetch_housing_data():
    response = requests.get('https://opendata.cbs.nl/ODataApi/odata/83913NED/TypedDataSet')
    data = pd.json_normalize(response.json()['value'])
    return data

def calculate_current_home_value(start_value, start_date, current_date, region):
    data = fetch_housing_data()
    region_data = data[data['RegioS'] == region]

    # Filter out only the quarterly data
    region_data = region_data[region_data['Perioden'].str.contains('KW')]

    start_data = region_data[region_data['Perioden'] == start_date]
    current_data = region_data[region_data['Perioden'] == current_date]

    start_index = start_data['PrijsindexVerkoopprijzen_1'].values[0] if not start_data.empty else None
    current_index = current_data['PrijsindexVerkoopprijzen_1'].values[0] if not current_data.empty else None

    if start_index is None or current_index is None:
        return None

    current_value = start_value * (current_index / start_index)
    return current_value
@app.route('/')
def index():
    return 'Welcome to the Flask backend!'

# Serve the favicon.ico file
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/calculate_home_value', methods=['POST'])
def calculate_home_value():
    data = request.get_json()
    start_value = data.get('start_value')
    start_date = data.get('start_date')
    current_date = data.get('current_date')
    region = data.get('region')

    current_home_value = calculate_current_home_value(start_value, start_date, current_date, region)

    if current_home_value is None:
        return jsonify(error='Price index data not found for the specified dates'), 400

    return jsonify(current_home_value=current_home_value)

if __name__ == "__main__":
    app.run()
    port = int(os.environ.get("PORT", 5000))

    # Run the app with host='0.0.0.0' to listen on all network interfaces
    app.run(host="0.0.0.0", port=port)