FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP email server code
COPY mcp_email /app/mcp_email

# Set environment variables (can be overridden)
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["python", "-m", "mcp_email.server"]
