"""Test simplu pentru verificare funcționalitate MCP Pandoc.

Acest script verifică:
1. Dacă mcp-pandoc este instalat
2. Dacă pandoc este disponibil pe sistem
3. Dacă xelatex (TeX Live) este disponibil
4. Dacă agentul poate face conversie Markdown → PDF
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_command(command, name):
    """Verifică dacă o comandă există în sistem."""
    try:
        result = subprocess.run(
            [command, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"  ✅ {name}: {version}")
            return True
        else:
            print(f"  ❌ {name}: Nu este instalat corect")
            return False
    except FileNotFoundError:
        print(f"  ❌ {name}: Nu este instalat")
        return False
    except Exception as e:
        print(f"  ❌ {name}: Eroare la verificare - {e}")
        return False

def check_python_package(package):
    """Verifică dacă un pachet Python este instalat."""
    try:
        import importlib
        importlib.import_module(package.replace('-', '_'))
        print(f"  ✅ {package}: Instalat")
        return True
    except ImportError:
        print(f"  ❌ {package}: Nu este instalat")
        return False

def test_mcp_pandoc():
    """Testează funcționalitatea MCP Pandoc."""
    print("\n" + "=" * 70)
    print("TEST: Verificare MCP Pandoc - Conversie Markdown → PDF")
    print("=" * 70)
    
    # 1. Verificare dependențe Python
    print("\n📦 1. Verificare Pachete Python:")
    print("-" * 70)
    
    all_ok = True
    all_ok &= check_python_package('mcp')
    all_ok &= check_python_package('mcp-pandoc')
    all_ok &= check_python_package('pypandoc')
    
    # 2. Verificare dependențe sistem
    print("\n🔧 2. Verificare Dependențe Sistem:")
    print("-" * 70)
    
    pandoc_ok = check_command('pandoc', 'Pandoc')
    xelatex_ok = check_command('xelatex', 'XeLaTeX (TeX Live)')
    uvx_ok = check_command('uvx', 'UVX')
    
    all_ok &= pandoc_ok and xelatex_ok and uvx_ok
    
    if not pandoc_ok:
        print("\n  💡 Instalează pandoc:")
        print("     brew install pandoc  # macOS")
        print("     sudo apt-get install pandoc  # Ubuntu")
    
    if not xelatex_ok:
        print("\n  💡 Instalează TeX Live:")
        print("     brew install texlive  # macOS")
        print("     sudo apt-get install texlive-xetex  # Ubuntu")
    
    if not uvx_ok:
        print("\n  💡 Instalează UV:")
        print("     brew install uv  # macOS")
        print("     pip install uv  # Linux/Windows")
    
    if not all_ok:
        print("\n" + "=" * 70)
        print("❌ VERIFICARE EȘUATĂ - Instalează dependențele lipsă")
        print("=" * 70)
        print("\nRulează scriptul de instalare automată:")
        print("  bash install_pdf_dependencies.sh")
        return False
    
    # 3. Test conversie simplă
    print("\n📄 3. Test Conversie Markdown → PDF:")
    print("-" * 70)
    
    try:
        from src.agents.pdf_converter_agent import convert_markdown_to_pdf
        
        # Markdown simplu de test
        test_markdown = """# Test Plan Financiar

## Introducere

Acesta este un test pentru verificarea conversiei **Markdown → PDF**.

### Caracteristici Testate

- ✅ Headers (H1, H2, H3)
- ✅ Text bold și *italic*
- ✅ Liste cu bullets
- ✅ Caractere speciale românești: ă, â, î, ș, ț
- ✅ Emoji: 🎯 📊 💰

### Tabel de Test

| Produs | Dobândă | Termen |
|--------|---------|--------|
| Cont Economii | 2.5% | Nelimitat |
| Depozit | 4.0% | 12 luni |

## Concluzie

Dacă vezi acest text în PDF, conversia funcționează perfect! ✅

---

**Generat:** Noiembrie 2025  
**Status:** Test Successful 🎉
"""
        
        print("\n  ⏳ Convertesc Markdown de test în PDF...")
        
        # Conversie
        pdf_path, message = convert_markdown_to_pdf(
            test_markdown,
            "test_verificare_mcp.pdf"
        )
        
        # Verificare fișier creat
        if Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size
            print(f"\n  ✅ PDF generat cu succes!")
            print(f"  📁 Locație: {pdf_path}")
            print(f"  📊 Dimensiune: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            print("\n" + "=" * 70)
            print("✅ TOATE TESTELE AU TRECUT CU SUCCES!")
            print("=" * 70)
            print("\n🎉 MCP Pandoc funcționează perfect!")
            print(f"\n📂 Deschide PDF-ul de test: {pdf_path}")
            
            return True
        else:
            print("\n  ❌ PDF-ul nu a fost creat!")
            return False
            
    except Exception as e:
        print(f"\n  ❌ Eroare la conversie: {str(e)}")
        print("\n  🔍 Detalii eroare:")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 70)
        print("❌ TEST EȘUAT")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = test_mcp_pandoc()
    sys.exit(0 if success else 1)
