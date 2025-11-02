FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_email /app/mcp_email

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "mcp_email.server"]
