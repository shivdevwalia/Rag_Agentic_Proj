# Python Environment

## Existing setup
The project uses a .venv virtual environment created with Python 3.11.5. A virtual environment isolates project packages from packages installed for other Python projects.

## Running Python
From the project root in PowerShell, the environment can be activated with .\.venv\Scripts\Activate.ps1. Alternatively, invoke .\.venv\Scripts\python.exe directly. Direct invocation is useful when activation is unavailable or a terminal has another interpreter selected.

## Dependencies
The installed core packages include LangChain, LangGraph, FastAPI, Uvicorn, pgvector, Psycopg, sentence-transformers, and Ragas. They serve different stages of the application. Not every package needs to be imported by the ingestion script.

## Verification
The command python -m pip check checks declared dependency compatibility for the active interpreter. An import check confirms that installed modules can load. Neither check proves that document ingestion or retrieval produces useful results; those behaviors need their own validation.

