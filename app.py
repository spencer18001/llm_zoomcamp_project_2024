import time, uuid, functools

import streamlit as st

from proj_config import config
from log_util import get_logger
from ingest import ingest
import elastic_util
import llm_util
import db_util
import grafana_util

_logger = get_logger(__name__)

def init():
    st.write("🔍 **Checking if Elasticsearch index exists...**")
    if not elastic_util.check_inited(st.session_state.es_client):
        st.write("🛠️ **Elasticsearch index does not exist. Creating index...**")
        ingest()
        st.write("✅ **Elasticsearch index created successfully.**")
    else:
        st.write("✅ **Elasticsearch index already exists.**")

    st.write("🔍 **Checking if database tables are created...**")
    if not db_util.check_inited():
        st.write("🛠️ **Database tables do not exist. Creating tables...**")
        db_util.init_db()
        st.write("✅ **Database tables created successfully.**")
    else:
        st.write("✅ **Database tables already exist.**")

    st.write("🔍 **Checking if Grafana dashboard is set up...**")
    if not grafana_util.check_inited():
        st.write("🛠️ **Grafana dashboard is not set up. Setting up dashboard...**")
        grafana_util.init_grafana()
        st.write("✅ **Grafana dashboard set up successfully.**")
    else:
        st.write("✅ **Grafana dashboard is already set up.**")

    st.write("🚀 **Application initialization complete.**")

def app_main():
    st.title(config.proj_name)

    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    
    if not st.session_state.initialized:
        with st.spinner('Initializing...'):
            st.session_state.es_client = elastic_util.create_client()
            st.session_state.llm_client = llm_util.create_client()
            st.session_state.embedding_model = llm_util.create_embedding_model()

            init()

            st.session_state.initialized = True

            time.sleep(3)
            st.rerun()
    else:
        es_client = st.session_state.es_client
        embedding_model = st.session_state.embedding_model
        llm_client = st.session_state.llm_client

    search_type = st.radio(
        "Select search type:",
        ["knn", "hybrid", "hybrid_rrf"]
    )

    user_input = st.text_input("Enter your question: (e.g., \"What were the circumstances that led to the death of Julia Stoner?\")", key="user_input")
    if st.button("Ask"):
        with st.spinner('Processing...'):
            if search_type == "hybrid":
                search_func = elastic_util.query_hybrid
            elif search_type == "hybrid_rrf":
                search_func = elastic_util.query_hybrid_rrf
            else:
                search_func = elastic_util.query_knn

            question = user_input
            answer_data = llm_util.rag(
                search_func=functools.partial(search_func, es_client, embedding_model),
                llm_func=functools.partial(llm_util.llm, llm_client),
                build_prompt_func=llm_util.build_prompt,
                query=question
            )
            st.write(answer_data["answer"])
            st.write(f"Response time: {answer_data['response_time']:.2f} seconds")
            st.write(f"Total tokens: {answer_data['total_tokens']}")

            st.session_state.conversation_id = str(uuid.uuid4())
            db_util.save_conversation(st.session_state.conversation_id, user_input, search_type, answer_data)
    
    def reset():
        st.session_state.conversation_id = None
        st.session_state.user_input = ""

    if st.session_state.conversation_id:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("+1", on_click=reset):
                db_util.save_feedback(st.session_state.conversation_id, 1)
        with col2:
            if st.button("-1", on_click=reset):
                db_util.save_feedback(st.session_state.conversation_id, -1)

if __name__ == "__main__":
    app_main()
