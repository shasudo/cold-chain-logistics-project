"""Local SOP knowledge base: persistent ChromaDB vector store with on-device embeddings."""

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

import config


class LocalEmbeddings(Embeddings):
    """Chroma's bundled ONNX model, exposed as a LangChain Embeddings (no API key, no torch)."""

    def __init__(self) -> None:
        self._fn = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._fn(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._fn([text])[0]


def get_vectorstore() -> Chroma:
    """Open (or create) the persistent SOP collection."""
    return Chroma(
        collection_name=config.SOP_COLLECTION,
        embedding_function=LocalEmbeddings(),
        persist_directory=str(config.CHROMA_DIR),
    )
