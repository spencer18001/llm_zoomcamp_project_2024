import logging, functools
from tqdm.auto import tqdm
import pandas as pd

from proj_config import config
from proj_util import setup_logger
import elastic_util
import llm_util
from ingest import ingest

_logger = logging.getLogger(__name__)
setup_logger(_logger)

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
            "question": record["question"],
            "answer": answer_data["answer"],
            "document": record["document"],
        }
        results.append(result)
    return pd.DataFrame(results, columns=["question", "answer", "document"])

if __name__ == "__main__":
    import os

    # todo_spencer: python-dotenv
    # from dotenv import load_dotenv

    # load_dotenv()

    elastic_util.ELASTIC_HOST = "localhost"
    elastic_util.ELASTIC_PORT = os.getenv("ELASTIC_LOCAL_PORT", 9200)
    llm_util.OLLAMA_HOST = "localhost"
    llm_util.OLLAMA__PORT = os.getenv("OLLAMA_LOCAL_PORT", 8501)

    es_client = elastic_util.create_client()
    llm_client = llm_util.create_client()
    embedding_model = llm_util.create_embedding_model()

    _logger.info(f"generating question samples...")
    df_ground_truth = pd.read_csv(config.ground_truth_file_path)
    df_questions = df_ground_truth.groupby('document').head(1)
    df_sample = df_questions.sample(n=config.llm_results_num, random_state=1)
    samples = df_sample.to_dict(orient='records')

    _logger.info(f"getting llm results for prompt...")
    df_results_prompt = get_llm_results(es_client, llm_client, embedding_model, samples, llm_util.build_prompt)
    df_results_prompt.to_csv(config.llm_results_prompt_file_path, index=False)

    _logger.info(f"getting llm results for prompt2...")
    df_results_prompt2 = get_llm_results(es_client, llm_client, embedding_model, samples, llm_util.build_prompt2)
    df_results_prompt2.to_csv(config.llm_results_prompt2_file_path, index=False)
    
    # getting llm results for prompt... elapsed: 20:54
    # getting llm results for prompt2... elapsed: 22:59
