# Add this code to your Flask app (app.py)

import csv
from flask import Flask, request, jsonify

app = Flask(__name__)

# Define the CSV file where feedback will be saved
csv_filename = 'feedback_data.csv'

# Feedback submission
@app.route('/submitFeedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()

    # Extract feedback data
    whisky1 = data['whisky1']
    whisky2 = data['whisky2']
    whisky3 = data['whisky3']
    recommended_whisky = data['recommendedWhisky']
    feedback1 = data['feedback1']
    feedback2 = data['feedback2']

    # Append feedback data to the CSV file
    with open(csv_filename, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([whisky1, whisky2, whisky3, recommended_whisky, feedback1, feedback2])

    return jsonify({'message': 'Feedback submitted successfully'}), 200


# Recommender model deployment:
from whisky_recommender_model import recommend_whisky

@app.route('/recommend', methods=['POST'])
def recommend_whisky_endpoint():
    data = request.get_json()
    whisky_names = data['whisky_names']  # Assuming the JSON contains 'whisky_names' as a list
    recommended_whisky = recommend_whisky(whisky_names)

    return jsonify({'recommended_whisky': recommended_whisky})


if __name__ == '__main__':
    app.run(debug=True)
