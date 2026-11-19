import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rank_bm25 import BM25Okapi
from scripts import ingestion as app


class RetrievalTests(unittest.TestCase):
    def test_bm25_omits_unmatched_chunks_even_with_zero_score(self):
        index = BM25Okapi([["docker"], ["python"]])
        self.assertEqual(app.bm25_search("penguin", index), [])
        self.assertEqual([i for i, _ in app.bm25_search("docker", index)], [0])
        self.assertEqual(app.bm25_search("docker", index)[0][1], 0.0)

    def test_blank_query_rejected(self):
        with self.assertRaises(ValueError):
            app.bm25_search("  ", BM25Okapi([["word"]]))

    def test_rrf_empty_list_and_duplicates(self):
        results = app.reciprocal_rank_fusion([(3, 0.9), (3, 0.8)], [])
        self.assertEqual(results, [(3, 1 / 61)])

    def test_loader_exclusion_empty_files_and_stable_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "AGENTS.md").write_text("Excluded", encoding="utf-8")
            (root / "empty.md").write_text("  ", encoding="utf-8")
            (root / "notes.md").write_text("Docker preserves data.", encoding="utf-8")
            documents = app.load_markdown_files(root)
            self.assertEqual(len(documents), 1)
            before = app.chunk_documents(documents)[0].metadata["chunk_id"]
            (root / "aaa.md").write_text("Another file", encoding="utf-8")
            after = app.chunk_documents(app.load_markdown_files(root))
            self.assertEqual(before, after[1].metadata["chunk_id"])

    def test_unreadable_document_reports_path(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "broken.md"
            path.write_bytes(b"\xff")
            with self.assertRaisesRegex(ValueError, "broken.md"):
                app.load_markdown_files(Path(folder))

    def test_empty_corpus_fails_before_model_loading(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch("sys.argv", ["ingestion", "--documents", folder]):
                with patch.object(app, "SentenceTransformer") as model:
                    with self.assertRaisesRegex(ValueError, "No nonempty"):
                        app.main()
                    model.assert_not_called()


if __name__ == "__main__":
    unittest.main()
