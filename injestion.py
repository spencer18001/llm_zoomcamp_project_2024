import time, json
import requests
import functools

from tqdm.auto import tqdm
import semchunk
import tiktoken
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from openai import OpenAI

url_elasticsearch = 'http://localhost:9200'

def create_elasticsearch_client():
    while True:
        try:
            response = requests.get(url_elasticsearch)
        except requests.ConnectionError:
            time.sleep(5)
        else:
            break
    client = Elasticsearch(url_elasticsearch)
    print(json.dumps(client.info().raw, indent=4))
    return client

def main():
    print("========== Starting...")

    print("========== Load text file...")
    data_file_path = "data/The_Adventure_of_the_Speckled_Band.txt"
    with open(data_file_path, 'r') as file:
        content = file.read()
    print(f"text content length: {len(content)}")

    print("========== Chunking...")
    chunk_size = 100
    chunker = semchunk.chunkerify(tiktoken.encoding_for_model("gpt-4o"), chunk_size)
    chunks = chunker(content)
    print(f"chunks #: {len(chunks)}")
    print(f"1st chunk length: {len(chunks[0])}")
    
    print("========== Load embedding model...")
    model_name = 'all-mpnet-base-v2'
    embedding_model = SentenceTransformer(model_name)
    embedding_size = embedding_model.get_sentence_embedding_dimension()
    print(f"embedding size: {embedding_size}")

    print("========== Embedding chunks...")
    docs = []
    for chunk in tqdm(chunks):
        doc = {
            'text': chunk,
            'vector': embedding_model.encode(chunk),
        }
        docs.append(doc)

    print("========== Creating elasticsearch client...")
    es_client = create_elasticsearch_client()

    print("========== Indexing chunks...")
    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "vector": {
                    "type": "dense_vector",
                    "dims": embedding_size,
                    "index": True,
                    "similarity": "cosine"
                },
            }
        }
    }
    index_name = "story_chunks"
    es_client.indices.delete(index=index_name, ignore_unavailable=True)
    es_client.indices.create(index=index_name, body=index_settings)
    for doc in tqdm(docs):
        es_client.index(index=index_name, document=doc)

    print("========== Done!")

if __name__ == "__main__":
    main()