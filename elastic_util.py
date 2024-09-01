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

def check_inited(es_client):
    return es_client.indices.exists(index=config.elastic_index_name)

def index(es_client, properties, docs):
    log_prefix = "index"

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

def query_knn(es_client, embedding_model, question):
    v = embedding_model.encode(question)
    knn = {
        "field": "vector",
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

def query_hybrid(es_client, embedding_model, question):
    v = embedding_model.encode(question)
    knn_query = {
        "field": "vector",
        "query_vector": v,
        "k": config.elastic_result_num,
        "num_candidates": 10000,
        "boost": 0.5
    }
    keyword_query = {
        "bool": {
            "must": {
                "multi_match": {
                    "query": question,
                    "fields": ["text"],
                    "type": "best_fields",
                    "boost": 0.5,
                }
            }
        }
    }
    search_query = {
        "knn": knn_query,
        "query": keyword_query,
        "size": config.elastic_result_num,
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

def compute_rrf(rank, k=60):
    return 1 / (k + rank)

def query_hybrid_rrf(es_client, embedding_model, question):
    v = embedding_model.encode(question)
    knn_query = {
        "field": "vector",
        "query_vector": v,
        "k": config.elastic_result_num * 2,
        "num_candidates": 10000,
        "boost": 0.5
    }
    keyword_query = {
        "bool": {
            "must": {
                "multi_match": {
                    "query": question,
                    "fields": ["text"],
                    "type": "best_fields",
                    "boost": 0.5,
                }
            }
        }
    }
    knn_results = es_client.search(
        index=config.elastic_index_name,
        body={
            "knn": knn_query, 
            "size": config.elastic_result_num * 2,
        }
    )['hits']['hits']
    keyword_results = es_client.search(
        index=config.elastic_index_name,
        body={
            "query": keyword_query, 
            "size": config.elastic_result_num * 2,
        }
    )['hits']['hits']
    
    rrf_scores = {}
    for rank, hit in enumerate(knn_results):
        doc_id = hit['_id']
        rrf_scores[doc_id] = compute_rrf(rank + 1)

    for rank, hit in enumerate(keyword_results):
        doc_id = hit['_id']
        if doc_id in rrf_scores:
            rrf_scores[doc_id] += compute_rrf(rank + 1)
        else:
            rrf_scores[doc_id] = compute_rrf(rank + 1)

    reranked_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    
    final_results = []
    for doc_id, score in reranked_docs[:config.elastic_result_num]:
        doc = es_client.get(index=config.elastic_index_name, id=doc_id)
        final_results.append(doc['_source'])
    return final_results
