from pathlib import Path
import argparse
import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import re
from rank_bm25 import BM25Okapi
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"

MODEL_NAME = "BAAI/bge-small-en-v1.5"


def load_markdown_files(directory: Path) -> list[dict]:
    if not directory.is_dir():
        raise FileNotFoundError(f"Document folder does not exist: {directory}")

    documents = []

    for path in sorted(directory.rglob("*.md")):
        if path.name.lower() == "agents.md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ValueError(f"Cannot read document {path}: {exc}") from exc

        if not text.strip():
            continue

        documents.append({
            "text": text,
            "source": path.relative_to(directory).as_posix(),
        })

    return documents


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        length_function=len,
    )

    chunks = []

    for document in documents:
        document_chunks = splitter.create_documents(
            texts=[document["text"]],
            metadatas=[{"source": document["source"]}],
        )

        for position, chunk in enumerate(document_chunks):
            identity = document["source"] + "\0" + str(position) + "\0" + chunk.page_content
            chunk.metadata["chunk_id"] = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        chunks.extend(document_chunks)

    return chunks

def embed_chunks(chunks, model):
    if not chunks:
        raise ValueError("No nonempty document chunks were found.")
    texts = [chunk.page_content for chunk in chunks]

    tokenized = model.tokenizer(texts, truncation=False)
    for chunk, token_ids in zip(chunks, tokenized["input_ids"]):
        if len(token_ids) > model.max_seq_length:
            raise ValueError(
                f"Chunk from {chunk.metadata['source']} exceeds the model's "
                f"{model.max_seq_length}-token limit; reduce chunk_size."
            )

    embeddings = model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    return embeddings

def dense_search(query, model, embeddings, top_k=5):
    if not query.strip():
        raise ValueError("Query must not be blank.")
    if top_k < 1:
        raise ValueError("top_k must be positive.")
    if len(embeddings) == 0:
        return []
    query_vector = model.encode(
        "Represent this sentence for searching relevant passages: " + query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    scores = embeddings @ query_vector

    ranked_ids = scores.argsort()[::-1][:top_k]

    return [
        (int(chunk_id), float(scores[chunk_id]))
        for chunk_id in ranked_ids
    ]

def tokenize(text):
    return re.findall(r"\w+", text.lower())


def bm25_search(query, index, top_k=5):
    if not query.strip():
        raise ValueError("Query must not be blank.")
    if top_k < 1:
        raise ValueError("top_k must be positive.")
    query_tokens = tokenize(query)
    matching_ids = [
        chunk_id for chunk_id, counts in enumerate(index.doc_freqs)
        if any(token in counts for token in query_tokens)
    ]
    if not matching_ids:
        return []
    scores = index.get_scores(query_tokens)

    ranked_ids = sorted(
        matching_ids,
        key=lambda chunk_id: scores[chunk_id],
        reverse=True,
    )

    return [
        (chunk_id, float(scores[chunk_id]))
        for chunk_id in ranked_ids[:top_k]
    ]

def reciprocal_rank_fusion(*ranked_lists, k=60, top_k=5):
    if k < 0 or top_k < 1:
        raise ValueError("k must be nonnegative and top_k must be positive.")
    fused_scores = {}

    for results in ranked_lists:
        seen = set()
        for rank, (chunk_id, _) in enumerate(results, start=1):
            if chunk_id in seen:
                continue
            seen.add(chunk_id)
            contribution = 1 / (k + rank)

            fused_scores[chunk_id] = (
                fused_scores.get(chunk_id, 0.0) + contribution
            )

    ranked_results = sorted(
        fused_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return ranked_results[:top_k]


def main():
    parser = argparse.ArgumentParser(description="In-memory hybrid retrieval experiment")
    parser.add_argument("--documents", type=Path, default=DOCUMENTS_DIR)
    parser.add_argument("--query", default="How does the database keep its data after stopping Docker?")
    args = parser.parse_args()
    if not args.query.strip():
        parser.error("Query must not be blank.")
    documents = load_markdown_files(args.documents)

    print(f"Loaded {len(documents)} documents")

    for document in documents:
        print(f"{document['source']}: {len(document['text'])} characters")

    chunks = chunk_documents(documents)
    if not chunks:
        raise ValueError("No nonempty document chunks were found.")
    tokenized_chunks = [tokenize(chunk.page_content) for chunk in chunks]
    if not any(tokenized_chunks):
        raise ValueError("Corpus has no words for BM25 indexing.")
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    print(f"Created {len(chunks)} chunks")

    for chunk in chunks[:3]:
        print("\nSource:", chunk.metadata["source"])
        print("Characters:", len(chunk.page_content))
        print(chunk.page_content)

    embeddings = embed_chunks(chunks, model)

    print("Embedding shape:", embeddings.shape)
    print("First vector's first 5 values:", embeddings[0][:5])

    if embeddings.ndim != 2 or len(embeddings) != len(chunks):
        raise ValueError("Embeddings must have one vector per chunk.")

    query = args.query

    # Prepare BM25 using the same chunks as dense search.
    tokenized_chunks = [
        tokenize(chunk.page_content)
        for chunk in chunks
    ]

    bm25_index = BM25Okapi(tokenized_chunks)

    # Retrieve 10 candidates from each method.
    dense_results = dense_search(
        query, model, embeddings, top_k=10
    )

    bm25_results = bm25_search(
        query, bm25_index, top_k=10
    )

    # Combine their rankings and keep the best 5.
    hybrid_results = reciprocal_rank_fusion(
        dense_results,
        bm25_results,
        top_k=5,
    )

    # Show rankings so we can compare them.
    print("\nDense chunk IDs:", [i for i, _ in dense_results])
    print("BM25 chunk IDs:", [i for i, _ in bm25_results])

    print("\n--- Hybrid results ---")

    for rank, (chunk_id, score) in enumerate(
        hybrid_results, start=1
    ):
        chunk = chunks[chunk_id]

        print(
            f"\nRank {rank} | Chunk {chunk_id} "
            f"| RRF score: {score:.6f}"
        )
        print("Source:", chunk.metadata["source"])
        print(chunk.page_content)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc)) from exc
