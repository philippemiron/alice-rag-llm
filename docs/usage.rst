.. _usage:

Usage
=====

This section provides a detailed guide on how to use the Alice RAG application. The application is designed to answer questions about *Alice's Adventures in Wonderland* using a combination of retrieval-based and generative AI techniques.

Build the container
-------------------

Follow these steps below to build the container for Alice RAG. The Dockerfile in the repository is configured to set up all the necessary environment and dependencies for the application.

Note: a functional `Docker <https://www.docker.com/products/docker-desktop/>`_ installation is required on your machine.

>>> git clone git@github.com:philippemiron/alice-rag-llm.git
>>> cd alice-rag-llm/
>>> docker build -t alice-rag-llm .

This will create a container image named `alice-rag-llm` that will appear in your local Docker registry (with `docker images`).

Running locally
---------------

Follow these steps to run the container locally and interact with the Alice RAG system:

- Ensure you have a valid Gemini API token. This token is required to interact with the Gemini model and can be obtained on the Gemini API `website <https://ai.google.dev/pricing>`_ (free tier available).
- Use the following command to run the Docker container, which will expose the application on port 8501, set the `GEMINI_API_TOKEN` environment variable, and run the application on the local machine. Note that in a real-world scenario, this token would be stored securely in a secret management system, but since the image is freely available on DockerHub for this POC, it is passed as an environment variable.

>>> docker run -p 8501:8501 -e GEMINI_API_TOKEN="TOKEN_STRING" alice-rag-llm

The application will be accessible locally at `http://0.0.0.0:8501 <http://0.0.0.0:8501>`_.

Running from DockerHub
----------------------

The container is also available on DockerHub at `pmiron/alice-rag-llm <https://hub.docker.com/repository/docker/pmiron/alice-rag-llm/general>`_. Similarly, you can pull the image from the repository and run it directly on your local machine.

>>> docker run -p 8501:8501 -e GEMINI_API_TOKEN="TOKEN_STRING" pmiron/alice-rag-llm:latest
