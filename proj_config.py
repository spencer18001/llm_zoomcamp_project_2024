import logging

class Config:
    def __init__(self, logging_level, chk_serv_timeout, chk_serv_retries, chk_serv_delay,
        data_file_path, chunk_size, chunk_model_name, embedding_model_name,
        elastic_index_name, elastic_result_num, llm_model_name, dashboard_file_path):
        self.chk_serv_timeout = chk_serv_timeout
        self.chk_serv_retries = chk_serv_retries
        self.chk_serv_delay = chk_serv_delay
        self.data_file_path = data_file_path
        self.chunk_size = chunk_size
        self.chunk_model_name = chunk_model_name
        self.embedding_model_name = embedding_model_name
        self.elastic_index_name = elastic_index_name
        self.elastic_result_num = elastic_result_num
        self.llm_model_name = llm_model_name
        self.dashboard_file_path = dashboard_file_path

config = Config(
    logging_level=logging.DEBUG,
    chk_serv_timeout=2,
    chk_serv_retries=120, # 10 min
    chk_serv_delay=5,
    data_file_path="The_Adventure_of_the_Speckled_Band.txt",
    chunk_size=100,
    chunk_model_name="gpt-4o",
    embedding_model_name="all-mpnet-base-v2",
    elastic_index_name="detective_assistant",
    elastic_result_num=5,
    llm_model_name="phi3",
    dashboard_file_path="dashboard.json"
)
