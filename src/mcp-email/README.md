# MCP Email Server

A Model Context Protocol (MCP) server that provides email sending capabilities via SMTP.

## Features

- **send_email**: Send emails via SMTP with TLS support
- Configurable SMTP settings via environment variables
- Error handling and status reporting
- Docker support for easy deployment

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMTP_HOST` | Yes | - | SMTP server hostname (e.g., smtp.gmail.com) |
| `SMTP_PORT` | No | 587 | SMTP server port |
| `SMTP_USER` | No | - | SMTP username for authentication |
| `SMTP_PASSWORD` | No | - | SMTP password for authentication |
| `SMTP_TLS` | No | true | Whether to use TLS encryption |
| `FROM_EMAIL` | No | SMTP_USER | Default sender email address |

## Installation

### Local Development

```bash
cd src/mcp-email
pip install -r requirements.txt
```

### Docker

```bash
cd src/mcp-email
docker-compose up -d
```

## Usage

### Running the Server

```bash
python -m mcp_email.server
```

### Available Tools

#### send_email

Send an email via SMTP.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject line
- `body` (string, required): Email body content in plain text
- `from_email` (string, optional): Sender email address (overrides FROM_EMAIL)

**Example:**
```json
{
  "to": "recipient@example.com",
  "subject": "Test Email",
  "body": "This is a test email sent via MCP Email Server.",
  "from_email": "sender@example.com"
}
```

**Response:**
```
✓ Email sent successfully to recipient@example.com
```

## Integration with Agents

To use this MCP server with your AI agents, connect the agent to the MCP server and use the `send_email` tool:

```python
from agents import Agent, mcp_tool
from mcp import StdioServerParameters, stdio_client

# Configure MCP connection
server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp_email.server"],
    env={"SMTP_HOST": "smtp.example.com", ...}
)

# Use in agent
email_agent = Agent(
    name="Email Agent",
    instructions="Send emails using the send_email MCP tool",
    tools=[mcp_tool(server_params)],
)
```

## Testing

Set up your SMTP credentials in environment variables and test the server:

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export FROM_EMAIL=your-email@gmail.com

python -m mcp_email.server
```

## Security Notes

- Never commit SMTP credentials to version control
- Use environment variables or secure secrets management
- For Gmail, use App Passwords instead of your main password
- Consider using `.env` files for local development (not committed)

## License

Part of the NEXXT_AI_PROJECT
