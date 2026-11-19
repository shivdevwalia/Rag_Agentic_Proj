# Upserting Document Chunks

## Desired behavior
An upsert inserts a new row when its identifier is absent and updates the existing row when that identifier is already present. It is the proposed mechanism for making ingestion safe to repeat without accumulating duplicate copies of unchanged chunks.

## Stable identifiers
One possible identifier combines a relative source path with a chunk position. Another design incorporates a content hash. Choose a strategy deliberately: content based identifiers avoid some duplicate writes, but changed content produces new identifiers that still require cleanup.

## Suggested fields
A chunk record should include its identifier, source path, position within the source, text, embedding, and embedding model name. Recording a content hash and ingestion configuration can help identify when a record needs to be regenerated.

## Database writes
Use parameterized SQL through Psycopg rather than building SQL by concatenating document contents. Group related writes in a transaction so that failures do not leave a source document only partly updated.

## Stale chunks
Upserts alone do not remove old rows when a file gets shorter, is deleted, or is split differently. A later reconciliation step must remove obsolete chunks. Test this explicitly before treating repeated ingestion as a complete synchronization process.

