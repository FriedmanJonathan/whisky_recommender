import pandas as pd
import pytest
import os

CSV_DIRECTORY = './'


@pytest.fixture(params=[file for file in os.listdir(CSV_DIRECTORY) if file.endswith('.csv')])
def csv_file(request):
    return request.param


@pytest.fixture
def expected_columns(csv_file):
    # Define your expected columns mappings here
    expected_columns_map = {
        'whisky_details_100.csv': ['whisky_url', 'distillery_name_inner', 'country', 'region', 'whisky_type', 'whisky_age_inner', 'alcohol_pct_inner', 'bottler', 'post_treatment', 'nosing_notes', 'tasting_notes', 'finish_notes']
        # Add more mappings as needed - this is TODO, currently test is working ok but failing on other CSVs since we didnt' specify column names
    }
    return expected_columns_map.get(csv_file, [])


@pytest.fixture
def df(csv_file):
    csv_filepath = os.path.join(CSV_DIRECTORY, csv_file)
    return pd.read_csv(csv_filepath)


class TestDataColumns:

    def test_loaded_data_has_correct_columns(self, df, expected_columns):
        assert df.columns.to_list() == expected_columns
