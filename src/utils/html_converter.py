"""HTML Converter pentru Planuri Financiare - Design Raiffeisen Bank.

Convertește markdown plan financiar în HTML profesional cu branding Raiffeisen:
- Culori corporate: Galben (#FFED00) și Alb
- Design responsive și profesional
- Personalizat pentru fiecare client
"""

import re
from typing import Optional


def convert_financial_plan_to_html(
    markdown_content: str,
    client_name: Optional[str] = None,
    client_age: Optional[int] = None,
    client_income: Optional[float] = None
) -> str:
    """Convertește plan financiar Markdown în HTML profesional Raiffeisen.
    
    Args:
        markdown_content: Conținutul planului în Markdown
        client_name: Numele clientului (opțional, pentru personalizare)
        client_age: Vârsta clientului (opțional)
        client_income: Venitul clientului (opțional)
    
    Returns:
        str: HTML complet cu styling Raiffeisen Bank
    """
    
    # Extrage titlul principal (primul H1)
    title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
    main_title = title_match.group(1) if title_match else "Plan Financiar Personalizat"
    
    # Procesare Markdown simplă
    html_body = markdown_content
    
    # Headers (H1, H2, H3)
    html_body = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
    
    # Bold text
    html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
    
    # Lists (bullets)
    html_body = re.sub(r'^\s*[-•]\s+(.+)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
    
    # Wrap consecutive <li> in <ul>
    html_body = re.sub(r'(<li>.*?</li>)(\n<li>.*?</li>)+', 
                       lambda m: '<ul>' + m.group(0).replace('\n', '\n') + '</ul>', 
                       html_body, flags=re.DOTALL)
    
    # Tables (Markdown → HTML)
    def convert_table(match):
        table_text = match.group(0)
        rows = [r.strip() for r in table_text.split('\n') if r.strip()]
        
        if len(rows) < 3:
            return table_text  # Not a valid table
        
        # Header row
        headers = [h.strip() for h in rows[0].split('|') if h.strip()]
        # Skip separator row (rows[1])
        # Data rows
        data_rows = []
        for row in rows[2:]:
            cells = [c.strip() for c in row.split('|') if c.strip()]
            if cells:
                data_rows.append(cells)
        
        # Build HTML table
        html = '<table class="financial-table">\n<thead>\n<tr>\n'
        for header in headers:
            html += f'<th>{header}</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        for cells in data_rows:
            html += '<tr>\n'
            for cell in cells:
                html += f'<td>{cell}</td>\n'
            html += '</tr>\n'
        
        html += '</tbody>\n</table>'
        return html
    
    # Match Markdown tables
    html_body = re.sub(r'^\|.+\|$\n^\|[-:\s|]+\|$\n(^\|.+\|$\n?)+', 
                       convert_table, 
                       html_body, 
                       flags=re.MULTILINE)
    
    # Horizontal rules
    html_body = re.sub(r'^---+$', r'<hr>', html_body, flags=re.MULTILINE)
    
    # Paragraphs (text between blank lines)
    html_body = re.sub(r'\n\n+', '</p>\n<p>', html_body)
    html_body = '<p>' + html_body + '</p>'
    
    # Clean up empty paragraphs
    html_body = re.sub(r'<p>\s*</p>', '', html_body)
    html_body = re.sub(r'<p>(\s*<h[1-3]>)', r'\1', html_body)
    html_body = re.sub(r'(</h[1-3]>\s*)</p>', r'\1', html_body)
    html_body = re.sub(r'<p>(\s*<ul>)', r'\1', html_body)
    html_body = re.sub(r'(</ul>\s*)</p>', r'\1', html_body)
    html_body = re.sub(r'<p>(\s*<table)', r'\1', html_body)
    html_body = re.sub(r'(</table>\s*)</p>', r'\1', html_body)
    html_body = re.sub(r'<p>(\s*<hr>)', r'\1', html_body)
    html_body = re.sub(r'(<hr>\s*)</p>', r'\1', html_body)
    
    # Personalizare header dacă avem date client
    client_greeting = ""
    if client_name:
        client_greeting = f"<p style='font-size: 18px; color: #333; margin-bottom: 25px;'>Bună ziua <strong>{client_name}</strong>,</p>"
    
    client_summary = ""
    if client_age and client_income:
        client_summary = f"""
        <div style='background-color: #FFF9E6; border-left: 4px solid #FFED00; padding: 15px; margin: 20px 0; border-radius: 4px;'>
            <p style='margin: 5px 0; color: #333;'><strong>Profilul dumneavoastră:</strong></p>
            <p style='margin: 5px 0; color: #555;'>Vârstă: {client_age} ani | Venit lunar: {client_income/12:,.0f} RON</p>
        </div>
        """
    
    # Template HTML complet cu design Raiffeisen
    html_template = f"""<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title} - Raiffeisen Bank</title>
    <style>
        /* Raiffeisen Bank Corporate Colors */
        :root {{
            --raiffeisen-yellow: #FFED00;
            --raiffeisen-black: #000000;
            --raiffeisen-gray: #333333;
            --raiffeisen-light-gray: #F5F5F5;
            --raiffeisen-white: #FFFFFF;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--raiffeisen-gray);
            background-color: var(--raiffeisen-white);
            margin: 0;
            padding: 0;
        }}
        
        .email-container {{
            max-width: 650px;
            margin: 0 auto;
            background-color: white;
        }}
        
        /* Header cu branding Raiffeisen */
        .email-header {{
            background: linear-gradient(135deg, var(--raiffeisen-yellow) 0%, #FFD700 100%);
            padding: 30px 20px;
            text-align: center;
            border-bottom: 3px solid var(--raiffeisen-black);
        }}
        
        .email-header h1 {{
            margin: 0;
            color: var(--raiffeisen-black);
            font-size: 28px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .bank-logo {{
            font-size: 14px;
            color: var(--raiffeisen-black);
            font-weight: 600;
            margin-top: 10px;
            letter-spacing: 2px;
        }}
        
        /* Content area */
        .email-content {{
            padding: 30px 25px;
            background-color: white;
        }}
        
        h1 {{
            color: var(--raiffeisen-black);
            font-size: 24px;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid var(--raiffeisen-yellow);
        }}
        
        h2 {{
            color: var(--raiffeisen-gray);
            font-size: 20px;
            margin-top: 25px;
            margin-bottom: 12px;
            padding-left: 12px;
            border-left: 4px solid var(--raiffeisen-yellow);
        }}
        
        h3 {{
            color: var(--raiffeisen-gray);
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        p {{
            margin: 12px 0;
            color: #555;
            font-size: 15px;
            line-height: 1.7;
        }}
        
        ul {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        
        li {{
            margin: 8px 0;
            color: #555;
            font-size: 15px;
        }}
        
        strong {{
            color: var(--raiffeisen-black);
            font-weight: 600;
        }}
        
        /* Tables */
        .financial-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .financial-table thead {{
            background: linear-gradient(135deg, var(--raiffeisen-yellow) 0%, #FFD700 100%);
        }}
        
        .financial-table th {{
            padding: 12px 15px;
            text-align: left;
            font-weight: 700;
            color: var(--raiffeisen-black);
            border: 1px solid #ddd;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .financial-table td {{
            padding: 12px 15px;
            border: 1px solid #ddd;
            color: #555;
            font-size: 14px;
        }}
        
        .financial-table tbody tr:nth-child(even) {{
            background-color: #FFFEF5;
        }}
        
        .financial-table tbody tr:hover {{
            background-color: #FFF9E6;
        }}
        
        /* Horizontal rule */
        hr {{
            border: none;
            border-top: 2px solid var(--raiffeisen-yellow);
            margin: 30px 0;
        }}
        
        /* Highlight boxes */
        .highlight-box {{
            background-color: #FFF9E6;
            border-left: 4px solid var(--raiffeisen-yellow);
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        /* Footer */
        .email-footer {{
            background-color: var(--raiffeisen-black);
            color: var(--raiffeisen-white);
            padding: 25px 20px;
            text-align: center;
            font-size: 13px;
        }}
        
        .email-footer p {{
            margin: 8px 0;
            color: var(--raiffeisen-white);
        }}
        
        .email-footer a {{
            color: var(--raiffeisen-yellow);
            text-decoration: none;
            font-weight: 600;
        }}
        
        .email-footer a:hover {{
            text-decoration: underline;
        }}
        
        /* Call to action button */
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, var(--raiffeisen-yellow) 0%, #FFD700 100%);
            color: var(--raiffeisen-black);
            padding: 14px 30px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 700;
            margin: 20px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}
        
        .cta-button:hover {{
            background: linear-gradient(135deg, #FFD700 0%, var(--raiffeisen-yellow) 100%);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        /* Responsive */
        @media only screen and (max-width: 600px) {{
            .email-content {{
                padding: 20px 15px;
            }}
            
            h1 {{
                font-size: 20px;
            }}
            
            h2 {{
                font-size: 18px;
            }}
            
            .financial-table {{
                font-size: 12px;
            }}
            
            .financial-table th,
            .financial-table td {{
                padding: 8px 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="email-header">
            <h1>🏦 RAIFFEISEN BANK</h1>
            <div class="bank-logo">BANKING & ADVISORY</div>
        </div>
        
        <!-- Content -->
        <div class="email-content">
            {client_greeting}
            
            <p style="font-size: 16px; color: #555; margin-bottom: 20px;">
                Vă mulțumim pentru încrederea acordată! Am pregătit pentru dumneavoastră un plan financiar personalizat, 
                conceput special pentru a vă ajuta să vă atingeți obiectivele financiare.
            </p>
            
            {client_summary}
            
            {html_body}
            
            <hr>
            
            <div class="highlight-box">
                <h3 style="margin-top: 0; color: var(--raiffeisen-black);">📞 Pași Următori</h3>
                <p>Pentru a implementa acest plan financiar personalizat:</p>
                <ul style="margin-bottom: 10px;">
                    <li>Programați o consultanță gratuită cu un specialist Raiffeisen</li>
                    <li>Pregătiți documentele necesare (CI, adeverință venit)</li>
                    <li>Discutați detaliile produselor selectate</li>
                </ul>
                <p style="text-align: center; margin-top: 20px;">
                    <a href="tel:*2000" class="cta-button">📞 Contactează-ne acum</a>
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="email-footer">
            <p><strong>Raiffeisen Bank România</strong></p>
            <p>📞 Tel: <a href="tel:*2000">*2000</a> (gratuit din orice rețea)</p>
            <p>📧 Email: <a href="mailto:advisory@raiffeisen.ro">advisory@raiffeisen.ro</a></p>
            <p>🌐 Web: <a href="https://www.raiffeisen.ro">www.raiffeisen.ro</a></p>
            <hr style="border-color: #555; margin: 20px 0;">
            <p style="font-size: 11px; color: #aaa; margin-top: 15px;">
                Acest email conține informații confidențiale destinate exclusiv dumneavoastră.<br>
                Recomandările sunt orientative și necesită validare cu un consultant financiar certificat.<br>
                © 2025 Raiffeisen Bank România. Toate drepturile rezervate.
            </p>
        </div>
    </div>
</body>
</html>"""
    
    return html_template


def clean_markdown_for_email(markdown_content: str) -> str:
    """Curăță markdown de emoji-uri și formatare problematică pentru email.
    
    Args:
        markdown_content: Conținutul markdown original
    
    Returns:
        str: Markdown curățat, gata pentru conversie HTML
    """
    # Remove emoji
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002700-\U000027BF"  # dingbats
        u"\U0001F900-\U0001F9FF"  # supplemental symbols
        u"\U00002600-\U000026FF"  # misc symbols
        u"\U0001F700-\U0001F77F"  # alchemical symbols
        "]+", 
        flags=re.UNICODE
    )
    cleaned = emoji_pattern.sub('', markdown_content)
    
    # Remove multiple blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned.strip()
