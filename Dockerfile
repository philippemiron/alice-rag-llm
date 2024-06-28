# https://docs.streamlit.io/deploy/tutorials/docker
# docker build -t alice-rag-llm .   
# docker run -p 8501:8501 -e GEMINI_API_TOKEN="AIzaSyA3zVz7txsa4jttqMCAKlKrtPQwXcGb6J8" alice-rag-llm

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# from https://rye.astral.sh/guide/docker/
COPY requirements.lock ./
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

COPY src .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
