"""
Functions for Streamlit applications
"""

import os
import yaml
from typing import Generator

import google.generativeai as genai
import streamlit as st

from store import VectorStore


def make_rag_prompt(query: str, passages: list[str]) -> str:
    """Generate the RAG prompt

    Args:
        query (str): user query
        relevant_passages (list[str]): list of relevant passages obtained from the index

    Returns:
        str: the prompt to pass to the LLM API
    """

    escaped_passages = "\n\n".join(
        passage.replace("\r", " ").replace("\n", " ") for passage in passages
    )

    prompt = (
        "You are a helpful and informative bot that answers questions using text from "
        "the reference passages included below. Be sure to respond in a complete sentence, "
        "being comprehensive, including all relevant background information. However, you "
        "are talking to a non-technical audience, so be sure to break down complicated "
        "concepts and strike a friendly and conversational tone. If the passages are "
        "irrelevant to the answer, you may ignore them.\n\n"
        f"QUESTION: {query}\n\n"
        f"PASSAGES: {escaped_passages}\n\n"
        "ANSWER:\n"
    )

    return prompt


def call_llm(user_query: str) -> Generator[str, None, None]:
    """LLM wrapper

    Args:
        prompt (str): _description_

    Yields:
        Generator[str]: LLM response stream
    """
    passages = st.session_state["vs"].query(user_query)

    prompt = make_rag_prompt(user_query, passages)

    print(prompt)

    response = st.session_state["llm"].generate_content(prompt, stream=True)
    for chunk in response:
        yield chunk.text


# UI is heavily inspired from
# https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
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
if "vs" not in st.session_state:
    vs = VectorStore()
    vs.load_store()
    st.session_state["vs"] = vs

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
