# llm_zoomcamp_project_2024

## Table of Contents

- [環境需求](#環境需求)
- [主要元件](#主要元件)
- [專案概述](#專案概述)
- [功能介紹](#功能介紹)
  - [RAG](#rag)
  - [手動執行 Script](#手動執行-script)
  - [Retrieval evaluation](#retrieval-evaluation)
  - [Dashboard](#dashboard)
  - [Notebook](#notebook)
- [Todo](#todo)

## 環境需求
- Github codespaces
    - `Python 3.12.1` (可選, 只有在需要手動執行 script 時才需要)
    - `Docker 27.0.3-1`
- Gemini api key (可選, free, for evaluation)

## 主要元件
- Dataset: [The_Adventure_of_the_Speckled_Band.txt](https://en.wikisource.org/wiki/The_Adventures_of_Sherlock_Holmes_(1892,_US)/The_Adventure_of_the_Speckled_Band)
- Knowledge base: `elasticsearch`
- LLM: `ollama phi3`
- Embedding model: `all-mpnet-base-v2`

## 專案概述
此專案為讀入一個短篇偵探小說當作知識庫, 使用 RAG 技術讓使用者可以針對故事的內容發問, 獲得有用的資訊

## 功能介紹

#### RAG
- 啟動 containers
    ```
    docker compose up
    ```
- 連到 streamlit app 網頁 (如 `localhost:8501`)
- 網頁先自動進行以下初始化動作:
    - 如有需要, 建立 elasticsearch index (ingestion)
    - 如有需要, 建立 database table
    - 如有需要, 建立 grafana dashboard
- 初始化完成後, 進入詢問的介面
    - 使用者選擇 elasticsearch 搜尋的類型 (`Select search type:`)
    - 輸入想問的問題 (`Enter your question:`)
    - 按下 `Ask`
    - 此時會進行 RAG 查詢, 約莫 30s 左右, 會回應答案
    - 可以選擇 `+1`、`-1` 的 feedback

#### 手動執行 Script
可選, 因為 streamlit app 已自動化處理
- 確定相關 containers 已啟動
    ```
    docker compose up
    ```
- 安裝所需的 python package
    ```
    pip install -r requirements.txt
    ```
- ingestion:
    - 讀入文字檔
    - chunking
    - embedding chunks
    - 建立 elasticsearch index
    ```
    python ingest.py
    ```
- 初始資料庫: 建立 database tables
    - `conversations`: 每次 RAG 查詢的結果與資訊
    - `feedback`: 使用者 feedback 的計數 (代表回應的 score)
    - `keyvalues`: 內部使用, 儲存 grafana api key 的 dictionary
    ```
    python init_db.py
    ```
- 初始 granafa:
    - 產生 grafana api key
    - 設定 datasource
    - 建立 dashboards
    ```
    python init_granafa.py
    ```

#### Retrieval evaluation
評估比較 text (keyword) search、vector (semantic) search
- metric: hit Rate (HR)、mean reciprocal rank (MRR)
    ```
    text: (hit_rate, mrr)=(0.7419753086419754, 0.6061522633744849)
    vector: (hit_rate, mrr)=(0.7617283950617284, 0.6104526748971189)
    ```
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

#### Dashboard
Access Grafana dashboard (`localhost:3000`), default login: admin/admin
- Last 5 Conversations (Table Panel): Lists the last five conversations with timestamps, questions, and answers, sorted by time.
- Feedback Summary (+1/-1 Pie Chart): Pie chart of user feedback, showing counts of positive and negative responses.
- Tokens (Time Series Panel): Line chart tracking total token usage over time.
- Search Type Distribution (Bar Chart Panel): Horizontal bar chart showing the frequency of different search types in conversations.
- Response Time (Time Series Panel): Time series of response times, helping to monitor performance.

#### Notebook
可在 colab 執行
- ground_truth_data.ipynb
    - 透過 gemini api 為每個 document 建立 5 個相關的問題
    - 產出 `ground-truth-data.csv`

## Todo
- [x] Problem description (2 points)
- [x] RAG flow (2 points)
    - knowledge base: elasticsearch
    - LLM: ollama phi3
- [x] Retrieval evaluation (2 points)
    - text/vector search
    - metrics: hit_rate, mrr
- [ ] RAG evaluation
    - 0 points: No evaluation of RAG is provided
    - 1 point: Only one RAG approach (e.g., one prompt) is evaluated
    - 2 points: Multiple RAG approaches are evaluated, and the best one is used
- [x] Interface (2 points)
    - UI: Streamlit
- [x] Ingestion pipeline (2 points)
    - python script: ingest.py
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
