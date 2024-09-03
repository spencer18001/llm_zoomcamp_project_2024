# llm_zoomcamp_project_2024

### todo

- [ ] Problem description
    - 0 points: The problem is not described
    - 1 point: The problem is described but briefly or unclearly
    - 2 points: The problem is well-described and it's clear what problem the project solves
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
- [ ] Containerization
    - 0 points: No containerization
    - 1 point: Dockerfile is provided for the main application OR there's a docker-compose for the dependencies only
    - 2 points: Everything is in docker-compose
- [ ] Reproducibility
    - 0 points: No instructions on how to run the code, the data is missing, or it's unclear how to access it
    - 1 point: Some instructions are provided but are incomplete, OR instructions are clear and complete, the code works, but the data is missing
    - 2 points: Instructions are clear, the dataset is accessible, it's easy to run the code, and it works. The versions for all dependencies are specified.
- Best practices
    - [x] Hybrid search: search_type `hybrid` (1 point)
    - [x] Document re-ranking: search_type `hybrid_rrf` (1 point)
    - [ ] User query rewriting (1 point)
- [ ] Bonus points (not covered in the course)
    - Deployment to the cloud (2 points)

- 12/23 points