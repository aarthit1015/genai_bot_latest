# GenAI Telegram Bot (Mini-RAG + Vision)

## Requirements
- Python 3.10+
- Set environment variable: TELEGRAM_TOKEN=<your token>
- Install packages: pip install -r requirements.txt

## Prepare docs (example)
Add 3-5 markdown files to `data/docs/` (or call a small script to add docs into DB).
You can also call `python -c "from rag import MiniRAG; rag=MiniRAG(); rag.add_documents([('Title','text...')])"`

## Run
python telegram_bot.py

## Models used
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- Generator: google/flan-t5-base
- Image captioning: Salesforce/blip-image-captioning-base

## Notes
- CPU can be slow. For faster retrieval, install `faiss-cpu`.
- To use OpenAI instead of Flan-T5, modify `rag.py` to call OpenAI API (set OPENAI_API_KEY).
