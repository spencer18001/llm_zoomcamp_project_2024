# llm_zoomcamp_project_2024

## Table of Contents

- [Project Overview](#project-overview)
- [Requirements](#requirements)
- [Components](#components)
- [Features](#features)
  - [RAG](#rag)
  - [Manual Script Execution](#manual-script-execution)
  - [Retrieval Evaluation](#retrieval-evaluation)
  - [Dashboard](#dashboard)
  - [Notebook](#notebook)
- [Todo](#todo)

## Project Overview
This project uses a short detective story as a knowledge base, allowing users to ask questions and get answers using RAG (Retrieval-Augmented Generation) techniques.

## Requirements
- GitHub Codespaces: Machine type > `4-core 16GB RAM`
  - `Python 3.12.1` (optional, only needed for manual script execution)
  - `Docker 27.0.3-1`
- Gemini API key (optional, free, for evaluation)

## Components
- Dataset: [The_Adventure_of_the_Speckled_Band.txt](https://en.wikisource.org/wiki/The_Adventures_of_Sherlock_Holmes_(1892,_US)/The_Adventure_of_the_Speckled_Band)
- Knowledge base: `Elasticsearch`
- LLM: `ollama phi3`
- Embedding model: `all-mpnet-base-v2`

## Features

#### RAG
- Start containers:
  ```
  docker compose up
  ```
- Access the Streamlit app (`localhost:8501`).
- The app automatically:
  - Creates Elasticsearch index (if needed)
  - Creates database tables (if needed)
  - Sets up Grafana dashboard (if needed)
- Once initialized, you can:
  - Select search type (`Select search type:`)
  - Ask your question (`Enter your question:`)
  - Click `Ask` to perform the RAG query (~30s for response)
  - Provide feedback with `+1` or `-1`

#### Manual Script Execution
Optional, since the Streamlit app automates these tasks.
- Ensure containers are running:
  ```
  docker compose up
  ```
- Install Python packages:
  ```
  pip install -r requirements.txt
  ```
- Ingest data:
  - Load text file
  - Chunk text
  - Embed chunks
  - Create Elasticsearch index
  ```
  python ingest.py
  ```
- Initialize database: create database tables
  - `conversations`: RAG query results and metadata
  - `feedback`: User feedback scores
  - `keyvalues`: Internal storage for Grafana API key
  ```
  python init_db.py
  ```
- Set up Grafana:
  - Generate API key
  - Configure datasource
  - Create dashboards
  ```
  python init_granafa.py
  ```

#### Retrieval Evaluation
Evaluate and compare text (keyword) search vs. vector (semantic) search.
- Metrics: Hit Rate (HR), Mean Reciprocal Rank (MRR)
  ```
  text: (HR, MRR) = (0.742, 0.606)
  vector: (HR, MRR) = (0.762, 0.610)
  ```
- Start Elasticsearch container:
  ```
  docker compose up elasticsearch
  ```
- Install Python packages:
  ```
  pip install -r requirements.txt
  ```
- Run evaluation script:
  ```
  python eval_retrieval.py
  ```

#### Dashboard
Access Grafana dashboard (`localhost:3000`), default login: admin/admin.
- **Last 5 Conversations (Table Panel):** Lists the last five conversations with timestamps, questions, and answers.
- **Feedback Summary (+1/-1 Pie Chart):** Displays user feedback with counts of positive and negative responses.
- **Tokens (Time Series Panel):** Tracks total token usage over time.
- **Search Type Distribution (Bar Chart Panel):** Shows the frequency of different search types.
- **Response Time (Time Series Panel):** Monitors response times to assess performance.

#### Notebook
Executable in Colab.
- **ground_truth_data.ipynb:**
  - Use Gemini API to generate five related questions for each document.
  - Outputs `ground-truth-data.csv`.

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
