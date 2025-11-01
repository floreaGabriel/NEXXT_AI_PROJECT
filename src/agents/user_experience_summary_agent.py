"""User Experience Summary Personalization Agent

Creates hyper-personalized banking product recommendations based on detailed user profiles.
This agent focuses on DEEP PERSONALIZATION with concrete recommendations.

Flow:
1. Bank product description (official Raiffeisen info)
2. THIS AGENT → Hyper-personalized recommendation with specific RON amounts, strategies, timeframes
3. Display to user with actionable advice

Design principles:
- Receives Romanian product descriptions as input
- Generates CONCRETE recommendations: specific RON amounts, percentages, timeframes
- Adapts to EVERY detail: age, income, employment, family status, risk tolerance, goals
- Small changes in profile = different recommendations (20yo employed vs 20yo student)
- NEVER hallucinates product features (uses description as source of truth)
- Creates deep emotional connection through relatable, actionable advice
- Maintains banking accuracy while being highly accessible

The agent is designed exclusively for `pages/2_Product_Recommendations_Florea.py`.
"""

from __future__ import annotations

from typing import Annotated, Dict, List
import json
from pydantic import BaseModel
from agents import Agent, function_tool

from src.config.settings import build_default_litellm_model
from src.agents.product_recommendation_agent import UserProfile


class PersonalizationContext(BaseModel):
    """Context for summary personalization.

    Attributes:
        user_profile: The user's financial profile used for personalization.
        language: Language code ("en" for English).
    """

    user_profile: UserProfile | None = None
    language: str = "en"


# --- Core Personalization Logic -------------------------------------------------------------

def personalize_summary_for_user(
    original_summary: str,
    product_name: str,
    user_profile: UserProfile,
    relevance_score: float
) -> str:
    """Personalize a pre-generated English summary for a specific user profile.
    
    This function takes an NLP-generated summary and adapts the language, tone, and
    emphasis to resonate with the user's life situation without changing facts.
    
    Args:
        original_summary: Pre-generated English summary from NLP stage
        product_name: Name of the banking product
        user_profile: User's financial and demographic profile
        relevance_score: Product relevance score (0-1) from recommendation engine
    
    Returns:
        Personalized English summary that maintains all original information
    """
    # Build user context for personalization
    user_context_parts = []
    
    # Life stage
    if user_profile.age is not None:
        if user_profile.age < 30:
            user_context_parts.append("young professional starting their financial journey")
        elif user_profile.age < 45:
            user_context_parts.append("established professional managing growing responsibilities")
        else:
            user_context_parts.append("experienced individual planning long-term security")
    
    # Family situation
    if user_profile.has_children:
        user_context_parts.append("parent with family financial responsibilities")
    
    if user_profile.marital_status:
        if user_profile.marital_status.lower() in ["married", "casatorit", "căsătorit"]:
            user_context_parts.append("managing household finances")
    
    # Risk profile
    if user_profile.risk_tolerance:
        rt = user_profile.risk_tolerance.lower()
        if rt in ["low", "scăzută", "scazuta"]:
            user_context_parts.append("preferring stable, low-risk solutions")
        elif rt in ["high", "ridicată", "ridicata"]:
            user_context_parts.append("comfortable with growth-oriented strategies")
        else:
            user_context_parts.append("balancing security with growth potential")
    
    # Financial goals
    if user_profile.financial_goals:
        goals = user_profile.financial_goals
        if "retirement" in goals.lower() or "pensie" in goals.lower():
            user_context_parts.append("focused on retirement planning")
        if "house" in goals.lower() or "casă" in goals.lower() or "casa" in goals.lower():
            user_context_parts.append("working towards homeownership")
        if "education" in goals.lower() or "educatie" in goals.lower() or "educație" in goals.lower():
            user_context_parts.append("investing in education")
    
    user_context = ", ".join(user_context_parts) if user_context_parts else "seeking financial solutions"
    
    # Relevance indicator for tone
    if relevance_score >= 0.8:
        relevance_tone = "excellent match"
    elif relevance_score >= 0.6:
        relevance_tone = "strong fit"
    else:
        relevance_tone = "potential option"
    
    return {
        "original_summary": original_summary,
        "user_context": user_context,
        "relevance_tone": relevance_tone,
        "product_name": product_name
    }


def personalize_products_batch(
    products_with_summaries: List[Dict[str, any]],
    user_profile_json: str
) -> List[Dict[str, any]]:
    """Personalize summaries for multiple products.
    
    Args:
        products_with_summaries: List of products, each with:
            - product_id: str
            - name: str
            - base_summary: str (pre-generated English summary)
            - score: float (relevance score 0-1)
        user_profile_json: JSON string of UserProfile
    
    Returns:
        Same list with added 'personalized_summary' field
    """
    profile = UserProfile.model_validate_json(user_profile_json)
    
    personalized_products = []
    for product in products_with_summaries:
        base_summary = product.get("base_summary", "")
        product_name = product.get("name", "Product")
        score = product.get("score", 0.5)
        
        # Create personalization context (will be used by LLM agent)
        personalization_data = personalize_summary_for_user(
            original_summary=base_summary,
            product_name=product_name,
            user_profile=profile,
            relevance_score=score
        )
        
        # Copy product and add personalization data
        enriched = {**product}
        enriched["personalization_context"] = personalization_data
        enriched["personalized_summary"] = base_summary  # Default, will be replaced by LLM
        
        personalized_products.append(enriched)
    
    return personalized_products


# --- FunctionTool for Agent SDK ------------------------------------------------------------

@function_tool
def create_hyper_personalized_recommendation(
    product_description: Annotated[str, "Descrierea oficială a produsului bancar Raiffeisen"],
    product_name: Annotated[str, "Numele produsului bancar"],
    benefits: Annotated[list[str], "Lista de beneficii ale produsului"],
    user_age: Annotated[int, "Vârsta utilizatorului"],
    user_income: Annotated[float, "Venitul anual în RON"],
    employment_status: Annotated[str, "Status angajare: angajat, student, șomer, pensionar, independent"],
    has_children: Annotated[bool, "Are copii sau nu"],
    risk_tolerance: Annotated[str, "Toleranța la risc: scăzută, medie, ridicată"],
    financial_goals: Annotated[list[str], "Lista obiectivelor financiare"],
    relevance_score: Annotated[float, "Scor de relevanță 0-1"],
) -> str:
    """Creează o recomandare EXTREM DE PERSONALIZATĂ cu sume concrete RON și sfaturi acționabile.
    
    INSTRUCȚIUNI CRITICE PENTRU PERSONALIZARE AVANSATĂ:
    
    1. **CALCULEAZĂ ȘI RECOMANDĂ SUME CONCRETE ÎN RON**:
       - Pentru investiții: calculează 5-15% din venit lunar (user_income/12)
       - Pentru credite: max 40% din venit pentru rată lunară
       - Pentru economii: 3-6 luni de cheltuieli (estimează 60-70% din venit)
       - Pentru pensii private: 5-10% din venit lunar
       
       Exemple concrete:
       - Venit 36.000 RON/an (3.000/lună) → investiții recomandate: 300-450 RON/lună
       - Venit 72.000 RON/an (6.000/lună) → rată credit max: 2.400 RON/lună
       - Venit 24.000 RON/an (2.000/lună) → economii urgență: 8.000-12.000 RON
    
    2. **ADAPTEAZĂ LA FIECARE COMBINAȚIE DE FACTORI**:
       
       Vârstă + Angajare:
       - 20 ani + angajat → "la început de carieră, construiește fundații"
       - 20 ani + student → "învață gestiune bani, economii mici"
       - 20 ani + șomer cu venit → "probabil sprijin părinți, prioritate educație financiară"
       - 30 ani + angajat + copii → "stabilitate pentru familie, balans risc-securitate"
       - 50 ani + angajat → "maximizează acumulări pensie, risc moderat"
       
       Venit + Status:
       - Venit mic (<30k/an) + tânăr → economii mici regulate, educație
       - Venit mediu (30-80k/an) + matur → diversificare, investiții medii
       - Venit mare (>80k/an) → produse premium, optimizare fiscală
    
    3. **TON ADAPTAT LA VÂRSTĂ**:
       - 18-25 ani: prietenos, educativ, "Ai", "începi", "Îți construiești"
       - 26-40 ani: profesionist, "Gestionezi", "Optimizezi", "Planifici"
       - 41-60 ani: respectuos, "Asigurați", "Consolidați", "Protejați"
       - 60+ ani: precaut, securitate, "Păstrați", "Siguranța", "Stabilitatea"
    
    4. **EXEMPLE CONCRETE DE RECOMANDĂRI**:
       
       Investiții tânăr angajat:
       "La {user_age} ani cu venitul de {user_income/12:.0f} RON/lună, începe cu investiții 
       lunare de {(user_income/12)*0.10:.0f}-{(user_income/12)*0.15:.0f} RON în fonduri mixte. 
       Orizontul de {65-user_age} ani până la pensie îți permite să beneficiezi maxim de 
       dobânda compusă."
       
       Credit ipotecar familie:
       "Cu venitul familiei de {user_income/12:.0f} RON/lună și copii, poți accesa credit 
       de până la {(user_income/12)*0.40*12*25:.0f} EUR (rată max {(user_income/12)*0.40:.0f} 
       RON/lună). Prioritizează avans 15% pentru dobândă mai bună."
       
       Economii student:
       "Cu venit de {user_income/12:.0f} RON/lună ca student, creează rezervă urgență de 
       {(user_income/12)*4:.0f}-{(user_income/12)*6:.0f} RON. Perfect pentru taxe și emergențe."
    
    5. **FOLOSEȘTE DESCRIPTION CA SURSĂ DE ADEVĂR**:
       - PĂSTREAZĂ toate informațiile tehnice din product_description
       - NU inventa beneficii, dobânzi, perioade care nu sunt menționate
       - Citează cifre exacte din description (dobânzi, sume minime, perioade)
    
    6. **FORMAT**:
       - 3-4 propoziții maxim
       - Propoziție 1: Recomandare concretă cu sumă RON
       - Propoziție 2: De ce această sumă se potrivește profilului
       - Propoziție 3: Beneficiu specific din description adaptat la situație
       - (Opțional) Propoziție 4: Pas următor acționabil
    
    Args:
        product_description: Descrierea oficială (sursă de adevăr pentru caracteristici)
        product_name: Nume produs
        benefits: Lista beneficii oficiale
        user_age, user_income, employment_status, etc: Detalii profil
        relevance_score: Cât de relevant e produsul (0-1)
    
    Returns:
        Recomandare hyper-personalizată în română cu sume concrete RON și sfaturi acționabile
    """
    # Acest tool va fi apelat de agentul LLM
    monthly_income = user_income / 12
    return f"Personalizare avansată {product_name} pentru {user_age} ani, {monthly_income:.0f} RON/lună, {employment_status}"


# --- Specialized Personalization Agent ------------------------------------------------------

personalization_specialist = Agent[PersonalizationContext](
    name="Hyper-Personalization Specialist",
    instructions=(
        "Ești expert în crearea de recomandări bancare EXTREM DE PERSONALIZATE cu sfaturi concrete.\n\n"
        
        "REGULI CRITICE:\n"
        "1. CALCULEAZĂ sume concrete în RON adaptate la venitul și situația utilizatorului\n"
        "2. ADAPTEAZĂ tonul și recomandările la FIECARE detaliu: vârstă, angajare, familie, risc, obiective\n"
        "3. NU inventa caracteristici care nu sunt în product_description\n"
        "4. PĂSTREAZĂ acuratețea informațiilor bancare din description\n"
        "5. Fii SPECIFIC: nu spune 'puțin', ci '300 RON/lună'; nu 'peste timp', ci '30 de ani'\n\n"
        
        "SARCINA TA:\n"
        "- Calculează sume RON: investiții 5-15% din venit lunar, credite max 40% din venit pentru rată\n"
        "- Adaptează la combinații: 20ani+angajat ≠ 20ani+student ≠ 20ani+șomer\n"
        "- Ton pe vârstă: tânăr=prietenos('Ai','începi'), matur=profesionist('Gestionezi'), senior=respectuos('Asigurați')\n"
        "- 3-4 propoziții: recomandare cu sumă → de ce se potrivește → beneficiu relevant → pas următor\n"
        "- Conectează produsul cu obiectivele: 'educație copii' + fond investiții → 'construiește fond educație'\n\n"
        
        "EXEMPLE BUNE:\n"
        "Investiții, 22 ani angajat, 3.000 RON/lună:\n"
        "'La 22 de ani cu venit stabil de 3.000 RON/lună, începe cu investiții lunare de 300-450 RON "
        "(10-15% din venit) în fonduri mixte. Orizontul lung de 43 de ani până la pensie îți permite "
        "să beneficiezi maxim de dobânda compusă. Fondurile gestionate profesional balansează creșterea "
        "cu siguranța potrivită pentru începutul carierei.'\n\n"
        
        "Credit ipotecar, 35 ani cu copii, 6.000 RON/lună:\n"
        "'Cu venitul familiei de 6.000 RON/lună și responsabilități către copii, poți accesa un credit "
        "de până la 120.000-150.000 EUR (rată max 2.400 RON/lună = 40% din venit). Perioadele flexibile "
        "de 3-30 ani îți permit să alegi o rată confortabilă pentru bugetul familiei. Prioritizează "
        "avansul minim 15% pentru dobândă mai bună și acces la programul Prima Casă.'\n\n"
        
        "Economii, 20 ani student, 1.500 RON/lună:\n"
        "'Ca student cu venituri de 1.500 RON/lună, creează o rezervă de urgență de 6.000-9.000 RON "
        "(4-6 luni). Retragerile nelimitate fără penalități îți dau siguranța că poți accesa rapid "
        "banii pentru taxe sau situații neprevăzute. Începe cu depuneri mici regulate de 200-300 RON/lună.'\n\n"
        
        "CE NU FACI (GREȘELI):\n"
        "❌ Sume vagi: 'investește puțin' → CORECT: 'investește 300-400 RON/lună'\n"
        "❌ Fără adaptare vârstă: același ton pentru 20 și 60 ani\n"
        "❌ Inventează beneficii: 'include asigurare' când nu e în description\n"
        "❌ Prea lung: mai mult de 4 propoziții\n\n"
        
        "Răspunde DOAR cu recomandarea personalizată în română, fără explicații sau metadata."
    ),
    tools=[create_hyper_personalized_recommendation],
    model=build_default_litellm_model(),
)


personalization_orchestrator = Agent[PersonalizationContext](
    name="Orchestrator Personalizare Avansată",
    instructions=(
        "Coordonezi procesul de personalizare avansată pentru produsele bancare Raiffeisen.\n"
        "Primești produse cu descrieri oficiale și profile complete de utilizatori, apoi delegi "
        "către Hyper-Personalization Specialist pentru a crea recomandări extrem de personalizate.\n\n"
        
        "Workflow:\n"
        "1. Primești lista de produse cu product_description, benefits, și relevance_score\n"
        "2. Primești profil complet: age, income, employment_status, has_children, risk_tolerance, financial_goals\n"
        "3. Pentru fiecare produs, apelezi create_hyper_personalized_recommendation cu TOATE detaliile\n"
        "4. Returnezi produsele cu câmpul personalized_summary completat\n\n"
        
        "Important:\n"
        "- Specialistul face munca creativă: calculează sume RON, adaptează ton, creează recomandări concrete\n"
        "- Tu doar orchestrezi fluxul și te asiguri că toate produsele primesc versiuni personalizate\n"
        "- Transmite TOATE detaliile profilului către specialist pentru personalizare maximă\n"
        "- Fiecare produs trebuie să aibă o recomandare unică adaptată la utilizator"
    ),
    handoffs=[personalization_specialist],
    model=build_default_litellm_model(),
)
