"""
Whisky Recommender Module

This module provides functionality to recommend whiskies based on user-selected whiskies
and their tasting notes. It uses cosine similarity to find the most similar whisky in the
dataset to the user's profile and identifies common and additional tasting notes.

Functions:
    recommend_whisky(whisky_data_file, user_whiskies): Recommends a whisky and identifies common
    and additional tasting notes.

Example usage shown in bottom of script.
"""

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def recommend_whisky(whisky_data_file, user_whiskies):
    """
    Recommend a whisky based on user-selected whiskies and identify common and additional
    tasting notes.

    Parameters:
    whisky_data_file (str): Path to the CSV file containing whisky data with tasting notes.
    user_whiskies (list of str): List of whiskies selected by the user.

    Returns:
    dict: A dictionary containing the recommended whisky, top three common high tasting notes,
          and top three additional tasting notes in the recommended whisky.
    """
    # Load the whisky DataFrame
    whisky_df = pd.read_csv(whisky_data_file)

    # Filter the DataFrame to get the data for the user's selected whiskies
    user_whisky_data = whisky_df[whisky_df["full_name"].isin(user_whiskies)]

    # Drop any duplicate rows (in case the user selected the same whisky multiple times)
    user_whisky_data = user_whisky_data.drop_duplicates(subset="full_name")

    # Extract the tasting note features and scores
    user_features = user_whisky_data.iloc[:, 18:]

    # Calculate the mean of the user's selected whiskies' feature vectors
    user_profile = user_features.mean(axis=0)

    # Calculate cosine similarity between the user profile and all whiskies in the dataset
    cosine_sim = cosine_similarity([user_profile], whisky_df.iloc[:, 18:])

    # Convert cosine similarity results to a DataFrame
    similarity_df = pd.DataFrame(
        {"full_name": whisky_df["full_name"], "Cosine_Similarity": cosine_sim[0]}
    )

    # Sort whiskies by similarity in descending order
    similarity_df = similarity_df.sort_values(by="Cosine_Similarity", ascending=False)

    # Recommend the top whisky (excluding the user's selections)
    recommended_whisky = similarity_df[
        ~similarity_df["full_name"].isin(user_whiskies)
    ].iloc[0]["full_name"]

    # Extract tasting notes for the recommended whisky
    recommended_whisky_notes = whisky_df.loc[
        whisky_df["full_name"] == recommended_whisky, user_features.columns
    ].values[0]

    # Extract tasting notes for the user's selected whiskies
    user_selected_notes = user_features.values[0]

    # Find the common high tasting notes between the recommended whisky and user-selected whiskies
    common_high_notes = []
    for idx, (recommended_note, user_note) in enumerate(
        zip(recommended_whisky_notes, user_selected_notes)
    ):
        if recommended_note >= 8 and user_note >= 8:
            common_high_notes.append(user_features.columns[idx])

    # Sort the common high notes by their values in the recommended whisky
    common_high_notes.sort(
        key=lambda x: recommended_whisky_notes[user_features.columns.get_loc(x)],
        reverse=True,
    )

    # Get the top three additional tasting notes with the highest values in the recommended whisky
    additional_notes = [
        note for note in user_features.columns if note not in common_high_notes
    ]
    additional_notes.sort(
        key=lambda x: recommended_whisky_notes[user_features.columns.get_loc(x)],
        reverse=True,
    )
    top_additional_notes = additional_notes[:3]

    # Return modeling details as a dictionary
    return {
        "Recommended Whisky": recommended_whisky,
        "Top Three Common High Tasting Notes": common_high_notes[:3],
        "Top Three Additional Tasting Notes in Recommended Whisky": top_additional_notes,
    }


# Example usage:
if __name__ == "__main__":
    user_whiskies = ["Lagavulin 16", "Ardbeg 10 TEN", "Laphroaig 10"]
    result = recommend_whisky(
        "../../data/processed/2023_09/whisky_features_100.csv", user_whiskies
    )
    print("Recommendation Results:")
    for key, value in result.items():
        print(f"{key}: {value}")
