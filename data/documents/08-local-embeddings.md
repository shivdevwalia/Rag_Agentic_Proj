# Local Embeddings

## Intended model
The planned embedding model is BAAI/bge-small-en-v1.5, loaded through sentence-transformers. It is intended for English text. Loading the model for the first time requires downloading model files; later runs can reuse the local cache.

## Meaning of an embedding
An embedding represents a text passage as a sequence of numbers. Similarity search compares these sequences to find passages that may be relevant to a question. Similar vectors are useful retrieval signals, but they are not proof that a passage supports an answer.

## Consistency
Use the same model and compatible preprocessing for corpus chunks and search queries. Changing the embedding model requires rebuilding stored document embeddings. Equal vector dimensions alone do not make embeddings from different models interchangeable.

## Batch processing
Load the model once per ingestion process and encode multiple chunks in batches. Start with a small batch on a CPU and adjust based on memory and runtime. Do not instantiate the model separately for every chunk.

## Validation
Inspect the returned embedding matrix shape to determine the required database vector dimension. Check that the number of embeddings matches the number of chunks before writing records.

