FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY minichess.py app.py server.html ./

RUN useradd --system --no-create-home app
USER app

ENV HOST=0.0.0.0 PORT=8000 MAX_DEPTH=4
EXPOSE 8000
CMD ["python", "-u", "app.py"]
