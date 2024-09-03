import logging
from tqdm.auto import tqdm
import pandas as pd

from proj_config import config
import elastic_util
import llm_util

def hit_rate(relevance_total):
    cnt = 0
    for line in relevance_total:
        if True in line:
            cnt = cnt + 1
    return cnt / len(relevance_total)

def mrr(relevance_total):
    total_score = 0.0
    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] == True:
                total_score = total_score + 1 / (rank + 1)
    return total_score / len(relevance_total)

def eval(es_client, embedding_model, search_func):
    relevance_total = []
    for q in tqdm(ground_truth):
        doc_id = q['document']
        results = search_func(es_client, embedding_model, q['question'])
        relevance = [d['id'] == doc_id for d in results]
        relevance_total.append(relevance)
    return hit_rate(relevance_total), mrr(relevance_total)

if __name__ == "__main__":
    import os
    
    # todo_spencer: python-dotenv
    # from dotenv import load_dotenv

    # load_dotenv()

    elastic_util.ELASTIC_HOST = "localhost"
    elastic_util.ELASTIC_PORT = os.getenv("ELASTIC_LOCAL_PORT", 9200)

    df_ground_truth = pd.read_csv(config.ground_truth_file_path)
    ground_truth = df_ground_truth.to_dict(orient='records')

    es_client = elastic_util.create_client()
    embedding_model = llm_util.create_embedding_model()

    text_results = eval(es_client, embedding_model, elastic_util.query_text)
    vector_results = eval(es_client, embedding_model, elastic_util.query_knn)
    print(f"text: (hit_rate, mrr)={text_results}")
    print(f"vector: (hit_rate, mrr)={vector_results}")
    # todo_spencer
    # text: (hit_rate, mrr)=(0.7419753086419754, 0.6061522633744849)
    # vector: (hit_rate, mrr)=(0.7617283950617284, 0.6104526748971189)
