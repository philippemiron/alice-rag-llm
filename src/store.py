"""
Module containing VectorStore utility
"""

import os
import requests

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader


class Book:
    title: str
    url: str
    encoding: str | None = "utf-8"
    filename: str | None = None

    def __init__(
        self, title: str, url: str, filename: str | None = None, encoding: str = "utf-8"
    ):
        self.title = title
        self.url = url
        self.filename = (
            filename if filename else f"{self.title.lower().replace(" ", "_")}.txt"
        )
        self.encoding = encoding


def load_documents(folder: str, books: list[Book]):
    """Load documents from a file

    Returns:
        _type_: _description_
    """

    if not os.path.exists(folder):
        os.makedirs(folder)

    for book in books:
        response = requests.get(book.url)
        response.encoding = book.encoding
        text = response.text
        open(os.path.join(folder, book.filename), "w").write(text)


class VectorStore:
    def __init__(
        self,
        documents_path: str = "documents",
        store_path: str = "store",
        top_passages: int = 5,
    ):
        self.documents_path = documents_path
        self.store_path = store_path
        self.top_passages = top_passages
        self.indexer = None

        # embedding settings
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 50
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
        )

    def load_store(self):
        """
        Load the vector store from the specified path.
        """
        documents = StorageContext.from_defaults(
            persist_dir=os.path.join(os.path.dirname(__file__), self.store_path)
        )

        index = load_index_from_storage(documents)
        self.indexer = index.as_retriever(similarity_top_k=self.top_passages)

    def save_store(self):
        """
        Save the vector store to the specified path.
        """
        dataset = SimpleDirectoryReader(self.documents_path).load_data()
        index = VectorStoreIndex.from_documents(dataset)

        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path)
        index.storage_context.persist(persist_dir=self.store_path)

    def query(self, query: str) -> list[str]:
        """
        Query the vector store with the specified query.
        """

        passages = self.indexer.retrieve(
            f"Represent this sentence for searching relevant passages: {query}"
        )

        # return list of passages with their scores
        return [p.node.text for p in passages]


if __name__ == "__main__":
    # when building the image, we can load the books,
    # create the embeddings, and save it locally to
    # speed up starting time

    # defined list of books to load
    books = []
    books.append(
        Book("Alice in Wonderland", "https://www.gutenberg.org/files/11/11-0.txt")
    )
    documents_path = os.path.join(os.path.dirname(__file__), "documents")
    load_documents(documents_path, books)

    # create the vector store
    store_path = os.path.join(os.path.dirname(__file__), "store")
    vs = VectorStore(documents_path=documents_path, store_path=store_path)
    vs.save_store()
