"""Financial Plan Agent - Generates comprehensive personalized financial plans.

This agent creates detailed, actionable financial plans based on:
- User's financial profile (income, goals, risk tolerance, life stage)
- Selected banking products from recommendations
- Product summaries and benefits
- Timeline and implementation strategy

The plan includes:
- Executive summary
- Current financial situation analysis
- Product integration strategy
- Timeline and action steps
- Risk assessment
- Expected outcomes and benefits
"""

from agents import Agent, ModelSettings
from src.config.settings import build_default_litellm_model


financial_plan_agent = Agent(
    name="Financial Plan Generator",
    instructions=(
        "You are a professional financial advisor specialized in creating comprehensive, "
        "personalized financial plans for banking customers.\n\n"
        
        "Your role is to analyze the user's financial profile and selected products, "
        "then create a detailed, actionable financial plan in Romanian language.\n\n"
        
        "PLAN STRUCTURE (MANDATORY - Follow exactly):\n\n"
        
        "# Plan Financiar Personalizat\n\n"
        
        "## 1. Rezumat Executiv\n"
        "- Scurtă prezentare a situației financiare actuale (2-3 propoziții)\n"
        "- Obiectivele principale identificate\n"
        "- Produsele recomandate selectate și scopul lor\n\n"
        
        "## 2. Analiza Situației Actuale\n"
        "**Profil Financiar:**\n"
        "- Vârstă și etapă de viață\n"
        "- Venit anual estimat\n"
        "- Situație familială (stare maritală, copii)\n"
        "- Status profesional\n"
        "- Toleranță la risc\n\n"
        
        "**Obiective Financiare:**\n"
        "- Liste obiectivele pe termen scurt (1-3 ani), mediu (3-7 ani) și lung (7+ ani)\n"
        "- Prioritizează obiectivele\n\n"
        
        "## 3. Strategia de Produse Recomandate\n\n"
        "Pentru fiecare produs selectat, creează o subsecțiune:\n\n"
        "### 3.X [Nume Produs]\n"
        "**De ce acest produs:**\n"
        "- Explicație clară cum se potrivește profilului și obiectivelor (2-3 propoziții)\n\n"
        
        "**Beneficii principale:**\n"
        "- Listează 3-5 beneficii specifice pentru situația utilizatorului\n\n"
        
        "**Mod de utilizare recomandat:**\n"
        "- Pași concreți de implementare\n"
        "- Sume recomandate (dacă e cazul)\n"
        "- Frecvență de utilizare/contribuție\n\n"
        
        "## 4. Timeline de Implementare\n\n"
        "**Luna 1-2: Fundamentele**\n"
        "- Pași imediați (ex: deschidere cont, aplicare card)\n"
        "- Configurări inițiale\n\n"
        
        "**Luna 3-6: Consolidare**\n"
        "- Dezvoltarea obiceiurilor financiare\n"
        "- Ajustări și optimizări\n\n"
        
        "**Luna 7-12: Creștere**\n"
        "- Extindere strategii\n"
        "- Evaluare progres\n\n"
        
        "**Anul 2+: Obiective pe Termen Lung**\n"
        "- Planuri investiționale\n"
        "- Securitate financiară\n\n"
        
        "## 5. Analiza Riscurilor și Protecție\n"
        "**Riscuri identificate:**\n"
        "- Liste riscurile financiare relevante pentru profil\n\n"
        
        "**Măsuri de protecție:**\n"
        "- Cum produsele selectate ajută la mitigarea riscurilor\n"
        "- Recomandări suplimentare de protecție\n\n"
        
        "## 6. Rezultate Așteptate\n\n"
        "**Pe termen scurt (1 an):**\n"
        "- Rezultate concrete măsurabile\n\n"
        
        "**Pe termen mediu (3-5 ani):**\n"
        "- Progres către obiectivele majore\n\n"
        
        "**Pe termen lung (7+ ani):**\n"
        "- Securitate financiară și independență\n\n"
        
        "## 7. Pași Următori Imediați\n"
        "1. [Acțiune concretă 1 - prioritate maximă]\n"
        "2. [Acțiune concretă 2]\n"
        "3. [Acțiune concretă 3]\n"
        "etc.\n\n"
        
        "## 8. Recomandări Finale\n"
        "- Sfaturi personalizate pentru maximizarea succesului\n"
        "- Frecvență de revizuire a planului\n"
        "- Când să contactezi un consultant pentru ajustări\n\n"
        
        "---\n\n"
        
        "IMPORTANT GUIDELINES:\n"
        "- Write in professional but accessible Romanian (formal 'dumneavoastră')\n"
        "- Be specific and actionable - avoid generic advice\n"
        "- Use concrete numbers when possible (percentages, amounts, timelines)\n"
        "- Maintain professional banking tone throughout\n"
        "- Keep sections balanced - no section should be too short or too long\n"
        "- Total plan should be 800-1200 words for comprehensive coverage\n"
        "- Use markdown formatting for clear structure\n"
        "- No emojis - keep it professional\n"
        "- Ensure all selected products are addressed individually\n"
        "- Connect products to specific user goals and profile characteristics\n\n"
        
        "INPUT FORMAT YOU'LL RECEIVE:\n"
        "- User Profile JSON: demographic info, financial situation, goals, risk tolerance\n"
        "- Selected Products JSON: array of products with IDs, names, descriptions, benefits, and personalized summaries\n\n"
        
        "Your output should be a complete, ready-to-present financial plan in markdown format."
    ),
    model=build_default_litellm_model(),
    model_settings=ModelSettings(
        temperature=0.7,  # Balanced creativity and consistency
        max_tokens=4000,  # Enough for comprehensive plan
        include_usage=True,
    ),
)


def generate_financial_plan(user_profile: dict, selected_products: list[dict]) -> str:
    """
    Generate a comprehensive financial plan using the LLM agent.
    
    Args:
        user_profile: Dictionary containing user's financial profile
            Expected keys: age, marital_status, annual_income, employment_status,
            has_children, number_of_children, risk_tolerance, financial_goals
        
        selected_products: List of product dictionaries
            Expected keys: product_id, name, name_ro, description, benefits,
            personalized_summary, score
    
    Returns:
        str: Complete financial plan in markdown format
    
    Raises:
        ValueError: If user_profile or selected_products are empty/invalid
        RuntimeError: If LLM agent fails to generate plan
    """
    import json
    from agents import Runner
    import asyncio
    
    # Validation
    if not user_profile:
        raise ValueError("User profile cannot be empty")
    
    if not selected_products or len(selected_products) == 0:
        raise ValueError("At least one product must be selected")
    
    # Build comprehensive prompt
    user_profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)
    products_json = json.dumps(selected_products, ensure_ascii=False, indent=2)
    
    prompt = f"""
Generează un plan financiar personalizat complet și profesional în limba română.

PROFIL UTILIZATOR:
{user_profile_json}

PRODUSE SELECTATE ({len(selected_products)} produse):
{products_json}

Instrucțiuni:
1. Analizează cu atenție profilul utilizatorului și produsele selectate
2. Creează un plan financiar detaliat urmând EXACT structura din instrucțiuni
3. Asigură-te că fiecare produs selectat este adresat individual în Secțiunea 3
4. Conectează fiecare produs la obiectivele și situația specifică a utilizatorului
5. Oferă recomandări concrete, măsurabile și acționabile
6. Păstrează un ton profesional, dar accesibil
7. Plan complet: 800-1200 cuvinte
8. Format: Markdown, fără emoji

Generează planul financiar acum:
"""
    
    # Run agent
    async def _generate():
        result = await Runner.run(financial_plan_agent, prompt)
        return result
    
    try:
        # Execute async function
        result = asyncio.run(_generate())
        
        # Extract the plan text from result
        if hasattr(result, 'final_response'):
            plan_text = result.final_response
        elif hasattr(result, 'content'):
            plan_text = result.content
        elif isinstance(result, str):
            plan_text = result
        else:
            # Try to extract text from result object
            plan_text = str(result)
        
        return plan_text
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate financial plan: {str(e)}") from e


# Utility function for formatting plan output
def format_plan_for_display(plan_text: str) -> str:
    """
    Post-process the generated plan for optimal display.
    
    Args:
        plan_text: Raw plan text from LLM
    
    Returns:
        str: Formatted plan ready for display
    """
    # Clean up any potential formatting issues
    plan_text = plan_text.strip()
    
    # Ensure consistent line breaks
    plan_text = plan_text.replace('\r\n', '\n')
    
    # Add metadata header
    import datetime
    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
    
    header = f"""---
**Data Generării:** {current_date}  
**Tip Document:** Plan Financiar Personalizat  
**Confidențial:** Document pentru uz personal
---

"""
    
    return header + plan_text


# Example usage and testing
if __name__ == "__main__":
    """
    Test the financial plan agent with sample data.
    Run: python -m src.agents.financial_plan_agent
    """
    
    # Sample user profile
    sample_profile = {
        "first_name": "Ion",
        "last_name": "Popescu",
        "age": 35,
        "marital_status": "Căsătorit/ă",
        "annual_income": 75000.0,
        "employment_status": "Angajat",
        "has_children": True,
        "number_of_children": 2,
        "risk_tolerance": "Medie",
        "financial_goals": [
            "Economii pe termen lung",
            "Educație copii",
            "Cumpărare locuință"
        ]
    }
    
    # Sample selected products
    sample_products = [
        {
            "product_id": "cont_economii",
            "name": "Savings Account",
            "name_ro": "Cont de Economii",
            "description": "Cont flexibil de economii cu acces rapid la fonduri",
            "benefits": [
                "Dobândă variabilă",
                "Retragere fără penalizări",
                "Fără comision administrare"
            ],
            "personalized_summary": "Un cont de economii ideal pentru a construi un fond de urgență și a economisi pentru obiective pe termen scurt.",
            "score": 0.92
        },
        {
            "product_id": "pensie_privata",
            "name": "Private Pension (Pillar III)",
            "name_ro": "Pensie Privată (Pilon III)",
            "description": "Plan de economii pe termen lung pentru pensie",
            "benefits": [
                "Avantaje fiscale",
                "Contribuții flexibile",
                "Randament pe termen lung"
            ],
            "personalized_summary": "Contribuții regulate la o pensie privată vă vor asigura securitate financiară la pensionare și beneficii fiscale imediate.",
            "score": 0.88
        }
    ]
    
    print("🧪 Testing Financial Plan Agent...\n")
    print("=" * 60)
    
    try:
        plan = generate_financial_plan(sample_profile, sample_products)
        formatted_plan = format_plan_for_display(plan)
        
        print("✅ Plan generat cu succes!\n")
        print("=" * 60)
        print(formatted_plan)
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Eroare: {str(e)}")
        import traceback
        traceback.print_exc()
