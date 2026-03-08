FROM python:3.12-slim

WORKDIR /app

RUN apt-get update -y \
  && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-fra poppler-utils \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000
CMD ["bash", "-lc", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
