"""
Functions for Streamlit applications
"""

import os
import torch
import yaml
from typing import Generator

import google.generativeai as genai
import streamlit as st

from store import VectorStore

# https://github.com/VikParuchuri/marker/issues/442#issuecomment-2636393925
torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]


def make_rag_prompt(user_query: str, passages: list[str]) -> str:
    """Generate the RAG prompt

    Parameters
    ----------
    user_query : str
        The user query.
    passages : list[str]
        List of relevant passages obtained from the index.

    Returns
    -------
    prompt : str
        The prompt to pass to the LLM API
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
        f"QUESTION: {user_query}\n\n"
        f"PASSAGES: {escaped_passages}\n\n"
        "ANSWER:\n"
    )

    return prompt


def call_llm(user_query: str) -> Generator[str, None, None]:
    """From the user query this retrieves the context, setup the prompt,
    and call the LLM API to generate the response.

    Parameters
    ----------
    user_query : str
        The user query.

    Returns
    -------
    llm response : Generator[str]
        Yields a string generator containing the live LLM response.
    """
    passages = st.session_state["vs"].query(user_query)
    prompt = make_rag_prompt(user_query, passages)

    # RAG config
    config = genai.GenerationConfig(
        temperature=0.3,  # [0, 1] lower values are more deterministic
        top_p=0.9,
        top_k=20,  # decrease from 40 to 20 to make model more focused on high probability token
    )

    response = st.session_state["llm"].generate_content(
        prompt, generation_config=config, stream=True
    )
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

genai.configure(api_key=GEMINI_API_TOKEN, transport="rest")


hide_decoration_bar_style = """
    <style>
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

st.title("Alice RAG")

# setup the session state
DEFAULT_MODEL = "Gemini 1.5 Flash"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "list_of_models" not in st.session_state:
    with open(os.path.join(os.path.dirname(__file__), "config.yaml"), "r") as file:
        st.session_state["list_of_models"] = yaml.safe_load(file)
if "model" not in st.session_state:
    st.session_state["model"] = DEFAULT_MODEL
if "vs" not in st.session_state:
    st.session_state["vs"] = VectorStore()
    st.session_state["vs"].load()

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

    # Initialize the selected model
    name = st.session_state["list_of_models"][st.session_state["model"]]["model_name"]
    st.session_state["llm"] = genai.GenerativeModel(model_name=name)

    if st.button("Clear Chat"):
        st.session_state["messages"] = []
        st.rerun()
