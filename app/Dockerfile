FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# M13: Chmod 777 on uploads (World Writable)
RUN mkdir -p uploads && chmod -R 777 /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
