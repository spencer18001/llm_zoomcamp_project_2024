import logging, time, requests

from sentence_transformers import SentenceTransformer
from openai import OpenAI

from proj_config import config
from proj_util import check_service

# todo_spencer: 外部測試用
OLLAMA_HOST = "ollama"
OLLAMA_PORT = 11434

_logger = logging.getLogger(__name__)
_logger.setLevel(config.logging_level)

def create_embedding_model():
    log_prefix = "create_embedding_model"

    embedding_model = SentenceTransformer(config.embedding_model_name)
    
    _logger.info(f"{log_prefix}: success. embedding_size={embedding_model.get_sentence_embedding_dimension()}")
    return embedding_model

def create_client():
    log_prefix = "create_client"

    if not check_service(OLLAMA_HOST, OLLAMA_PORT):
        _logger.error(f"{log_prefix}: failed!")
        return None
    
    ollama_url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

    response = requests.post(f'{ollama_url}/api/pull', json={
        "name": config.llm_model_name,
        "stream": False
    })
    _logger.debug(f"{log_prefix}: pull model. response={response}")

    return OpenAI(api_key="ollama", base_url=f"{ollama_url}/v1/")

def build_prompt(query, search_results):
    prompt_template = """
You are an expert detective analyzing the details of the story "The Adventure of the Speckled Band." Answer the QUESTION using only the relevant information provided in the CONTEXT from the story.

Make sure to stay true to the facts in the CONTEXT when answering the QUESTION. Avoid adding any outside knowledge or assumptions.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

    context = ""
    for doc in search_results:
        context = context + f"text: {doc['text']}\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def build_prompt2(query, search_results):
    prompt_template = """
You are a meticulous detective focused on delivering fact-based answers strictly derived from the CONTEXT provided from "The Adventure of the Speckled Band." Answer the QUESTION by citing specific lines or details directly from the CONTEXT. Refrain from adding any interpretation or external knowledge.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

    context = ""
    for doc in search_results:
        context = context + f"text: {doc['text']}\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def build_prompt_eval(query, record):
    prompt_template = """
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer_llm}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

    prompt = prompt_template.format(**record)
    return prompt

def llm(llm_client, prompt):
    start_time = time.time()
    response = llm_client.chat.completions.create(
        model=config.llm_model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    end_time = time.time()
    response_time = end_time - start_time
    tokens = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }
    return response.choices[0].message.content, tokens, response_time

def rag(search_func, llm_func, build_prompt_func, query):
    search_results = search_func(query)
    prompt = build_prompt_func(query, search_results)
    answer, tokens, response_time = llm_func(prompt)
    return {
        "answer": answer,
        "response_time": response_time,
        "prompt_tokens": tokens["prompt_tokens"],
        "completion_tokens": tokens["completion_tokens"],
        "total_tokens": tokens["total_tokens"]
    }
