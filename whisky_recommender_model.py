import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load your whisky DataFrame (replace 'whisky_data.csv' with your file)
whisky_df = pd.read_csv('whisky_features_100.csv')

# Assuming the user provides three whisky names
user_whiskies = ["Lagavulin 16", "Ardbeg 10 TEN", "Talisker 10"]

# Filter the DataFrame to get the data for the user's selected whiskies
user_whisky_data = whisky_df[whisky_df['full_name'].isin(user_whiskies)]

# Drop any duplicate rows (in case the user selected the same whisky multiple times)
user_whisky_data = user_whisky_data.drop_duplicates(subset='full_name')

# Extract the tasting note features and scores
user_features = user_whisky_data.iloc[:, 18:]  # Columns 18 and onwards are the tasting note features

# Calculate the mean of the user's selected whiskies' feature vectors
user_profile = user_features.mean(axis=0)

# Calculate cosine similarity between the user profile and all whiskies in the dataset
cosine_sim = cosine_similarity([user_profile], whisky_df.iloc[:, 18:])  # Columns 18 and onwards are the tasting note features

# Convert cosine similarity results to a DataFrame
similarity_df = pd.DataFrame({'full_name': whisky_df['full_name'], 'Cosine_Similarity': cosine_sim[0]})

# Sort whiskies by similarity in descending order
similarity_df = similarity_df.sort_values(by='Cosine_Similarity', ascending=False)

# Recommended the top whisky (excluding the user's selections)
recommended_whisky = similarity_df[~similarity_df['full_name'].isin(user_whiskies)].iloc[0]['full_name']

# Extract tasting notes for the recommended whisky
recommended_whisky_notes = whisky_df.loc[whisky_df['full_name'] == recommended_whisky, user_features.columns].values[0]

# Extract tasting notes for the user's selected whiskies
user_selected_notes = user_features.values[0]

# Find the common high tasting notes between the recommended whisky and user-selected whiskies
common_high_notes = []
for idx, (recommended_note, user_note) in enumerate(zip(recommended_whisky_notes, user_selected_notes)):
    if recommended_note >= 8 and user_note >= 8:
        common_high_notes.append(user_features.columns[idx])

# Sort the common high notes by their values in the recommended whisky
common_high_notes.sort(key=lambda x: recommended_whisky_notes[user_features.columns.get_loc(x)], reverse=True)

# Get the top three additional tasting notes with the highest values in the recommended whisky
additional_notes = [note for note in user_features.columns if note not in common_high_notes]
additional_notes.sort(key=lambda x: recommended_whisky_notes[user_features.columns.get_loc(x)], reverse=True)
top_additional_notes = additional_notes[:3]

print(f"Recommended Whisky: {recommended_whisky}")
print(f"Top Three Common High Tasting Notes: {', '.join(common_high_notes[:3])}")
print(f"Top Three Additional Tasting Notes in Recommended Whisky: {', '.join(top_additional_notes)}")