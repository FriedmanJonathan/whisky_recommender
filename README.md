# Whisky Recommender Project

## Overview

The Whisky Recommender Project aims to help users discover new whiskies based on their preferences. The project involves web scraping whisky data, processing it, and using machine learning to recommend whiskies that match user tastes. Users can select their favorite whiskies and get recommendations along with common and additional tasting notes.

## Project Structure

The basic structure of the project is as follows:

```plaintext
whisky_recommender/
├── backend/
│   ├── app.py
├── data/
│   ├── feedback/
│   │   └── 2024_05/
│   │       └── feedback_file_dated1.csv
│   │       └── feedback_file_dated2.csv
│   ├── processed/
│   │   └── 2024_05/
│   │       └── whisky_features.csv
│   └── raw/
│       └── 2024_05/
│           ├── whisky_main_page_with_ratings.csv
│           └── whisky_details_all.csv
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── distillery_data.csv
├── scripts/
│   ├── processing/
│   │   └── data_parsing_and_cleaning.csv
│   ├── modeling/
│   │   └── whisky_recommender_model.py
│   ├── ingestion/
│   │   └── whisky_com_main_page_scraper.csv
│   │   └── whisky_com_secondary_pages_scraper.csv
├── tests/
│   └── test_data_parsing.py
├── gitignore
├── LICENSE
├── Makefile
├── requirements.txt
└── README.md

```

## Installation

1. Clone the repository:

git clone https://github.com/yourusername/whisky_recommender.git
cd whisky_recommender

2. Set up a virtual environment:

python -m venv .whisky_rec_venv

3. Activate the virtual environment:

Windows: .whisky_rec_venv\Scripts\activate
MacOS/Linux: source .whisky_rec_venv/bin/activate

4. Install the required packages:

make install

5. Run the project

Run python app.py in the backend folder and then access on your browser at http://localhost:8000


6. Running Tests

To run tests, use the following command: make test

7. Linting and Formatting

To lint the code using pylint and format it using black, run the commands make lint of make format, respectively.

## Project Components

### Web Scraping

The synchronous scraping module uses Selenium and BeautifulSoup to scrape whisky data from the Whisky.com website.

### Data Parsing

The data_parsing_and_modeling.py script processes the outputs of the whisky scraping scripts into a feature dataset. It prepares the data required for generating whisky recommendations.

### Whisky Recommender Model

The whisky_recommender_model.py script generates recommendations based on user-selected whiskies. It uses cosine similarity to compare user-selected whisky profiles with other whiskies in the dataset.


## Next steps: Deploying to Production

The ultimate goal is to create a web interface where users can select their favorite whiskies and receive recommendations. The frontend consists of HTML, JavaScript, and CSS files, while the backend is built with Python.


## Feedback and Contributions

Feedback and contributions are welcome! Please fork the repository and create a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.


## License

This project is licensed under the MIT License. See the LICENSE file for details.