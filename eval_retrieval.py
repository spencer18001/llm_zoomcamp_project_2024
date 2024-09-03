import pandas as pd

from tqdm.auto import tqdm

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
    df_ground_truth = pd.read_csv('ground-truth-data.csv')
    ground_truth = df_ground_truth.to_dict(orient='records')

    es_client = elastic_util.create_client()
    embedding_model = llm_util.create_embedding_model()

    print(f"text: (hit_rate, mrr)={eval(es_client, embedding_model, elastic_util.query_text)}")
    print(f"text: (hit_rate, mrr)={eval(es_client, embedding_model, elastic_util.query_knn)}")
