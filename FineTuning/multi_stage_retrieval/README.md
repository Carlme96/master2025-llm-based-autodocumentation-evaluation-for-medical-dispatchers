# RAG with nomic-embed-text-v1.5

Use [nomic-embed-text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) for dense vector embeddings in a Retrieval-Augmented Generation (RAG) pipeline.

| Component | Model                      | Role            |
|-----------|----------------------------|-----------------|
| Encoder   | nomic-embed-text-v1.5      | Document & Query Encoder |
| LLM | e.g. GPT4.o-mini, GPT4.1     | Extract |
| Vector DB | FAISS              | Similarity Search (Nearest Neighbour) |
