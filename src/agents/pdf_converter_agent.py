"""PDF Converter Agent - Converts Markdown financial plans to PDF using MCP Pandoc.

This agent integrates with the MCP Pandoc server to provide document conversion
capabilities, specifically for converting generated financial plans from Markdown
to PDF format.

The agent uses the convert-contents tool from mcp-pandoc to perform conversions
while preserving formatting and structure.
"""

from agents import Agent
from agents.mcp import MCPServerStdio
from src.utils.mcp_pandoc_client import get_mcp_pandoc_server_config
from src.config.settings import build_default_litellm_model
import tempfile
import os
from pathlib import Path


def create_pdf_converter_agent() -> Agent:
    """Create and configure the PDF converter agent with MCP Pandoc server.
    
    Returns:
        Agent: Configured agent with MCP Pandoc capabilities
    """
    return Agent(
        name="PDF Converter",
        model=build_default_litellm_model(),
        instructions=(
            "You are a document conversion specialist that converts Markdown financial plans to PDF format.\n\n"
            
            "Your capabilities:\n"
            "- Convert Markdown content to professionally formatted PDF documents\n"
            "- Preserve all formatting, headers, lists, and structure from the original Markdown\n"
            "- Handle Romanian language content correctly\n"
            "- Use appropriate fonts and spacing for financial documents\n\n"
            
            "When converting documents:\n"
            "1. Use the convert-contents tool from the MCP Pandoc server\n"
            "2. Set input_format to 'markdown'\n"
            "3. Set output_format to 'pdf'\n"
            "4. Always provide the output_file path (PDF format requires it)\n"
            "5. Ensure the conversion preserves all content and formatting\n\n"
            
            "Important notes:\n"
            "- PDF conversions require a complete output file path\n"
            "- The output path must include the .pdf extension\n"
            "- Verify that the conversion completed successfully\n"
            "- Report any errors clearly to the user\n\n"
            
            "You work with Romanian language financial planning documents and must ensure\n"
            "proper character encoding and formatting for Romanian text."
        ),
        mcp_servers=[MCPServerStdio(get_mcp_pandoc_server_config())],
    )


def convert_markdown_to_pdf(markdown_content: str, output_filename: str = None) -> tuple[str, str]:
    """Convert Markdown financial plan to PDF using the MCP Pandoc agent.
    
    Args:
        markdown_content: The Markdown content to convert
        output_filename: Optional custom filename (without path). If not provided,
                        generates a temporary filename with timestamp.
    
    Returns:
        tuple[str, str]: (output_file_path, conversion_message)
        - output_file_path: Full path to the generated PDF file
        - conversion_message: Success or error message from the agent
    
    Raises:
        RuntimeError: If the conversion fails
        ValueError: If markdown_content is empty or invalid
    
    Example:
        >>> from src.agents.pdf_converter_agent import convert_markdown_to_pdf
        >>> markdown = "# Plan Financiar\\n\\nConținut plan..."
        >>> pdf_path, message = convert_markdown_to_pdf(markdown, "plan_financiar.pdf")
        >>> print(f"PDF saved to: {pdf_path}")
    """
    if not markdown_content or not markdown_content.strip():
        raise ValueError("Markdown content cannot be empty")
    
    # Create output directory for PDFs
    output_dir = Path.home() / "Downloads" / "NEXXT_Financial_Plans"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename if not provided
    if not output_filename:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"plan_financiar_{timestamp}.pdf"
    
    # Ensure .pdf extension
    if not output_filename.endswith('.pdf'):
        output_filename += '.pdf'
    
    output_path = output_dir / output_filename
    
    # Prepare the conversion request
    conversion_request = (
        f"Please convert the following Markdown financial plan to PDF format.\n\n"
        f"Output file path: {str(output_path)}\n\n"
        f"Markdown content:\n\n{markdown_content}"
    )
    
    # Run the conversion using Runner with MCP server
    from agents import Runner, Agent
    from agents.mcp import MCPServerStdio
    import asyncio
    
    async def _convert():
        """Convert with MCP server explicitly connected."""
        # Create MCP server instance
        mcp_server = MCPServerStdio(get_mcp_pandoc_server_config())
        
        try:
            # Connect to MCP server
            await mcp_server.connect()
            
            # Create agent with connected server
            agent = Agent(
                name="PDF Converter",
                model=build_default_litellm_model(),
                instructions=(
                    "You are a document conversion specialist that converts Markdown financial plans to PDF format.\n\n"
                    "Your capabilities:\n"
                    "- Convert Markdown content to professionally formatted PDF documents\n"
                    "- Preserve all formatting, headers, lists, and structure from the original Markdown\n"
                    "- Handle Romanian language content correctly\n"
                    "- Use appropriate fonts and spacing for financial documents\n\n"
                    "When converting documents:\n"
                    "1. Use the convert-contents tool from the MCP Pandoc server\n"
                    "2. Set input_format to 'markdown'\n"
                    "3. Set output_format to 'pdf'\n"
                    "4. Always provide the output_file path (PDF format requires it)\n"
                    "5. Ensure the conversion preserves all content and formatting\n\n"
                    "You work with Romanian language financial planning documents and must ensure\n"
                    "proper character encoding and formatting for Romanian text."
                ),
                mcp_servers=[mcp_server],
            )
            
            # Run the conversion
            result = await Runner.run(agent, conversion_request)
            return result
            
        finally:
            # Always cleanup MCP connection
            try:
                await mcp_server.cleanup()
            except:
                pass  # Ignore cleanup errors
    
    try:
        # Execute async function
        # Handle both standalone and Streamlit contexts
        try:
            # Try to get existing event loop (Streamlit context)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, use nest_asyncio for Streamlit
                import nest_asyncio
                nest_asyncio.apply()
        except RuntimeError:
            # No event loop exists, that's fine
            pass
        
        result = asyncio.run(_convert())
        
        # Verify the file was created
        if not output_path.exists():
            # Extract response content for error message
            response_text = ""
            if hasattr(result, 'final_response'):
                response_text = result.final_response
            elif hasattr(result, 'content'):
                response_text = result.content
            else:
                response_text = str(result)
                
            raise RuntimeError(
                f"PDF file was not created at {output_path}. "
                f"Agent response: {response_text}"
            )
        
        return str(output_path), f"PDF generat cu succes: {output_path.name}"
        
    except Exception as e:
        raise RuntimeError(f"Eroare la conversia PDF: {str(e)}")


def convert_markdown_file_to_pdf(markdown_file_path: str, output_filename: str = None) -> tuple[str, str]:
    """Convert a Markdown file to PDF.
    
    Args:
        markdown_file_path: Path to the input Markdown file
        output_filename: Optional custom filename for the PDF output
    
    Returns:
        tuple[str, str]: (output_file_path, conversion_message)
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
        RuntimeError: If the conversion fails
    """
    markdown_path = Path(markdown_file_path)
    
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_file_path}")
    
    # Read the Markdown content
    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Use the input filename if no output filename provided
    if not output_filename:
        output_filename = markdown_path.stem + '.pdf'
    
    return convert_markdown_to_pdf(markdown_content, output_filename)
