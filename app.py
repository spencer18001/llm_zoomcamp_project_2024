import logging, uuid
import functools

from tqdm.auto import tqdm
import streamlit as st

from proj_config import config
import elastic_util
import llm_util
import db_util

_logger = logging.getLogger(__name__)

def app_main():
    st.title("Detective Assistant")
    
    if 'initialized' not in st.session_state:
        with st.spinner('Loading...'):
            print("create es_client...")
            st.session_state.es_client = elastic_util.create_client()
            print("create embedding_model...")
            st.session_state.embedding_model = llm_util.create_embedding_model()
            print("create llm_client...")
            st.session_state.llm_client = llm_util.create_client()

            st.session_state.initialized = True
            print("initialized")
    else:
        es_client = st.session_state.es_client
        embedding_model = st.session_state.embedding_model
        llm_client = st.session_state.llm_client

    user_input = st.text_input("Enter your question:")
    if st.button("Ask"):
        with st.spinner('Processing...'):
            question = user_input
            answer_data = llm_util.rag(
                search_func=functools.partial(elastic_util.query_knn, es_client, embedding_model, 'vector'),
                llm_func=functools.partial(llm_util.llm, llm_client, embedding_model),
                build_prompt_func=llm_util.build_prompt,
                query=question
            )
            st.success("Completed!")
            st.write(answer_data['answer'])
            st.write(f"Response time: {answer_data['response_time']:.2f} seconds")
            st.write(f"Total tokens: {answer_data['total_tokens']}")

            conversation_id = str(uuid.uuid4())
            db_util.save_conversation(conversation_id, user_input, answer_data)

if __name__ == "__main__":
    logging.basicConfig(level=config.logging_level)

    # todo_spencer
    elastic_util.ELASTIC_HOST = "localhost"
    llm_util.OLLAMA_HOST = "localhost"
    db_util.POSTGRES_HOST = "localhost"

    app_main()
