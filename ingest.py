import logging
from tqdm.auto import tqdm
import semchunk
import tiktoken

from proj_config import config
import elastic_util
import llm_util

_logger = logging.getLogger(__name__)
_logger.setLevel(config.logging_level)

def load_text():
    log_prefix = "load_text"

    with open(config.data_file_path, 'r') as file:
        content = file.read()

    _logger.info(f"{log_prefix}: success. text_len={len(content)}")
    return content

def chunk(content):
    log_prefix = "chunk"

    chunker = semchunk.chunkerify(tiktoken.encoding_for_model(config.chunk_model_name), config.chunk_size)
    chunks = chunker(content)

    _logger.info(f"{log_prefix}: success. chunks#={len(chunks)}, avg_chunk_len={int(sum([len(s) for s in chunks]) / len(chunks))}")
    return chunks

def embed_chunks(chunks, embedding_model):
    log_prefix = "embed_chunks"

    docs = []
    for i, chunk in enumerate(tqdm(chunks)):
        doc = {
            "text": chunk,
            "vector": embedding_model.encode(chunk),
            "id": i,
        }
        docs.append(doc)

    _logger.info(f"{log_prefix}: success.")
    return docs

def index_docs(embedding_size, docs):
    log_prefix = "index_docs"

    es_client = elastic_util.create_client()

    properties = {
        "text": {"type": "text"},
        "vector": {
            "type": "dense_vector",
            "dims": embedding_size,
            "index": True,
            "similarity": "cosine"
        },
        "id": {"type": "keyword"},
    }
    elastic_util.index(es_client, properties, docs)

    _logger.info(f"{log_prefix}: success.")

def ingest():
    log_prefix = "ingest"

    content = load_text()
    chunks = chunk(content)
    embedding_model = llm_util.create_embedding_model()
    docs = embed_chunks(chunks, embedding_model)
    embedding_size = embedding_model.get_sentence_embedding_dimension()
    index_docs(embedding_size, docs)

    _logger.info(f"{log_prefix}: success.")

if __name__ == "__main__":
    import os
    
    # todo_spencer: python-dotenv
    from dotenv import load_dotenv

    load_dotenv()

    elastic_util.ELASTIC_HOST = "localhost"
    elastic_util.ELASTIC_PORT = os.getenv("ELASTIC_LOCAL_PORT", 9200)

    ingest()
