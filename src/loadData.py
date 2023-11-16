import os
import json
import pandas as pd
import numpy as np
import redis
import shutil
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Directories for data and loaded files
data_dir = 'data/embeddings'
loaded_dir = 'data/embeddings/loaded'
os.makedirs(loaded_dir, exist_ok=True)  # create 'loaded' directory if it doesn't exist


def process_csv(csv_file):
    print(f"Processing file: {csv_file}")  # Print the name of the file being processed

    # Read the CSV file into a DataFrame
    df = pd.read_csv(os.path.join(data_dir, csv_file), index_col=0)

    # Reset index
    df = df.reset_index()

    # Convert the embeddings column to a list of numpy arrays
    df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Prepare the data
        data = {
            'embeddings': row['embeddings'].tolist(),
            'n_tokens': row['n_tokens'],
            'text': row['text']
        }
        # Serialize the embeddings, n_tokens, and text, and store them in Redis
        redis_client.set(str(index), json.dumps(data))

    # After successfully processing, move the file to the 'loaded' directory
    shutil.move(os.path.join(data_dir, csv_file), os.path.join(loaded_dir, csv_file))
    print(f"Successfully moved file: {csv_file} to the 'loaded' directory")  # Print the name of the file being moved


while True:
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

    for csv_file in csv_files:
        process_csv(csv_file)

    # Sleep for 1 second before checking again
    print("Sleeping for 60 seconds before checking for new data")
    time.sleep(60)
