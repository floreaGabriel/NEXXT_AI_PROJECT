# Raiffeisen Bank AI Hackathon Template

A professional template for building AI-powered banking solutions using OpenAI Agents SDK, scikit-learn, and Streamlit.

## Features

- **Multi-Agent Systems**: Implement complex AI workflows with specialized agents
- **Banking Use Cases**: Pre-configured templates for financial analysis, customer service, compliance, and call center analytics
- **Raiffeisen Bank Branding**: Professional UI with official color palette and styling
- **Production-Ready**: Clean code structure following best practices

## Prerequisites

- Python 3.10 or higher
- AWS Bedrock API key (used via LiteLLM with OpenAI Agents SDK)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd raiffeisen-ai-hackathon
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and set your Bedrock API key
# Required: AWS_BEARER_TOKEN_BEDROCK
# Optional: DEFAULT_LITELLM_MODEL (defaults to anthropic/claude-3-5-sonnet-20240620)
```

## Running the Application
```bash
streamlit run Homepage.py
```

The application will open in your browser at `http://localhost:8501`

## Project Structure
```
raiffeisen-ai-hackathon/
├── assets/             # Static assets (logos, images)
├── src/
│   ├── agents/         # Agent implementations
│   ├── config/         # Configuration settings
│   ├── utils/          # Helper utilities
│   └── components/     # Reusable UI components
├── pages/              # Streamlit pages for each use case
└── streamlit_app.py    # Main application entry point
```

## Challenge Areas

### 1. Financial Data Analysis
Multi-agent system for:
- Transaction pattern analysis
- Risk score calculation
- Automated report generation

### 2. Customer Service
AI chatbot and virtual assistant for:
- Account inquiries
- FAQ responses
- Intelligent routing

### 3. Compliance & Regulations
AI tool for:
- KYC verification
- AML monitoring
- Compliance reporting

### 4. Call Center Analytics
System for:
- Audio transcription
- Sentiment analysis
- Call summarization

### 5. Product Recommendations
Personalized product recommendation system for:
- Profile-based product ranking
- Smart product matching
- Personalized benefit highlighting
- Customer segmentation

## Development

### Adding New Agents

1. Create a new agent file in `src/agents/`
2. Define your agent with appropriate tools and handoffs
3. Import and use in the relevant page

### Customizing UI

Modify `src/components/ui_components.py` for styling changes and `src/config/settings.py` for theme colors.

### Adding New Pages

Create new pages in the `pages/` directory following the naming convention: `{number}_{page_name}.py`

## Best Practices

- Use type hints for better code clarity
- Follow agent patterns from OpenAI Agents SDK documentation
- Keep agents focused on specific tasks
- Implement proper error handling
- Add comprehensive docstrings

## Support

For questions or issues, please refer to:
- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents-python)
- [Streamlit Documentation](https://docs.streamlit.io)