import re
import sys
import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to sys.path to access the scripts package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from scripts.modeling.whisky_recommender_model import recommend_whisky

application = Flask(__name__, static_url_path='', static_folder='./frontend')

# Environment setup
IS_LOCAL = os.getenv('IS_LOCAL', 'True') == 'True'
S3_BUCKET = os.getenv('S3_BUCKET')  # Only necessary when not local

# Define the directories and files based on whether the app is running locally or on AWS
if IS_LOCAL:
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
    optional_fields = ['rating', 'feedback2', 'experience']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing data'}), 400

    try:
        # Log incoming data
        print(data)

        # Prepare feedback data for CSV
        header = required_fields + optional_fields
        feedback_entries = [data.get(field, '') for field in header]

        # Construct CSV content
        csv_content = ','.join(['"{}"'.format(entry) for entry in header]) + '\n'  # Header row
        csv_content += ','.join(['"{}"'.format(entry) for entry in feedback_entries])  # Data row

        # Sanitize timestamp and create a filename
        sanitized_timestamp = re.sub(r'[^a-zA-Z0-9]', '_', data['timestamp'])
        feedback_file_name = f'feedback_{sanitized_timestamp}.csv'

        # Decide storage based on environment
        if IS_LOCAL:
            feedback_file = os.path.join(FEEDBACK_DIR, feedback_file_name)
            with open(feedback_file, 'w', newline='') as file:
                file.write(csv_content)
            print(f"Feedback written to local file: {feedback_file}")
        else:
            import boto3
            s3 = boto3.client('s3')
            s3.put_object(Bucket=S3_BUCKET, Key=feedback_file_name, Body=csv_content.encode('utf-8'))
            print(f"Feedback written to S3 bucket {S3_BUCKET}")

        return jsonify({'message': 'Feedback submitted successfully'}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': str(e)}), 500

# Recommendation endpoint
@application.route('/recommend', methods=['POST'])
def recommend_whisky_endpoint():
    data = request.get_json()
    if 'whisky_names' not in data or not isinstance(data['whisky_names'], list):
        return jsonify({'error': 'Invalid input, list of whisky names expected'}), 400

    try:
        recommended_whisky = recommend_whisky(data['whisky_names'])
        return jsonify({'recommended_whisky': recommended_whisky})
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=8000)
