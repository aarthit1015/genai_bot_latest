# extras/add_docs.py
from rag import MiniRAG
import os

rag = MiniRAG()
folder = "data/docs"

docs_to_add = []

for fname in os.listdir(folder):
    if fname.endswith((".txt", ".md")):
        path = os.path.join(folder, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            docs_to_add.append((fname, text))
            print(f" Found and added: {fname}")
        else:
            print(f"⚠️ Skipped empty file: {fname}")

if docs_to_add:
    rag.add_documents(docs_to_add)
    print("🎉 All documents added successfully!")
else:
    print("⚠️ No documents found with content.")
