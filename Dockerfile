# SkillAdapt experiment image. Real library versions are installed on demand into /cache/envs with uv.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl git openssl \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv==0.12.21 requests==2.32.3 PyYAML==6.0.2 numpy==2.1.3 matplotlib==3.9.2
ENV UV_PYTHON_INSTALL_DIR=/cache/uv-python \
    UV_CACHE_DIR=/cache/uv-cache \
    UV_PYTHON_PREFERENCE=only-managed \
    SA_ENVS=/cache/envs \
    SA_UV=uv \
    PYTHONUNBUFFERED=1 \
    OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
WORKDIR /work
CMD ["python", "run.py", "--help"]
