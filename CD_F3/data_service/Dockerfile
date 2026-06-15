FROM python:3.11-slim

WORKDIR /app

COPY data_server.py .
COPY dados.json .
COPY utilizadores.json .

CMD ["python", "data_server.py"]
