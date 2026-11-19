# Chunking Strategy

## Why split documents
Retrieval operates on passages, not necessarily entire files. A chunk should contain enough context to explain an idea while remaining focused enough to match a specific question.

## Recursive splitting
The planned splitter is LangChain's RecursiveCharacterTextSplitter. It tries separators in order, favoring larger text boundaries before falling back to smaller ones. This helps preserve paragraphs when they fit within the configured size.

## Initial experiment
Use a target chunk size of 700 characters and an overlap of 100 characters as an initial learning experiment. These are proposed starting values, not measured optimal settings. With the usual character length function, chunk size measures characters rather than model tokens.

## Overlap
Overlap repeats some nearby text across adjacent chunks to preserve continuity. Too much overlap increases storage and may produce repetitive search results. Too little can separate an explanation from its context.

## Inspection
Before embedding, print a few chunks and their metadata. Confirm that each chunk retains its source path. Compare the output with the original Markdown and adjust splitting settings if headings or explanations become difficult to interpret.

