import pandas as pd

# Paths to input and output CSVs
DETAILS_CSV_PATH = '../../data/raw/2024_05/whisky_details_all.csv'
MAIN_PAGE_CSV_PATH = '../../data/raw/2024_05/whisky_main_page_with_ratings.csv'
OUTPUT_CSV_PATH = '../../data/processed/2024_05/whisky_features_test.csv'
DISTILLERY_OUTPUT_CSV_PATH = '../../frontend/distillery_data.csv'


def load_and_merge_data(details_path, main_page_path):
    """Load data from the given CSV files and merge the details with the main page data."""
    whisky_details_df = pd.read_csv(details_path)
    main_page_df = pd.read_csv(main_page_path)

    # Merge based on 'whisky_link' and 'whisky_url'
    whisky_details_df = pd.merge(
        whisky_details_df,
        main_page_df[['whisky_link', 'whisky_name_suffix', 'whisky_rating', 'num_ratings', 'num_reviews']],
        left_on='whisky_url',
        right_on='whisky_link',
        how='left'
    )

    # Drop duplicates based on notes - if identical for all tw
    whisky_details_df.drop_duplicates(
        subset=['nosing_notes','tasting_notes','finish_notes'],
        inplace=True
    )

    return whisky_details_df


def clean_features(whisky_details_df):
    """Clean feature columns in the whisky details DataFrame."""
    whisky_details_df['whisky_age'] = whisky_details_df['whisky_age_inner'].apply(
        lambda x: 'NAS' if pd.isna(x) else x.split()[0])
    whisky_details_df['alcohol_pct'] = whisky_details_df['alcohol_pct_inner'].str.rstrip('%').astype(float)
    whisky_details_df['num_ratings'] = whisky_details_df['num_ratings'].str.replace(r'[\(\),]', '', regex=True).astype(float)
    whisky_details_df['num_reviews'] = pd.to_numeric(whisky_details_df['num_reviews'], errors='coerce').fillna(0).astype(int)

    whisky_details_df['full_name'] = whisky_details_df.apply(
        lambda row: f"{row['distillery_name_inner']} "
                    f"{row['whisky_age'] if row['whisky_age'] != 'NAS' else ''} "
                    f"{row['whisky_name_suffix'] if pd.notna(row['whisky_name_suffix']) else ''}".strip(),
        axis=1
    )
    return whisky_details_df


def one_hot_encode_post_treatment(whisky_details_df):
    """One-hot encode the post-treatment information."""
    post_treatment_possibilities = set()
    for index, row in whisky_details_df.iterrows():
        if not pd.isna(row['post_treatment']):
            post_treatment_dict = eval(row['post_treatment'])
            post_treatment_possibilities.update(post_treatment_dict)

    for possibility in post_treatment_possibilities:
        whisky_details_df[possibility] = whisky_details_df['post_treatment'].apply(
            lambda x: 1 if not pd.isna(x) and possibility in eval(x) else 0
        )
    return whisky_details_df


def calculate_average_notes(row):
    """Calculate the average notes for nosing, tasting, and finish."""
    nosing_notes = eval(row['nosing_notes']) if not pd.isna(row['nosing_notes']) else {}
    tasting_notes = eval(row['tasting_notes']) if not pd.isna(row['tasting_notes']) else {}
    finish_notes = eval(row['finish_notes']) if not pd.isna(row['finish_notes']) else {}

    all_keys = set(nosing_notes.keys()).union(tasting_notes.keys(), finish_notes.keys())

    average_dict = {}
    for key in all_keys:
        total_score = (float(nosing_notes.get(key, 0)) + float(tasting_notes.get(key, 0)) + float(finish_notes.get(key, 0))) / (3 * 10)
        average_dict[key] = round(total_score)

    return average_dict


def one_hot_encode_average_notes(whisky_details_df):
    """One-hot encode the average notes for nosing, tasting, and finish."""
    whisky_details_df['average_notes'] = whisky_details_df.apply(calculate_average_notes, axis=1)

    all_notes = set()
    for index, row in whisky_details_df.iterrows():
        if not pd.isna(row['average_notes']):
            all_notes.update(row['average_notes'].keys())

    for note in all_notes:
        whisky_details_df[note.rstrip(':')] = whisky_details_df['average_notes'].apply(lambda x: x.get(note, 0))
    return whisky_details_df


def drop_unnecessary_columns(whisky_details_df):
    """Drop unnecessary columns from the whisky details DataFrame."""
    columns_to_drop = [
        'whisky_age_inner', 'post_treatment', 'nosing_notes', 'tasting_notes',
        'finish_notes', 'average_notes', 'alcohol_pct_inner'
    ]
    whisky_details_df.drop(columns=columns_to_drop, axis=1, inplace=True)
    return whisky_details_df


def create_distillery_data_table(whisky_details_df):
    """
    Create a table with distillery names and concatenated whisky names.
    Only include whisky age in the name if it is not 'NAS', and include the whisky_name_suffix if it exists.
    """
    # Ensure clean data by removing leading/trailing whitespace
    whisky_details_df['whisky_age'] = whisky_details_df['whisky_age'].str.strip()
    whisky_details_df['whisky_name_suffix'] = whisky_details_df['whisky_name_suffix'].str.strip()

    # Concatenate whisky age and suffix if applicable
    whisky_details_df['whisky_name'] = whisky_details_df.apply(
        lambda
            row: f"{row['whisky_age'] + ' ' if row['whisky_age'] != 'NAS' else ''}{row['whisky_name_suffix'] if pd.notna(row['whisky_name_suffix']) else ''}".strip(),
        axis=1
    )

    # Create a new DataFrame for the CSV output
    distillery_data = whisky_details_df[['distillery_name_inner', 'whisky_name']].rename(
        columns={'distillery_name_inner': 'distillery'})

    # Drop duplicates to ensure each distillery-whisky pair is unique
    distillery_data = distillery_data.drop_duplicates()

    # Write to CSV
    distillery_data.to_csv(DISTILLERY_OUTPUT_CSV_PATH, index=False)

    print("Distillery data table created successfully.")


def main():
    """Main function to orchestrate data loading, cleaning, transformation, and export."""
    # Step 1: Load and merge data
    whisky_details_df = load_and_merge_data(DETAILS_CSV_PATH, MAIN_PAGE_CSV_PATH)

    # Step 2: Clean features
    whisky_details_df = clean_features(whisky_details_df)

    # Step 3: One-hot encode post-treatment
    whisky_details_df = one_hot_encode_post_treatment(whisky_details_df)

    # Step 4: One-hot encode average notes
    whisky_details_df = one_hot_encode_average_notes(whisky_details_df)

    # Step 5: Drop unnecessary columns
    whisky_details_df = drop_unnecessary_columns(whisky_details_df)

    # Step 6: Export the final DataFrame to CSV
    whisky_details_df.to_csv(OUTPUT_CSV_PATH, index=False)

    # Step 7: Create distillery data table
    create_distillery_data_table(whisky_details_df)


if __name__ == '__main__':
    main()
