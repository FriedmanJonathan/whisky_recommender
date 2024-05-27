import csv
import pandas as pd
import sys
import os
from flask import Flask, request, jsonify, send_from_directory

# Add the parent directory to sys.path to access the scripts package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from scripts.modeling.whisky_recommender_model import recommend_whisky

application = Flask(__name__, static_url_path='', static_folder='./frontend')

# Define the CSV file where feedback will be saved and load feature store data
csv_filename = 'distillery_data.csv'
FEATURE_STORE_PATH = os.path.join('', 'data', 'processed', '2023_09', 'whisky_features_100.csv')
FEEDBACK_DIR = os.path.join('', 'data', 'feedback', '2024_05')
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# Main page
@application.route('/')
def index():
    return send_from_directory(application.static_folder, 'index.html')


# Feedback submission
@application.route('/submitFeedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    required_fields = ['whisky1', 'whisky2', 'whisky3', 'recommendedWhisky', 'feedback1', 'timestamp']

    # Check if all required fields are provided
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing data'}), 400

    try:
        # Extract feedback data
        print(data)  # Log the incoming data
        whisky1 = data['whisky1']
        whisky2 = data['whisky2']
        whisky3 = data['whisky3']
        recommended_whisky = data['recommendedWhisky']
        feedback1 = data['feedback1']
        rating = data.get('rating')  # This field is optional
        feedback2 = data.get('feedback2', '')  # This field is optional
        experience = data['experience']  # New field for whisky experience
        timestamp = data['timestamp']

        # Sanitize timestamp for use in filenames
        sanitized_timestamp = timestamp.replace(':', '').replace('-', '').replace('.', '').replace('T', '_').replace('Z', '')

        # Generate a unique filename based on sanitized timestamp
        feedback_file = os.path.join(FEEDBACK_DIR, f'feedback_{sanitized_timestamp}.csv')
        print(f"Writing to file: {feedback_file}")  # Log the feedback file path

        # Save feedback data to CSV
        with open(feedback_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['whisky1', 'whisky2', 'whisky3', 'recommendedWhisky', 'feedback1', 'rating', 'feedback2', 'experience', 'timestamp'])
            writer.writerow([whisky1, whisky2, whisky3, recommended_whisky, feedback1, rating, feedback2, experience, timestamp])

        return jsonify({'message': 'Feedback submitted successfully'}), 200
    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500


@application.route('/recommend', methods=['POST'])
def recommend_whisky_endpoint():
    data = request.get_json()

    if 'whisky_names' not in data or not isinstance(data['whisky_names'], list):
        return jsonify({'error': 'Invalid input, list of whisky names expected'}), 400

    try:
        whisky_names = data['whisky_names']

        recommended_whisky_info = recommend_whisky(FEATURE_STORE_PATH, whisky_names)

        recommended_whisky = recommended_whisky_info["Recommended Whisky"]

        return jsonify({'recommended_whisky': recommended_whisky})
    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=8000)
