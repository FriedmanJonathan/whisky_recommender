import pandas as pd
import numpy as np

# Step 1: Import CSV file
whisky_details_df = pd.read_csv('whisky_details_template.csv')

# Step 2: Clean 'whisky_age_inner'
whisky_details_df['whisky_age'] = whisky_details_df['whisky_age_inner'].apply(
    lambda x: 'NAS' if pd.isna(x) else str(int(x.split()[0])))

# Step 3: Clean 'alcohol_pct'
whisky_details_df['alcohol_pct'] = whisky_details_df['alcohol_pct'].str.rstrip('%').astype(float)

# Step 4: Create 'post_treatment_possibilities' dictionary and one-hot encode
post_treatment_possibilities = set()
for index, row in whisky_details_df.iterrows():
    if not pd.isna(row['post_treatment']):
        post_treatment_dict = eval(row['post_treatment'])
        for key in post_treatment_dict.keys():
            post_treatment_possibilities.add(key.replace(' ', '_'))

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
        total_score = (nosing_notes.get(key, 0) + tasting_notes.get(key, 0) + finish_notes.get(key, 0)) / 10
        average_dict[key] = round(total_score)

    return average_dict


whisky_details_df['average_notes'] = whisky_details_df.apply(average_notes, axis=1)

# Step 6: Create 'all_notes' dictionary and one-hot encode
all_notes = set()
for index, row in whisky_details_df.iterrows():
    if not pd.isna(row['average_notes']):
        all_notes.update(row['average_notes'].keys())

for note in all_notes:
    whisky_details_df[note.replace(' ', '_')] = whisky_details_df['average_notes'].apply(lambda x: x.get(note, 0))

# Step 7: Delete the original columns
whisky_details_df.drop(
    ['whisky_age_inner', 'post_treatment', 'nosing_notes', 'tasting_notes', 'finish_notes', 'average_notes'], axis=1,
    inplace=True)

# Step 8: Export the final DataFrame to CSV
whisky_details_df.to_csv('whisky_features_template.csv', index=False)
