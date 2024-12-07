FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv venv && \
    /bin/bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"


CMD ["/bin/bash", "-c", "source venv/bin/activate && hypercorn main:app --bind 0.0.0.0:8000"]

EXPOSE 8000
