import pandas as pd
import pytest
import os

class TestDataColumns:
    CSV_DIRECTORY = 'csv_files/'

    def __init__(self, csv_filename):
        self.csv_filename = csv_filename

    @property
    def csv_filepath(self):
        return os.path.join(self.CSV_DIRECTORY, self.csv_filename)

    @pytest.fixture
    def df(self):
        return pd.read_csv(self.csv_filepath)

    def test_loaded_data_has_correct_columns(self, df):
        expected_columns_map = {
            'whisky_details_100.csv': ['whisky_url', 'distillery_name_inner', 'country', 'region', 'whisky_type', 'whisky_age_inner', 'alcohol_pct_inner', 'bottler', 'post_treatment', 'nosing_notes', 'tasting_notes', 'finish_notes'],
            # Add more mappings as needed
        }
        expected_columns = expected_columns_map.get(self.csv_filename, [])

        assert df.columns.to_list() == expected_columns

def test_data_columns():
    csv_directory = 'csv_files/'
    for csv_file in [file for file in os.listdir(csv_directory) if file.endswith('.csv')]:
        test = TestDataColumns(csv_file)
        test.test_loaded_data_has_correct_columns()
