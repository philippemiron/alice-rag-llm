.. _description:

Description
===========

This page gives a global overview of the application, its components, and the underlying technologies used to build it. The following sections provide a detailed description of the system's architecture, user interaction, and the AI models employed.

User Interaction
----------------

Built using `Streamlit <https://streamlit.io/>`_, the interface is designed to be user-friendly, intuitive, and efficient for interacting with the Retrieval-Augmented Generation system. The key components are:

- Chat Window: The primary area where the conversation takes place. This window displays user inputs and the corresponding responses from Gemini in a chat-like format. AI responses are streamed in real-time to enhance user feedback and interaction. A small icon next to the messages makes it easy to distinguish user queries and AI responses.

- Sidebar: Includes the available model that can be used to query the document. The user can select the desired model from the radio button to optimize the performance of the system.

- Input Field: A text box where users can type their questions, commonly referred as prompts.

- Send Button: A button to submit the text entered in the input field. This can be clicked or activated by pressing the Enter key on the keyboard.

Document Retrieval (VectorStore)
--------------------------------

We utilize `LlamaIndex <https://www.llamaindex.ai/>`_ for ingesting the documents, and creating easily creating the vector store. The embedding model used is `BAAI/bge-small-en-v1.5 <https://huggingface.co/BAAI/bge-small-en-v1.5>`_.

When a user provides a `{query}`, it is appended to the following prefix: `Represent this sentence for searching relevant passages: {query}`, as recommended in `BAAI's documentation <https://model.baai.ac.cn/model-detail/100112#usage>`_.

Note: For this proof of concept, I did not explore many different embedding models. The selected model was chosen based on a recommendation from a RAG tutorial in the `LlamaIndex documentation <https://docs.llamaindex.ai/en/stable/examples/low_level/oss_ingestion_retrieval/>`_. In a real-world scenario, it would be beneficial to benchmark various models to optimize the user experience.

Prompt Generation
-----------------

We combine results from vector store retrieval with the user's query to generate a prompt for the selected Gemini model.

The prompt was designed based on guidelines provided in the `Gemini documentation <https://model.baai.ac.cn/model-detail/100112#usage>`_ and this insightful article on understanding `RAG <https://medium.com/@saurabhgssingh/understanding-rag-building-a-rag-system-from-scratch-with-gemini-api-b11ad9fc1bf7>`_ architecture.

Specifically, the top relevant passages and the user query are concatenated in the following format:

.. code-block:: python

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

Large Language Model
--------------------

Choices of three models from the Gemini's family are available. The choice of model was simply made because Google offer limited free tier API! The current available models are:

- Gemini 1.0 Pro
- Gemini 1.5 Pro
- Gemini 1.5 Flash

The first model is from the previous generation, it is slightly faster but returns simpler and less accurate answer as the newer models. The two latest models are more accurate, in practice would be more expensive, and are slightly slower. The default model is set to `Gemini 1.5 Flash`, which provides fast and versatile performance across diverse variety of tasks. The user can change the model on the left sidebar of the interface to optimize their experience.
