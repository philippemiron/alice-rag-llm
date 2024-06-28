.. _usage:

Usage
=====

This section provides a detailed guide on how to use the Alice RAG application. The application is designed to answer questions about *Alice's Adventures in Wonderland* using a combination of retrieval-based and generative AI techniques.

Build the container
-------------------

To build the container for Alice RAG, follow these steps. The Dockerfile in the repository is configured to set up the necessary environment and dependencies for the application.

Note: that this requires a functional `Docker <https://www.docker.com/products/docker-desktop/>`_ installation on your machine.

.. code-block:: shell

  >>> git@github.com:philippemiron/alice-rag-llm.git
  >>> cd alice-rag-llm
  >>> docker build -t alice-rag-llm .

This will create a container image named `alice-rag-llm`, that you should be able to see in your local Docker registry (`docker images`)

Running locally
---------------

To run the container locally and interact with the Alice RAG system, follow these steps:

- Ensure you have a valid Gemini API token. This token is required to interact with the Gemini model and can be obtained on the Gemini API `website <https://ai.google.dev/pricing>`_ (free tier available).
- Use the following command to run the Docker container, which will expose the application on port 8501, set the `GEMINI_API_TOKEN` environment variable, and run the application on the local machine. Note that in a real-world scenario, this token would be stored securely in a secret management system, but since the image is freely available on DockerHub for this POC, it is passed as an environment variable.

.. code-block:: shell

  >>> docker run -p 8501:8501 -e GEMINI_API_TOKEN="TOKEN_STRING" >>> alice-rag-llm

The application will be accessible locally at `http://0.0.0.0:8501 <http://0.0.0.0:8501>`_.

Running from DockerHub
----------------------

The container is also available on DockerHub as `pmiron/alice-rag-llm <https://hub.docker.com/repository/docker/pmiron/alice-rag-llm/general>`_. Similarly, you can pull the image from the repository and run it directly on your local machine.

.. code-block:: shell

  >>> docker run -p 8501:8501 -e GEMINI_API_TOKEN="TOKEN_STRING" pmiron/alice-rag-llm:latest
