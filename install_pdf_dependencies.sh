#!/bin/bash

# Script automat instalare dependențe MCP Pandoc pentru conversie PDF
# Suportă macOS (Homebrew) și Linux (apt)

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "  Instalare Dependențe MCP Pandoc - Conversie Markdown → PDF"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "✓ OS detectat: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "✓ OS detectat: Linux"
else
    echo "❌ OS-ul '$OSTYPE' nu este suportat automat"
    echo "   Instalează manual: pandoc și texlive"
    exit 1
fi

echo ""
echo "────────────────────────────────────────────────────────────────"
echo "1️⃣  Instalare Pandoc"
echo "────────────────────────────────────────────────────────────────"

# Check if pandoc is already installed
if command -v pandoc &> /dev/null; then
    echo "✓ Pandoc este deja instalat"
    pandoc --version | head -1
else
    echo "⏳ Instalez pandoc..."
    if [[ "$OS" == "macos" ]]; then
        brew install pandoc
    else
        sudo apt-get update
        sudo apt-get install -y pandoc
    fi
    echo "✓ Pandoc instalat cu succes!"
fi

echo ""
echo "────────────────────────────────────────────────────────────────"
echo "2️⃣  Instalare TeX Live (pentru conversie PDF)"
echo "────────────────────────────────────────────────────────────────"

# Check if xelatex is already installed
if command -v xelatex &> /dev/null; then
    echo "✓ TeX Live este deja instalat"
    xelatex --version | head -1
else
    echo "⏳ Instalez TeX Live..."
    echo "   ⚠️  ATENȚIE: TeX Live este mare (~2-3 GB)"
    echo "   Instalarea poate dura 5-15 minute..."
    
    if [[ "$OS" == "macos" ]]; then
        brew install texlive
    else
        sudo apt-get install -y texlive-xetex texlive-fonts-recommended
    fi
    echo "✓ TeX Live instalat cu succes!"
fi

echo ""
echo "────────────────────────────────────────────────────────────────"
echo "3️⃣  Instalare Pachete Python"
echo "────────────────────────────────────────────────────────────────"

# Check if in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Nu ești într-un virtual environment"
    echo "   Recomandat: activează venv-ul înainte de instalare"
    echo "   source .venv/bin/activate  # sau calea corectă"
    echo ""
    read -p "Continui instalarea în environment-ul global? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Instalare anulată"
        exit 1
    fi
fi

echo "⏳ Instalez mcp-pandoc și dependențe..."
pip install -q mcp-pandoc

echo "✓ Pachete Python instalate cu succes!"

echo ""
echo "────────────────────────────────────────────────────────────────"
echo "4️⃣  Verificare Instalare"
echo "────────────────────────────────────────────────────────────────"

echo ""
echo "Verificare pandoc:"
pandoc --version | head -1
echo ""
echo "Verificare xelatex:"
xelatex --version | head -1
echo ""
echo "Verificare mcp-pandoc:"
pip show mcp-pandoc | grep "Version:"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ INSTALARE COMPLETĂ CU SUCCES!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Următorii pași:"
echo ""
echo "   1️⃣  Testează conversia PDF:"
echo "      python test_pdf_conversion.py"
echo ""
echo "   2️⃣  Sau pornește aplicația:"
echo "      streamlit run Homepage.py"
echo ""
echo "   3️⃣  În aplicație:"
echo "      • Du-te la Product Recommendations"
echo "      • Generează un plan financiar"
echo "      • Click 'Generează PDF'"
echo ""
echo "📁 PDF-urile vor fi salvate în:"
echo "   ~/Downloads/NEXXT_Financial_Plans/"
echo ""
echo "════════════════════════════════════════════════════════════════"
