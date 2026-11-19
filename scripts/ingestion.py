from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import re
from rank_bm25 import BM25Okapi
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"

model = SentenceTransformer(
      "BAAI/bge-small-en-v1.5",
      device="cpu",
  )


def load_markdown_files(directory: Path) -> list[dict]:
    if not directory.is_dir():
        raise FileNotFoundError(f"Document folder does not exist: {directory}")

    documents = []

    for path in sorted(directory.rglob("*.md")):
        text = path.read_text(encoding="utf-8")

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

        chunks.extend(document_chunks)

    return chunks

def embed_chunks(chunks):
   
    texts = [chunk.page_content for chunk in chunks]

    embeddings = model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    return embeddings

def dense_search(query, model, embeddings, top_k=5):
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
    scores = index.get_scores(tokenize(query))

    ranked_ids = sorted(
        range(len(scores)),
        key=lambda chunk_id: scores[chunk_id],
        reverse=True,
    )

    return [
        (chunk_id, float(scores[chunk_id]))
        for chunk_id in ranked_ids[:top_k]
    ]

def reciprocal_rank_fusion(*ranked_lists, k=60, top_k=5):
    fused_scores = {}

    for results in ranked_lists:
        for rank, (chunk_id, _) in enumerate(results, start=1):
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


if __name__ == "__main__":
    documents = load_markdown_files(DOCUMENTS_DIR)

    print(f"Loaded {len(documents)} documents")

    for document in documents:
        print(f"{document['source']}: {len(document['text'])} characters")

    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks")

    for chunk in chunks[:3]:
        print("\nSource:", chunk.metadata["source"])
        print("Characters:", len(chunk.page_content))
        print(chunk.page_content)

    embeddings = embed_chunks(chunks)

    print("Embedding shape:", embeddings.shape)
    print("First vector's first 5 values:", embeddings[0][:5])

    assert len(embeddings) == len(chunks)

    query = "How does the database keep its data after stopping Docker?"

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