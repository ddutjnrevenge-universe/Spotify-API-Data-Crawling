import boto3
import os

# AWS S3 configuration
bucket_name = 'batch10-nguyentnh-proj'
staging_folder = 'staging'

# Local directory containing the files
local_directory = r'F:\Data_Engineering\SpotifyPipeline\data'

# Initialize a session using Amazon S3
s3 = boto3.client('s3')

def upload_files(local_directory, bucket_name, staging_folder):
    for filename in ['albums.csv', 'artists.csv', 'tracks.csv']:
        local_file_path = os.path.join(local_directory, filename)
        s3_file_path = f"{staging_folder}/{filename}"
        
        try:
            # Upload the file
            s3.upload_file(local_file_path, bucket_name, s3_file_path)
            print(f"Successfully uploaded {filename} to {s3_file_path}")
        except Exception as e:
            print(f"Error uploading {filename}: {e}")

# Execute the function
upload_files(local_directory, bucket_name, staging_folder)
