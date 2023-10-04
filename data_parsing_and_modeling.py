import pandas as pd
import numpy as np

# Step 1: Import CSV file
whisky_details_df = pd.read_csv('whisky_details_100.csv')

# Merge 'main_page_df' with 'whisky_details_df' on 'whisky_link' and 'whisky_url'
main_page_df = pd.read_csv('whisky_main_page_with_ratings.csv')
main_page_df.drop_duplicates(
        subset=['whisky_name', 'whisky_age', 'alcohol_pct', 'whisky_rating', 'num_reviews', 'num_ratings'],
        inplace=True
    )
whisky_details_df = pd.merge(whisky_details_df, main_page_df[
    ['whisky_link', 'whisky_name_suffix', 'whisky_rating', 'num_ratings', 'num_reviews']],
                          left_on='whisky_url', right_on='whisky_link', how='left')

# Step 2: Cleaning the features
whisky_details_df['whisky_age'] = whisky_details_df['whisky_age_inner'].apply(
    lambda x: 'NAS' if pd.isna(x) else x.split()[0]) #str(int(x.split()[0])))
whisky_details_df['alcohol_pct'] = whisky_details_df['alcohol_pct_inner'].str.rstrip('%').astype(float)
whisky_details_df['num_ratings'] = whisky_details_df['num_ratings'].str.replace(r'[\(\),]', '', regex=True).astype(float)
whisky_details_df['num_reviews'] = pd.to_numeric(whisky_details_df['num_reviews'], errors='coerce').fillna(0).astype(int)

whisky_details_df['full_name'] = whisky_details_df.apply(lambda row:
    row['distillery_name_inner'] + (" " + row['whisky_age'] if row['whisky_age'] != 'NAS' else "") + \
    (" " + row['whisky_name_suffix'] if not pd.isna(row['whisky_name_suffix']) and row['whisky_name_suffix'] != '' else ""), axis=1)

# Step 4: Create 'post_treatment_possibilities' dictionary and one-hot encode
post_treatment_possibilities = set()
for index, row in whisky_details_df.iterrows():
    if not pd.isna(row['post_treatment']):
        post_treatment_dict = eval(row['post_treatment'])
        for post_treatment in post_treatment_dict:
            post_treatment_possibilities.add(post_treatment)

for possibility in post_treatment_possibilities:
    whisky_details_df[possibility] = whisky_details_df['post_treatment'].apply(
        lambda x: 1 if not pd.isna(x) and possibility in eval(x) else 0)


# Step 5: Create 'average_notes' dictionary and calculate the average
def average_notes(row):
    nosing_notes = eval(row['nosing_notes']) if not pd.isna(row['nosing_notes']) else {}
    tasting_notes = eval(row['tasting_notes']) if not pd.isna(row['tasting_notes']) else {}
    finish_notes = eval(row['finish_notes']) if not pd.isna(row['finish_notes']) else {}

    all_keys = set(nosing_notes.keys()).union(tasting_notes.keys(), finish_notes.keys())

    average_dict = {}
    for key in all_keys:
        total_score = (float(nosing_notes.get(key, 0)) + float(tasting_notes.get(key, 0)) + float(finish_notes.get(key, 0))) / (3*10)
        average_dict[key] = round(total_score)

    return average_dict


whisky_details_df['average_notes'] = whisky_details_df.apply(average_notes, axis=1)

# Step 6: Create 'all_notes' dictionary and one-hot encode
all_notes = set()
for index, row in whisky_details_df.iterrows():
    if not pd.isna(row['average_notes']):
        all_notes.update(row['average_notes'].keys())

for note in all_notes:
    whisky_details_df[note.rstrip(':')] = whisky_details_df['average_notes'].apply(lambda x: x.get(note, 0))

# Step 7: Delete the original columns
whisky_details_df.drop(
    ['whisky_age_inner', 'post_treatment', 'nosing_notes', 'tasting_notes', 'finish_notes', 'average_notes', 'alcohol_pct_inner'], axis=1,
    inplace=True)

# Step 8: Export the final DataFrame to CSV
whisky_details_df.to_csv('whisky_features_100.csv', index=False)
