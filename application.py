import re
import sys
import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to sys.path to access the scripts package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from scripts.modeling.whisky_recommender_model import recommend_whisky

application = Flask(__name__, static_url_path='', static_folder='./frontend')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment setup
IS_LOCAL = os.getenv('IS_LOCAL', 'True') == 'True'
S3_BUCKET = os.getenv('S3_BUCKET')  # Only necessary when not local
FEATURE_STORE_PATH = os.path.join('', 'data', 'processed', '2023_09', 'whisky_features_100.csv')

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

    # Log the data
    logger.info(f"Received feedback data: {data}")

    required_fields = ['whisky1', 'whisky2', 'whisky3', 'recommendedWhisky', 'feedback1', 'timestamp']
    optional_fields = ['rating', 'feedback2', 'experience']

    if not all(field in data for field in required_fields):
        logger.error("Missing data in the feedback submission")
        return jsonify({'error': 'Missing data'}), 400

    try:
        # Prepare feedback data for CSV
        header = required_fields + optional_fields
        feedback_entries = [data.get(field, '') for field in header]

        # Construct CSV content
        csv_content = ','.join(['"{}"'.format(entry) for entry in header]) + '\n'  # Header row
        csv_content += ','.join(['"{}"'.format(entry) for entry in feedback_entries])  # Data row

        # Sanitize timestamp and create a filename
        sanitized_timestamp = re.sub(r'[^a-zA-Z0-9]', '_', data['timestamp'])
        feedback_file_name = f'feedback_{sanitized_timestamp}.csv'
        feedback_file_path = os.path.join('data', 'feedback', '2024_05', feedback_file_name)

        # Decide storage based on environment
        if IS_LOCAL:
            local_feedback_file = os.path.join(FEEDBACK_DIR, feedback_file_name)
            with open(local_feedback_file, 'w', newline='') as file:
                file.write(csv_content)
            logger.info(f"Feedback written to local file: {local_feedback_file}")
        else:
            import boto3
            s3 = boto3.client('s3')
            logger.info(f"Attempting to write feedback to S3 bucket: {S3_BUCKET}, Key: {feedback_file_path}")
            try:
                response = s3.put_object(Bucket=S3_BUCKET, Key=feedback_file_path, Body=csv_content.encode('utf-8'))
                logger.info(f"S3 put_object response: {response}")
                logger.info(f"Feedback written to S3 bucket {S3_BUCKET}")
            except Exception as e:
                logger.error(f"Failed to write to S3 bucket: {e}", exc_info=True)
                return jsonify({'error': str(e)}), 500

        return jsonify({'message': 'Feedback submitted successfully'}), 200
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# Recommendation endpoint
@application.route('/recommend', methods=['POST'])
def recommend_whisky_endpoint():
    data = request.get_json()
    logger.info(f"Received recommendation request: {data}")

    if 'whisky_names' not in data or not isinstance(data['whisky_names'], list):
        return jsonify({'error': 'Invalid input, list of whisky names expected'}), 400

    try:
        recommendation = recommend_whisky(FEATURE_STORE_PATH, data['whisky_names'])
        recommended_whisky = recommendation["Recommended Whisky"]
        logger.info(f"Recommended whisky: {recommended_whisky}")
        return jsonify({'recommended_whisky': recommended_whisky})
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=8000)
