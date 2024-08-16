"""
This script extracts and processes music data from Spotify using the Spotify Web API.

The script performs the following tasks:
1. Initialization:
   - Loads environment variables for Spotify API credentials.
   - Sets up logging for tracking the script's execution.
   - Initializes instances of `SpotifyDataManager` and `SpotifyDataFetcher`.

2. Data Extraction and Processing:
   - Retrieves album IDs for a specified list of artists.
   - Fetches and processes album data, including cleaning and deduplication.
   - Extracts track IDs and fetches related audio features and track data.
   - Retrieves and processes artist data.

3. Data Storage:
   - Saves the processed data to CSV files in a specified output directory.

Dependencies:
- `logging` for logging script activities.
- `os` for environment variable management and file operations.
- `pandas` for data manipulation and storage.
- `dotenv` for loading environment variables from a `.env` file.
- `core.spotify_data_manager` and `core.spotify_data_fetcher` for interacting with the Spotify API.

Configuration:
- The script requires Spotify API credentials (`client_id` and `client_secret`) which should be defined in a `.env` file.
- The list of artists to analyze is specified in the `artist_list` variable.

Usage:
- Run the script to initialize the data extraction process, fetch and process Spotify data, and save the results to CSV files.
"""
import logging
import os
import pandas as pd
from dotenv import load_dotenv
from core.spotify_data_manager import SpotifyDataManager
from core.spotify_data_fetcher import SpotifyDataFetcher

# Configuration Variables
artist_list = ["One Direction", "Taylor Swift", "Little Mix", "Ed Sheeran", "Ariana Grande", "Olivia Rodrigo", "BTS", "Sabrina Carpenter", "Billie Eilish", "Lauv", "Jeremy Zucker"]

# Path for Dataform logic (not used here, but kept for context)
# dataform_files_path = "dataform_logic"

load_dotenv()  # take environment variables from .env.
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Initialize instances
    logging.info("Initializing instances")
    spotify_manager = SpotifyDataManager(client_id, client_secret)
    token = spotify_manager.get_token()
    spotify_fetcher = SpotifyDataFetcher(token)

    # Spotify Data Extraction and Processing
    logging.info("Extracting and processing Spotify albums data")
    album_ids = spotify_manager.get_album_ids(artist_list)
    print("Album IDs: ",  album_ids[:1])
    albums_data = spotify_manager.get_album_data(album_ids)
    # print("Album Data: ", albums_data)
    # Only print the first album data
    print("Album Data: ", albums_data[:1][0])
    albums_df = spotify_manager.albums_df(albums_data)
    print("Albums DF: ", albums_df)
    albums_df = albums_df.drop_duplicates(subset=["track_id"])
    cleaned_albums_df = spotify_fetcher.cleanup(albums_df)
    print("Cleaned albums df: ", cleaned_albums_df)

    logging.info("Now fetching track ids")
    track_ids = cleaned_albums_df['track_id'].tolist()
    logging.info("Extracting and processing features data")
    features_df = spotify_fetcher.features_df(track_ids)
    logging.info("Extracting and processing tracks data")
    tracks_df = spotify_fetcher.tracks_df(track_ids)
    logging.info("Now fetching artist ids")
    artist_ids = cleaned_albums_df['artist_id'].unique()
    logging.info("Now fetching artist data")
    artists_df = spotify_fetcher.artists_df(artist_ids)

    # Save data to CSV files
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

    logging.info("Saving data to CSV files")
    cleaned_albums_df.to_csv(os.path.join(output_dir, 'albums.csv'), index=False)
    features_df.to_csv(os.path.join(output_dir, 'features.csv'), index=False)
    tracks_df.to_csv(os.path.join(output_dir, 'tracks.csv'), index=False)
    artists_df.to_csv(os.path.join(output_dir, 'artists.csv'), index=False)

    logging.info("Script finished")

if __name__ == "__main__":
    main()
