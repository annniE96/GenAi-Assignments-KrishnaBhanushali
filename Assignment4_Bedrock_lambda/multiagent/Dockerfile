FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY multiagent.py ./
COPY uat_documents ./uat_documents

EXPOSE 8080

CMD ["python", "multiagent.py"]