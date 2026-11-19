# Validation and Next Steps

## Ingestion checkpoints
Check each stage independently. Verify the input document count, inspect sample chunks, compare chunk and embedding counts, and query the number of stored rows. A successful program exit is only one piece of evidence.

## Repeated ingestion
Run ingestion twice without editing the files. The stored chunk count should remain stable. Then change a document and verify that retrieval reflects the updated text. When stale chunk cleanup is implemented, also test shortening and deleting a source file.

## Retrieval questions
Try asking where local database credentials are stored, how to start the Compose service, why chunk overlap is useful, and why embeddings must use a consistent model. Relevant source documents should appear near the top of search results.

## Future application
After ingestion and retrieval work, a FastAPI application can expose query endpoints. Uvicorn can serve that application. LangGraph can later coordinate retrieval and other steps when the workflow needs explicit state and branching.

## Evaluation
Ragas is installed for later evaluation experiments. Evaluate retrieval relevance and answer support separately. Model based evaluation may need provider configuration and credentials, so installing Ragas does not by itself provide a working evaluation pipeline.

