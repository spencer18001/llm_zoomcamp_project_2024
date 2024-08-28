import streamlit as st
import time
import uuid

import time, json
import requests
import functools
from tqdm.auto import tqdm
import semchunk
import tiktoken
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from openai import OpenAI

index_name = "story_chunks"

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

def elasticsearch_knn(es_client, field, vector):
    knn = {
        "field": field,
        "query_vector": vector,
        "k": 5,
        "num_candidates": 10000
    }

    search_query = {
        "knn": knn,
        "_source": ["text"]
    }

    es_results = es_client.search(
        index=index_name,
        body=search_query
    )

    result_docs = []
    for hit in es_results['hits']['hits']:
        result_docs.append(hit['_source'])
    return result_docs

url_ollama = 'http://localhost:11434'

def create_ollama_client(model):
    while True:
        try:
            response = requests.get(url_ollama)
        except requests.ConnectionError:
            time.sleep(5)
        else:
            print(response.content.decode())
            break
    
    response = requests.post(f'{url_ollama}/api/pull', json={"name": model})
    print(response.status_code)
    print(response)

    while True:
        response = requests.get(f'{url_ollama}/api/tags')
        if len(response.json().get("models", [])) > 0:
            print(json.dumps(response.json(), indent=4))
            break
        time.sleep(5)

    api_key = "ollama"
    base_url = f"{url_ollama}/v1/"
    return OpenAI(api_key=api_key, base_url=base_url)

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

def llm_ollama(client, prompt, model_name):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def rag(search_func, llm_func, build_prompt_func, query, query_vec, model_name):
    search_results = search_func(query_vec)
    prompt = build_prompt_func(query, search_results)
    answer = llm_func(prompt, model_name)
    return answer

def main():
    st.title("Detective Assistant")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    if 'initialized' not in st.session_state:
        with st.spinner('Loading...'):
            print("create es_client...")
            st.session_state.es_client = create_elasticsearch_client()
            print("create embedding_model...")
            st.session_state.embedding_model = SentenceTransformer('all-mpnet-base-v2')
            print("create ol_client...")
            st.session_state.ol_client = create_ollama_client('phi3')

            st.session_state.initialized = True
            print("initialized")
    else:
        es_client = st.session_state.es_client
        embedding_model = st.session_state.embedding_model
        ol_client = st.session_state.ol_client

    # Session state initialization
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())

    user_input = st.text_input("Enter your question:")
    if st.button("Ask"):
        with st.spinner('Processing...'):
            question = user_input
            v = embedding_model.encode(question)
            answer = rag(
                search_func=functools.partial(elasticsearch_knn, es_client, 'vector'),
                llm_func=functools.partial(llm_ollama, ol_client),
                build_prompt_func=build_prompt,
                query=question,
                query_vec=v,
                model_name='phi3'
            )
            st.success("Completed!")
            st.write(answer)

if __name__ == "__main__":
    main()