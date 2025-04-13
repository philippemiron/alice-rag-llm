.. _description:

Description
===========

This page gives a global overview of the application, its components, and the underlying technologies used to build Alice RAG. The following sections provide a detailed description of the system's architecture, user interaction, and the AI model employed.

User Interaction
----------------

Built using `Streamlit <https://streamlit.io/>`_, the interface is designed to be user-friendly, intuitive, and efficient for interacting with the Retrieval-Augmented Generation system. The key components are:

- Chat Window: The primary area where the conversation takes place. This window displays user inputs and the corresponding responses from Gemini in a chat-like format. AI responses are streamed in real-time to enhance user feedback and interaction. A small icon next to the messages makes it easy to distinguish user queries and AI responses.

- Sidebar: Includes the available model that can be used to query the document. The user can select the desired model from the radio button to optimize the performance of the system.

- Input Field: A text box where users can type their questions, commonly referred as prompts.

- Send Button: A button to submit the text entered in the input field. This can be clicked or activated by pressing Enter on the keyboard.

Document Retrieval (vector database)
------------------------------------

We utilize `LlamaIndex <https://www.llamaindex.ai/>`_ for ingesting the documents, and creating the vector store. The embedding model used is `BAAI/bge-small-en-v1.5 <https://huggingface.co/BAAI/bge-small-en-v1.5>`_. To keep the repository lightweight, the datasets and embeddings are fetched during the Docker image build process. These steps can be performed using the following command:

>>> uv run python src/store.py

This command downloads the document from the `Gutenberg Project <https://www.gutenberg.org/>_` and stores it in `src/documents/`. It also creates and stores the embeddings in `src/store/`.

The `store.py` module contains two classes: `Book <https://philippemiron.github.io/alice-rag-llm/_autosummary/store.html#store.Book>`_ and `VectorStore <https://philippemiron.github.io/alice-rag-llm/_autosummary/store.html#store.VectorStore>`_ to load the document and interact with the vector database. The `Book` class is used to represent the document data. The `VectorStore` class is used to create the vector store, save or load the embeddings, and retrieve the most relevant passages for a given query.

When a user provides a query, it is first appended as such:

.. code-block:: python

    f"Represent this sentence for searching relevant passages: {query}"

before retrieving top passages from the vector database, as recommended in `BAAI's documentation <https://model.baai.ac.cn/model-detail/100112#usage>`_.

*Note*: The selected model was chosen for speed and based on a RAG tutorial in the `LlamaIndex documentation <https://docs.llamaindex.ai/en/stable/examples/low_level/oss_ingestion_retrieval/>`_. In a real-world scenario, it would be beneficial to benchmark various models to optimize the user experience.

Prompt Generation
-----------------

Top passages returned from querying the vector database are combined with the user's query to generate a prompt for the selected Gemini model.

The prompt was designed following guidelines in the `Gemini documentation <https://model.baai.ac.cn/model-detail/100112#usage>`_ and the following insightful article on understanding RAG architecture (`Building a RAG system from scratch with Gemini API <https://medium.com/@saurabhgssingh/understanding-rag-building-a-rag-system-from-scratch-with-gemini-api-b11ad9fc1bf7>`_).

Specifically, the top relevant passages and the user query are concatenated in the following format:

.. code-block:: python

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

Large Language Model
--------------------

When using Alice RAG, the user can choose from three Gemini's model. Gemini models were selected because Google offer limited free tier API. The models available are:

- Gemini 1.0 Pro
- Gemini 1.5 Pro
- Gemini 1.5 Flash

The first model, from the previous generation, is slightly faster but provides simpler and less accurate answers compared to the newer models. The two latest models (1.5 Pro and Flash) offer higher accuracy but are generally more expensive and slightly slower.  The default model is set to `Gemini 1.5 Flash`, which provides fast and versatile performance across diverse variety of tasks. The user can change the model on the left sidebar of the interface to optimize their experience.
