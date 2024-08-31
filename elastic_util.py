import logging, os, json
from tqdm.auto import tqdm
from elasticsearch import Elasticsearch

from proj_config import config
from proj_util import check_service

ELASTIC_HOST = "elasticsearch"
ELASTIC_PORT = 9200
ELASTIC_URL = f"http://{ELASTIC_HOST}:{ELASTIC_PORT}"

_logger = logging.getLogger(__name__)

def create_client():
    log_prefix = "create_client"

    if not check_service(ELASTIC_HOST, ELASTIC_PORT):
        _logger.error(f"{log_prefix}: failed!")
        return None

    client = Elasticsearch(ELASTIC_URL)

    _logger.info(f"{log_prefix}: success. info={json.dumps(client.info().raw, indent=2)}")
    return client

def index(es_client, properties, docs):
    log_prefix = "index"

    es_client = create_client()

    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": properties,
        }
    }
    es_client.indices.delete(index=config.elastic_index_name, ignore_unavailable=True)
    es_client.indices.create(index=config.elastic_index_name, body=index_settings)
    for doc in tqdm(docs):
        es_client.index(index=config.elastic_index_name, document=doc)

    _logger.info(f"{log_prefix}: success.")

def query_knn(es_client, embedding_model, field, question):
    v = embedding_model.encode(question)
    knn = {
        "field": field,
        "query_vector": v,
        "k": config.elastic_result_num,
        "num_candidates": 10000
    }
    search_query = {
        "knn": knn,
        "_source": ["text"]
    }
    es_results = es_client.search(
        index=config.elastic_index_name,
        body=search_query
    )

    result_docs = []
    for hit in es_results['hits']['hits']:
        result_docs.append(hit['_source'])
    return result_docs