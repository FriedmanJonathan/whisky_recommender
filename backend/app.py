# Add this code to your Flask app (app.py)

import csv
import pandas as pd
import sys
import os

# Add the parent directory to sys.path to access the scripts package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..',)))

from flask import Flask, request, jsonify, send_from_directory
from scripts.recommendation.whisky_recommender_model import recommend_whisky

app = Flask(__name__, static_url_path='', static_folder='../frontend')

# Define the CSV file where feedback will be saved and load feature store data
csv_filename = 'distillery_data.csv'
FEATURE_STORE_PATH = '../data/processed/2023_09/whisky_features_100.csv'


# Main page
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


# Feedback submission
@app.route('/submitFeedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    required_fields = ['whisky1', 'whisky2', 'whisky3', 'recommendedWhisky', 'feedback1', 'feedback2']

    # Check if all required fields are provided
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing data'}), 400

    try:
        # Extract feedback data
        whisky1, whisky2, whisky3 = data['whisky1'], data['whisky2'], data['whisky3']
        recommended_whisky, feedback1, feedback2 = data['recommendedWhisky'], data['feedback1'], data['feedback2']

        # Append feedback data to the CSV file
        with open(csv_filename, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([whisky1, whisky2, whisky3, recommended_whisky, feedback1, feedback2])

        return jsonify({'message': 'Feedback submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/recommend', methods=['POST'])
def recommend_whisky_endpoint():
    data = request.get_json()

    if 'whisky_names' not in data or not isinstance(data['whisky_names'], list):
        return jsonify({'error': 'Invalid input, list of whisky names expected'}), 400

    try:
        whisky_names = data['whisky_names']

        recommended_whisky_info = recommend_whisky(FEATURE_STORE_PATH, whisky_names)

        recommended_whisky = recommended_whisky_info["Recommended Whisky"]

        return jsonify({'recommended_whisky': recommended_whisky})  # TODO: First extract the name only, then expand to get all data
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
