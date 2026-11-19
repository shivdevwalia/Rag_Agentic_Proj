# PostgreSQL and pgvector

## Local database
The Compose configuration defines a PostgreSQL service named postgres using the pgvector/pgvector:pg17 image. The database is bound to the loopback interface so that local clients can connect through 127.0.0.1.

## Connection settings
The default database name is rag, the default user is rag, and the default host port is 5432. The generated password lives in .env. If POSTGRES_PORT is changed, Python clients must use the new port too.

## Extension
The image includes pgvector extension files. The initialization SQL enables the extension with CREATE EXTENSION IF NOT EXISTS vector. PostgreSQL extension names are database specific, so availability in one database does not automatically enable it in another.

## Storage plan
The ingestion table has not yet been created. A proposed chunk record contains a stable identifier, source path, chunk text, metadata, and an embedding. The vector column must match the dimensions produced by the chosen embedding model.

