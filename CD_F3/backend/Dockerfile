FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação (templates, static e Server.py)
COPY . .

CMD ["python", "Server.py"]
