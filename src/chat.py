import os
import numpy as np
import pandas as pd
import redis
import openai
import json
from dotenv import load_dotenv
from openai.embeddings_utils import distances_from_embeddings

# Load variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")  # Get API key from environment variable
redis_client = redis.Redis(host='localhost', port=6379, db=0)


def load_embeddings_from_redis():
    """Loads embeddings, n_tokens, and text from Redis and returns a DataFrame"""
    df = pd.DataFrame(columns=['embeddings', 'n_tokens', 'text'])
    for key in redis_client.scan_iter():
        data_json = redis_client.get(key)
        if data_json is not None and data_json.strip() != b'':  # Verify data_json is not None and not empty
            data_json = data_json.decode('utf-8')  # Decode the bytes to a string
            try:
                data = json.loads(data_json)  # Attempt to parse JSON
            except json.JSONDecodeError:  # Handle invalid JSON
                print(f"Invalid JSON for key {key}: {data_json}")
                continue
            embeddings = np.array(data['embeddings'])
            n_tokens = data['n_tokens']
            text = data['text']
            df.loc[key] = [embeddings, n_tokens, text]
    return df


df = load_embeddings_from_redis()


def create_context(question, df, max_len=1800):
    """Creates a context for a given question"""
    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

    # Get the distances from the embeddings
    df['distances'] = distances_from_embeddings(q_embeddings, df['embeddings'].values, distance_metric='cosine')

    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        # Add the length of the text to the current length
        cur_len += row['n_tokens'] + 4

        # If the context is too long, break
        if cur_len > max_len:
            break

        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return None if no relevant context found
    if not returns:
        return None

    # Return the context
    return "\n\n###\n\n".join(returns)
