import pandas as pd
import pytest
import os

CSV_DIRECTORY = "./"


@pytest.fixture(
    params=[file for file in os.listdir(CSV_DIRECTORY) if file.endswith(".csv")]
)
def csv_file(request):
    """
    Fixture to provide CSV file names found in the specified directory.

    Parameters:
        request: pytest request object

    Returns:
        str: Name of a CSV file
    """
    return request.param


@pytest.fixture
def expected_columns(csv_file):
    """
    Fixture to provide the expected column names for a given CSV file.

    Parameters:
        csv_file (str): Name of the CSV file

    Returns:
        list: Expected column names for the CSV file
    """
    # Define your expected columns mappings here
    expected_columns_map = {
        "whisky_details_100.csv": [
            "whisky_url",
            "distillery_name_inner",
            "country",
            "region",
            "whisky_type",
            "whisky_age_inner",
            "alcohol_pct_inner",
            "bottler",
            "post_treatment",
            "nosing_notes",
            "tasting_notes",
            "finish_notes",
        ]
        # Add more mappings as needed - this is TODO
    }
    return expected_columns_map.get(csv_file, [])


@pytest.fixture
def df(csv_file):
    """
    Fixture to load a CSV file into a pandas DataFrame.

    Parameters:
        csv_file (str): Name of the CSV file

    Returns:
        pandas.DataFrame: Loaded DataFrame
    """
    csv_filepath = os.path.join(CSV_DIRECTORY, csv_file)
    return pd.read_csv(csv_filepath)


class TestDataColumns:

    def test_loaded_data_has_correct_columns(self, df, expected_columns):
        """
        Test to verify that loaded data has correct columns.

        Parameters:
            df (pandas.DataFrame): Loaded DataFrame
            expected_columns (list): Expected column names
        """
        assert df.columns.to_list() == expected_columns
