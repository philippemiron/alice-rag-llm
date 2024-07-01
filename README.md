# Alice Retrieval-Augmented Generation (RAG)

Alice Retrieval-Augmented Generation (RAG) is a proof of concept application designed to answer queries about Alice’s Adventures in Wonderland, Lewis Carroll’s timeless classic. This innovative solution leverages the power of modern AI to combine the strengths of retrieval-based and generation-based approaches. By integrating a language model with a customized knowledge store, “Alice RAG” can accurately and efficiently retrieve information from the book and generate responses related to *Alice’s Adventures in Wonderland*.

This project showcases my ability to implement advanced AI techniques, containerization, CI/CD, documentation, and web-based interaction using Streamlit, all while adhering to best practices in software development and deployment.

A Gemini API token is required to run the application. There is a free tier, and a key can be obtained at [Google AI](https://ai.google.dev/pricing). The following command downloads the latest version of the container (built for amd64 and arm64) and maps the Streamlit default port 8501 to a local port (in that case, also 8501).

```
docker run -p 8501:8501 -e GEMINI_API_TOKEN=$GEMINI_API_KEY pmiron/alice-rag-llm:latest
```
then the application will be available locally at [http://0.0.0.0:8501](http://0.0.0.0:8501).

![screnshot-alicerage](img/alicerag.png)
