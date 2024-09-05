
import functools
from tqdm.auto import tqdm
import pandas as pd

from proj_config import config
import elastic_util
import llm_util

def get_llm_results(es_client, llm_client, embedding_model, samples, build_prompt_func):
    results = []
    for record in tqdm(samples):
        answer_data = llm_util.rag(
            search_func=functools.partial(elastic_util.query_knn, es_client, embedding_model),
            llm_func=functools.partial(llm_util.llm, llm_client),
            build_prompt_func=build_prompt_func,
            query=record["question"]
        )
        result = {
            'question': record["question"],
            'answer': answer_data.answer,
            'document': record["document"],
        }
        results.append(result)
    df_results = pd.DataFrame(results)
    return pd.DataFrame(results)

if __name__ == "__main__":
    es_client = elastic_util.create_client()
    llm_client = llm_util.create_client()
    embedding_model = llm_util.create_embedding_model()

    df_ground_truth = pd.read_csv(config.ground_truth_file_path)
    df_questions = df_ground_truth.groupby('document').head(1)
    df_sample = df_questions.sample(n=50, random_state=1)
    samples = df_sample.to_dict(orient='records')

    df_results_prompt = get_llm_results(es_client, llm_client, embedding_model, samples, llm_util.build_prompt)
    df_results_prompt.to_csv("llm-results-prompt.csv", index=False)

    df_results_prompt2 = get_llm_results(es_client, llm_client, embedding_model, samples, llm_util.build_prompt2)
    df_results_prompt2.to_csv("llm-results-prompt2.csv", index=False)
    