# Agentic RAG Project Overview

## Purpose
This project is a learning application that answers questions using a local collection of Markdown documents. Its first milestone is a reliable ingestion pipeline. Question answering and agent behavior are later milestones, rather than features already implemented.

## Ingestion flow
The pipeline reads document text, divides it into overlapping chunks, creates an embedding for each chunk, and stores the results in PostgreSQL. The pgvector extension allows the database to compare vectors.

## Retrieval flow
A future retrieval pipeline will embed a user's question using the same embedding model used during ingestion. It will search for similar document chunks and provide their text to a language model as context.

## Success criteria
A successful first ingestion run stores nonempty chunks with source metadata and embeddings. Repeating ingestion should not create duplicate rows. A useful retrieval result should identify the original source document so that a person can check the answer.

