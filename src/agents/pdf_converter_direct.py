"""Direct Pandoc PDF Converter - Converts Markdown to PDF without MCP.

Fast and reliable PDF generation using pypandoc directly.
"""

import logging
import re
from pathlib import Path
from typing import List, Callable
from datetime import datetime
import tempfile

# Configure logging
logger = logging.getLogger(__name__)

# Type for progress callback
ProgressCallback = Callable[[str], None]


def sanitize_markdown_for_pdf(markdown: str) -> str:
    """Remove emojis and problematic characters that break Pandoc.
    
    Keeps: letters, numbers, Romanian diacritics, basic punctuation, whitespace
    Removes: emojis, special symbols, exotic Unicode
    """
    import re
    
    # Remove ALL emojis and special Unicode symbols
    # This is aggressive but necessary to avoid YAML parse errors
    cleaned = re.sub(
        r'[\U0001F000-\U0001FFFF]|'  # All emoji blocks
        r'[\U00002600-\U000027BF]|'   # Misc symbols  
        r'[\U0000FE00-\U0000FE0F]|'   # Variation selectors
        r'[\U00002000-\U0000206F]|'   # General punctuation
        r'[\U00002300-\U000023FF]|'   # Misc technical
        r'[\U00002B00-\U00002BFF]',   # Misc symbols and arrows
        '', markdown, flags=re.UNICODE)
    
    return cleaned


def convert_markdown_to_pdf_direct(
    markdown_content: str, 
    output_filename: str = None,
    progress_callback: ProgressCallback = None
) -> tuple[str, str, List[str]]:
    """Convert Markdown to PDF using pypandoc directly.
    
    Args:
        markdown_content: The Markdown content to convert
        output_filename: Optional custom filename (without path)
        progress_callback: Optional callback for progress updates
    
    Returns:
        tuple[str, str, List[str]]: (pdf_path, success_message, logs)
    """
    logs = []
    
    def log(message: str, level: str = "INFO"):
        """Internal logging."""
        log_entry = f"[{level}] {message}"
        logs.append(log_entry)
        logger.log(getattr(logging, level), message)
        if progress_callback:
            progress_callback(message)
    
    try:
        log("Validare conținut Markdown...", "INFO")
        if not markdown_content or not markdown_content.strip():
            raise ValueError("Conținut Markdown gol")
        
        log(f"Conținut valid: {len(markdown_content)} caractere", "INFO")
        
        # Sanitize content
        log("Curățare conținut (eliminare emoji și simboluri speciale)...", "INFO")
        cleaned_content = sanitize_markdown_for_pdf(markdown_content)
        log(f"Conținut procesat: {len(cleaned_content)} caractere", "INFO")
        
        # Create output directory
        log("Creare director output...", "INFO")
        output_dir = Path.home() / "Downloads" / "NEXXT_Financial_Plans"
        output_dir.mkdir(parents=True, exist_ok=True)
        log(f"Director: {output_dir}", "INFO")
        
        # Generate filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"plan_financiar_{timestamp}.pdf"
            log(f"Nume fișier generat: {output_filename}", "INFO")
        else:
            log(f"Nume fișier: {output_filename}", "INFO")
        
        if not output_filename.endswith('.pdf'):
            output_filename += '.pdf'
        
        output_path = output_dir / output_filename
        log(f"Cale PDF: {output_path}", "INFO")
        
        # Import pypandoc
        log("Încărcare pypandoc...", "INFO")
        import pypandoc
        log("pypandoc gata", "INFO")
        
        # Create temporary markdown file with UTF-8 encoding
        log("Creare fișier temporar Markdown...", "INFO")
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.md', 
            delete=False, 
            encoding='utf-8'
        ) as tmp:
            tmp.write(cleaned_content)
            tmp_path = tmp.name
        
        log(f"Fișier temporar: {tmp_path}", "INFO")
        
        try:
            # Convert with pandoc
            log("Conversie Markdown -> PDF (XeLaTeX)...", "INFO")
            pypandoc.convert_file(
                tmp_path,
                'pdf',
                outputfile=str(output_path),
                extra_args=[
                    '--pdf-engine=xelatex',
                    '-V', 'geometry:margin=1in',
                    '-V', 'fontsize=11pt',
                    '--no-highlight',  # Disable syntax highlighting that might cause issues
                ],
                encoding='utf-8'
            )
            log("Conversie completă!", "INFO")
            
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
            log("Fișier temporar șters", "INFO")
        
        # Verify PDF was created
        log(f"Verificare PDF...", "INFO")
        if not output_path.exists():
            raise RuntimeError(f"PDF-ul nu a fost creat: {output_path}")
        
        file_size = output_path.stat().st_size
        log(f"PDF creat cu succes!", "INFO")
        log(f"Dimensiune: {file_size:,} bytes ({file_size/1024:.1f} KB)", "INFO")
        log(f"Locație: {output_path}", "INFO")
        
        success_message = f"PDF generat: {output_path.name}"
        return str(output_path), success_message, logs
        
    except ImportError as e:
        error_message = f"pypandoc nu este instalat: {str(e)}"
        log(error_message, "ERROR")
        raise RuntimeError(error_message)
    except Exception as e:
        error_message = f"Eroare la conversie: {str(e)}"
        log(error_message, "ERROR")
        raise RuntimeError(error_message)
