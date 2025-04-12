"""
Module containing VectorStore utility
"""

import os
import requests

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader


class Book:
    """Simple class to represent a book"""

    title: str
    url: str
    encoding: str | None = "utf-8"
    filename: str | None = None

    def __init__(
        self, title: str, url: str, filename: str | None = None, encoding: str = "utf-8"
    ):
        """Initialize a new book

        Parameters
        ----------
        title : str
            Title of the book
        url : str
            The path or url to download the book
        filename : str, optional
            The local filename where to store the book. Default generates the
            filename from the title.
        encoding : str, optional
            The book's encoding. Default to "utf-8".
        """
        self.title = title
        self.url = url
        self.filename = (
            filename if filename else f"{self.title.lower().replace(' ', '_')}.txt"
        )
        self.encoding = encoding


def load_documents(
    books: list[Book],
    folder: str = os.path.join(os.path.dirname(__file__), "documents"),
):
    """Retrieve the list of books and store them locally.

    Parameters
    ----------
    books : list[Book]
        List of books to download
    folder : str, optional
        The folder where to store the books, by default `src/document`.
    """

    if not os.path.exists(folder):
        os.makedirs(folder)

    for book in books:
        response = requests.get(book.url)
        response.encoding = book.encoding
        text = response.text
        open(os.path.join(folder, book.filename), "w").write(text)


class VectorStore:
    """VectorStore class to handle the embedding database"""

    def __init__(
        self,
        documents_path: str = os.path.join(os.path.dirname(__file__), "documents"),
        store_path: str = os.path.join(os.path.dirname(__file__), "store"),
    ):
        self.documents_path = documents_path
        self.store_path = store_path
        self.index = None

        # embedding settings
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 50
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
        )

    def load(self):
        """
        Reload the vector store from a previous state.
        """
        documents = StorageContext.from_defaults(
            persist_dir=os.path.join(os.path.dirname(__file__), self.store_path)
        )

        self.index = load_index_from_storage(documents)

    def save(self):
        """
        Save the vector store locally.
        """
        dataset = SimpleDirectoryReader(self.documents_path).load_data()
        self.index = VectorStoreIndex.from_documents(dataset)

        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path)
        self.index.storage_context.persist(persist_dir=self.store_path)

    def query(
        self,
        query: str,
        top_passages: int = 5,
    ) -> list[str]:
        """
        Query the vector store with the specified query and returns the top passages.

        Parameters
        ----------
        query : str
            The user provided query.
        top_passages : int, optional
            The number of passages to return, default is 5.
        """

        passages = self.index.as_retriever(similarity_top_k=top_passages).retrieve(
            f"Represent this sentence for searching relevant passages: {query}"
        )

        # return list of similar passages
        return [p.node.text for p in passages]


if __name__ == "__main__":
    # when building the image, the books are downloaded,
    # the embeddings is created, and everything is saved locally to
    # speed up starting time

    # defined list of books to load
    books = []
    books.append(
        Book("Alice in Wonderland", "https://www.gutenberg.org/files/11/11-0.txt")
    )
    load_documents(books)

    # create the vector store
    vs = VectorStore()
    vs.save()
