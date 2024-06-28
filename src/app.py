"""
Functions for Streamlit applications
"""

import os
import yaml
from typing import Generator

import google.generativeai as genai
import streamlit as st
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# heavily inspired from https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps


# https://docs.llamaindex.ai/en/stable/module_guides/models/embeddings/
def init_vector_store() -> VectorIndexRetriever:
    """
    Initialize the vector store index
    """
    # create a class to generate this and save to the image
    # load book(s)
    # build vector index
    # save to disk
    # Alice's Adventures in Wonderland

    # url = "https://www.gutenberg.org/files/11/11-0.txt"
    # response = requests.get(url)
    # response.encoding = 'utf-8'
    # return response.text

    # from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    # from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    # from llama_index.core import Settings
    # Settings.chunk_size = 512
    # Settings.chunk_overlap = 50
    # Settings.embed_model = HuggingFaceEmbedding(
    #     model_name="BAAI/bge-small-en-v1.5",
    # )
    # documents = SimpleDirectoryReader("data").load_data()
    # index = VectorStoreIndex.from_documents(documents)
    # index.storage_context.persist(persist_dir="store")

    # https://model.baai.ac.cn/model-detail/100112
    # Represent this sentence for searching relevant passages:
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5", cache_folder="bge-small-en-v1.5/"
    )

    documents = StorageContext.from_defaults(
        persist_dir=os.path.join(os.path.dirname(__file__), "store")
    )
    index = load_index_from_storage(documents)
    return index.as_retriever(similarity_top_k=4)


def make_rag_prompt(query: str, relevant_passages: list[str]) -> str:
    """Generate the RAG prompt

    Args:
        query (str): user query
        relevant_passages (list[str]): list of relevant passages obtained from the index

    Returns:
        str: the prompt to pass to the LLM API
    """
    escaped_passages = " ".join(
        passage.replace("'", "").replace('"', "").replace("\n", " ")
        for passage in relevant_passages
    )

    prompt = (
        "You are a helpful and informative bot that answers questions using text from "
        "the reference passages included below. Be sure to respond in a complete sentence, "
        "being comprehensive, including all relevant background information. However, you "
        "are talking to a non-technical audience, so be sure to break down complicated "
        "concepts and strike a friendly and conversational tone. If the passages are "
        "irrelevant to the answer, you may ignore them.\n"
        f"QUESTION: '{query}'\n"
        f"PASSAGES: '{escaped_passages}'\n\n"
        "ANSWER:\n"
    )

    return prompt


def call_llm(prompt: str) -> Generator[str, None, None]:
    """LLM wrapper

    Args:
        prompt (str): _description_

    Yields:
        _type_: _description_
    """
    response = st.session_state["llm"].generate_content(prompt, stream=True)
    for chunk in response:
        yield chunk.text


# since the image will be public
# better pass this as a environment variable to the image
# docker run -e TOKEN=ASDASD -p 8501:8501 streamlit
# GEMINI_API_TOKEN = "AIzaSyA3zVz7txsa4jttqMCAKlKrtPQwXcGb6J8"
st.session_state["prompt_deactivated"] = False
if not (GEMINI_API_TOKEN := os.getenv("GEMINI_API_TOKEN")):
    st.error(
        "GEMINI_API_TOKEN environment variable must be provided when running the container.",
        icon="🚨",
    )
    st.session_state["prompt_deactivated"] = True

genai.configure(api_key=GEMINI_API_TOKEN)


hide_decoration_bar_style = """
    <style>
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

st.title("Alice RAG")

DEFAULT_MODEL = "Gemini 1.5 Flash"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "list_of_models" not in st.session_state:
    with open(os.path.join(os.path.dirname(__file__), "config.yaml"), "r") as file:
        st.session_state["list_of_models"] = yaml.safe_load(file)
if "model" not in st.session_state:
    st.session_state["model"] = DEFAULT_MODEL
if "store" not in st.session_state:
    st.session_state["vector_store"] = init_vector_store()

with st.chat_message("assistant"):
    st.markdown(
        "Hello there! I recently read *Alice's Adventures in Wonderland*, what a great book! "
        "I can answer any questions you might have about it. "
        "Please enter your question in the prompt area below."
    )
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(
    "Prompt",
    disabled=st.session_state["prompt_deactivated"],
):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        stream = call_llm(prompt)
        response = st.write_stream(stream)

    st.session_state["messages"].append({"role": "assistant", "content": response})

with st.sidebar:
    models = [k for k in st.session_state["list_of_models"]]
    st.session_state["model"] = st.radio(
        "Available LLMs:",
        models,
        index=models.index(DEFAULT_MODEL),
        captions=[
            m["description"] for m in st.session_state["list_of_models"].values()
        ],
    )

    name = st.session_state["list_of_models"][st.session_state["model"]]["model_name"]
    st.session_state["llm"] = genai.GenerativeModel(model_name=name)

    if st.button("Clear Chat"):
        st.session_state["messages"] = []
        st.rerun()
