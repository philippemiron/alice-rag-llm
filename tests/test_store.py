import os
from glob import glob

from src.store import Book
from src.store import load_documents
from src.store import VectorStore


def clean_test_data():
    files = glob("src/documents/*", recursive=True)
    for f in files:
        os.remove(f)

    files = glob("src/store/*", recursive=True)
    for f in files:
        os.remove(f)

    if os.path.exists("src/documents"):
        os.rmdir("src/documents")
    if os.path.exists("src/store"):
        os.rmdir("src/store")


def test_download_default():
    books = []
    books.append(
        Book("Alice in Wonderland", "https://www.gutenberg.org/files/11/11-0.txt")
    )
    load_documents(books)

    assert os.path.exists("src/documents/alice_in_wonderland.txt")

    clean_test_data()


def test_download_rename():
    books = []
    books.append(
        Book(
            "Alice in Wonderland",
            "https://www.gutenberg.org/files/11/11-0.txt",
            "test.txt",
        )
    )
    load_documents(books)

    assert os.path.exists("src/documents/test.txt")
    clean_test_data()


def test_vector_store():
    books = []
    books.append(
        Book("Alice in Wonderland", "https://www.gutenberg.org/files/11/11-0.txt")
    )
    load_documents(books)

    assert os.path.exists("src/documents/alice_in_wonderland.txt")
    vs = VectorStore()
    vs.save()

    assert os.path.exists("src/store")

    del vs
    vs = VectorStore()
    vs.load()
    clean_test_data()


def test_vector_store_query():
    books = []
    books.append(
        Book("Alice in Wonderland", "https://www.gutenberg.org/files/11/11-0.txt")
    )
    load_documents(books)
    vs = VectorStore()
    vs.save()

    assert os.path.exists("src/store")

    passages = vs.query("What is the name of the rabbit encountered by Alice?")
    assert len(passages) == 5
    for p in passages:
        assert isinstance(p, str)

    passages = vs.query(
        "What is the name of the rabbit encountered by Alice?", top_passages=2
    )
    assert len(passages) == 2

    for p in passages:
        assert isinstance(p, str)

    clean_test_data()
