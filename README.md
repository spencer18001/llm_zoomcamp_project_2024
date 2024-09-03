# llm_zoomcamp_project_2024

### 環境需求

- Github codespaces
    - Python 3.12.1
    - Docker 27.0.3-1

### 主要元件

- Dataset: The_Adventure_of_the_Speckled_Band.txt [source](https://en.wikisource.org/wiki/The_Adventures_of_Sherlock_Holmes_(1892,_US)/The_Adventure_of_the_Speckled_Band)
- Knowledge base: elasticsearch
- LLM: ollama phi3
- Embedding model: all-mpnet-base-v2

### 專案概述

此專案為讀入一個短篇偵探小說當作知識庫, 使用 RAG 技術讓使用者可以針對故事的內容發問, 獲得有用的資訊

### 功能介紹

##### RAG

- 啟動 container
```
docker compose up
```
- 連到 streamlit app 網頁 (如 "localhost:8501")
- 網頁先自動進行以下初始化動作:
    - 如有需要, 建立 Elasticsearch index (ingestion)
    - 如有需要, 建立 Database table
    - 如有需要, 建立 Grafana dashboard
- 初始化完成後, 進入詢問的介面
    - 使用者選擇搜尋的類型 (`Select search type:`)
    - 輸入想問的問題 (`Enter your question:`)
    - 按下 `Ask`
    - 此時會進行 RAG 查詢
    - 約莫 30s 左右, 會回應答案
    - 此時可以選擇 `+1`、`-1` 的 feedback

##### 手動執行 Script (可選, 因為 streamlit app 已自動化處理)
- 需先安裝所需的 python package
```
pip install -r requirements.txt
```
- 確定 container 已啟動
```
docker compose up
```
- ingestion:
    - 讀入文字檔
    - chunking
    - embedding
    - 建立 elasticsearch index
    ```
    python ingest.py
    ```
- 初始資料庫: 建立 Database tables
    - conversations: 每次 RAG 查詢的結果與資訊
    - feedback: 使用者 feedback 的計數
    - keyvalues: 內部使用存 grafana api key 的 dictionary
    ```
    python init_db.py
    ```
- 初始 granafa:
    - 產生 grafana api key
    - 設定 datasource
    - 建立 dashboard
    ```
    python init_granafa.py
    ```

- Retrieval evaluation
    - 啟動 elasticsearch container
    ```
    docker compose up elasticsearch
    ```
    - 安裝所需的 python package
    ```
    pip install -r requirements.txt
    ```
    - 執行 script
    ```
    python eval_retrieval.py
    ```
- Dashboard
    - 連到 grafana dashboard 網頁 (預設帳密 admin/admin)
    - Last 5 Conversations (Table Panel):
        - Displays the last five recorded conversations, including the timestamp, question, and answer. The data is sorted in descending order by timestamp, providing a quick view of recent interactions.
    - Feedback Summary (+1/-1 Pie Chart):
        - Description: Shows a pie chart summarizing user feedback with counts of positive (+1) and negative (-1) responses. This visual representation helps quickly assess the overall sentiment.
    - Tokens (Time Series Panel):
        - Plots the total number of tokens used over time in a line chart. This panel helps monitor and analyze token consumption trends during conversations.
    - Search Type Distribution (Bar Chart Panel):
        - Displays a horizontal bar chart showing the distribution of different search types within the conversations. The chart groups and counts occurrences by search type.
    - Response Time (Time Series Panel):
        - Illustrates response times for conversations over a specific period. The time series chart provides insights into performance and helps identify potential delays.

### TODO

- [x] Problem description (2 points)
- [x] RAG flow (2 points)
    - knowledge base: elasticsearch
    - LLM: ollama phi3
- [x] Retrieval evaluation
    - hit_rate, mrr (2 points)
- [ ] RAG evaluation
    - 0 points: No evaluation of RAG is provided
    - 1 point: Only one RAG approach (e.g., one prompt) is evaluated
    - 2 points: Multiple RAG approaches are evaluated, and the best one is used
- [x] Interface (2 points)
    - UI: Streamlit
- [x] Ingestion pipeline (2 points)
    - ingest.py
- [x] Monitoring (2 points)
    - user feedback
    - 5 panels of the dashboard
- [x] Containerization (2 points)
    - elasticsearch、ollama、postgres、grafana、streamlit
- [x] Reproducibility (2 points)
- Best practices
    - [x] Hybrid search: search_type `hybrid` (1 point)
    - [x] Document re-ranking: search_type `hybrid_rrf` (1 point)
    - [ ] User query rewriting (1 point)
- [ ] Bonus points (not covered in the course)
    - Deployment to the cloud (2 points)

- 18/23 points