# Project Folder Layout

## Corpus
The data/documents directory holds the Markdown corpus. These ten numbered documents are learning material for the ingestion exercise. They describe both existing setup and proposed behavior; proposed features must be implemented before they can be relied upon.

## Scripts
The scripts directory is reserved for Python entry points. The learner will create scripts/ingest.py to load, split, embed, and store documents. Keeping corpus files separate from scripts makes it easier to reason about what is input and what is executable code.

## Environment and configuration
The .venv directory contains the Python virtual environment. requirements.txt lists direct dependencies, while requirements.lock.txt records installed package versions. compose.yaml defines the database service.

## Local secrets
The .env file contains local database configuration and is excluded from Git. The .env.example file documents configuration names without carrying the generated password. Credentials should not be added to this document corpus because retrieved text may later be sent to a language model.

