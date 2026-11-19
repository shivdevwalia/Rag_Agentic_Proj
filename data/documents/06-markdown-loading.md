# Loading Markdown Documents

## Discovery
The loader should search data/documents recursively for files ending in .md. Python pathlib provides Path.rglob for this task. Sort discovered paths to make processing order predictable across repeated runs.

## Reading text
Read each file as UTF-8 text. Ignore files containing only whitespace. If a file cannot be decoded or accessed, report its source path so the problem can be fixed rather than silently losing part of the corpus.

## Document representation
A first implementation can return dictionaries containing text and source. The next stage can convert these records into LangChain Document objects. The document text belongs in page_content, while the relative source path belongs in metadata.

## Source paths
Store paths relative to the corpus root, such as 06-markdown-loading.md. Relative paths avoid tying records to a particular developer's Windows username or absolute directory.

## Loader checkpoint
Print the document count, each source path, and its character count. For this sample corpus, the expected count is ten. Loading does not yet imply that any text has been embedded or stored.

