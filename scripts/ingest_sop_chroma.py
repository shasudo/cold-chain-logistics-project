"""Load data/policy/*.md into the local ChromaDB via LangChain. Safe to re-run (upserts by id)."""

import sys
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config  # noqa: E402
from src.rag import get_vectorstore  # noqa: E402


def main() -> None:
    files = sorted(config.SOP_DIR.glob("*.md"))
    print(f"Found {len(files)} policy file(s) in {config.SOP_DIR}...")
    if not files:
        return
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60)
    docs = [
        Document(page_content=path.read_text(encoding="utf-8"), metadata={"source_file": path.name})
        for path in files
    ]
    chunks = splitter.split_documents(docs)
    store = get_vectorstore()
    store.add_texts(
        texts=[c.page_content for c in chunks],
        metadatas=[c.metadata for c in chunks],
        ids=[f"{c.metadata['source_file']}-chunk-{i}" for i, c in enumerate(chunks)],
    )
    print(f"Upserted {len(chunks)} chunk(s). Collection now holds {store._collection.count()} chunk(s).")


if __name__ == "__main__":
    main()
