"""Product Recommendation Agent - Personalized banking product recommendations."""

from agents import Agent, function_tool
from typing import Annotated
from pydantic import BaseModel
import json
from src.config.settings import (
    build_default_litellm_model,
)


class UserProfile(BaseModel):
    """User profile for product recommendations."""
    marital_status: str | None = None  # single, married, divorced, widowed
    annual_income: float | None = None  # in RON
    age: int | None = None
    employment_status: str | None = None  # employed, self-employed, unemployed, retired, student
    has_children: bool = False
    risk_tolerance: str | None = None  # low, medium, high
    financial_goals: list[str] = []  # e.g., ["savings", "investment", "home_purchase"]
    education_level: str | None = None  # fara_studii_superioare, liceu, facultate, masterat, doctorat

class ProductRecommendationContext(BaseModel):
    """Context for product recommendation operations."""
    user_profile: UserProfile | None = None
    session_id: str | None = None



def _get_products_catalog_dict() -> dict:
    """Internal helper: return products catalog as dict. Contains official Raiffeisen Bank Romania products."""
    products = {
        "card_cumparaturi_rate": {
            "name": "Card de Cumpărături în Rate",
            "description": "Card de credit cu opțiuni de plată în rate fără dobândă la comercianții parteneri Raiffeisen Bank",
            "base_summary": "Card de credit special pentru cumpărături în rate fără dobândă la magazinele partenere, cu posibilitatea de a plăti până la 12 rate lunare fixe pentru achizițiile tale.",
            "benefits": ["Rate fără dobândă până la 12 luni", "Disponibil la comercianți parteneri", "Valoare maximă tranzacție 40.000 RON sau 10.000 EUR"],
            "target_audience": "Clienți cu venituri regulate care fac achiziții frecvente la parteneri"
        },
        
        "depozite_termen": {
            "name": "Depozite la Termen",
            "description": "Depozite bancare cu dobândă fixă și garantată în RON, EUR și USD",
            "base_summary": "Depozit bancar sigur cu dobândă fixă garantată, oferind randamente competitive cu protecție totală a capitalului pe perioade flexibile de la 1 la 12 luni.",
            "benefits": ["Dobânzi competitive (5.70% la 3 luni RON, 5.20% la 12 luni RON)", "Depozit minim: 500 RON, 200 EUR/USD", "Perioade: 1-12 luni", "Bonus 0.30% pentru clienți cu salariu", "Garantat prin Fondul de Garantare a Depozitelor"],
            "target_audience": "Clienți care doresc să economisească fără risc cu randament garantat"
        },
        
        "cont_economii_super_acces": {
            "name": "Cont de Economii Super Acces Plus",
            "description": "Cont de economii flexibil cu dobândă progresivă și acces nelimitat la fonduri",
            "base_summary": "Cont de economii cu dobândă variabilă progresivă în funcție de sold, oferind acces instant la bani fără penalități și fără comisioane de administrare.",
            "benefits": ["Dobândă variabilă progresivă (2-3% RON, 0.50% EUR, 0.30% USD)", "Sumă minimă deschidere: 1 RON/EUR/USD", "Retrageri nelimitate fără penalizări", "Zero comision administrare", "Calcul zilnic dobândă, capitalizare lunară", "Funcție SavingBox economisire automată (1%, 3%, 5%, 10% din plățile cu cardul)"],
            "target_audience": "Clienți care vor flexibilitate și acces imediat la economii"
        },
        
        "card_debit_platinum": {
            "name": "Card de Debit Visa Platinum",
            "description": "Card de debit premium cu beneficii extinse și asigurări incluse",
            "base_summary": "Card de debit premium cu comision zero la plăți, acces în saloanele de aeroport LoungeKey, asigurare de călătorie inclusă și reduceri exclusive.",
            "benefits": ["Zero comision plăți la comercianți", "Acces LoungeKey în saloanele de aeroport", "Asigurare de călătorie inclusă", "Reduceri și oferte exclusive", "Serviciu BlackCab", "Asistență rutieră premium", "Serviciu de concierge"],
            "target_audience": "Clienți cu venituri mari care călătoresc frecvent și doresc servicii premium"
        },
        
        "credit_ipotecar_casa_ta": {
            "name": "Credit Ipotecar Casa Ta",
            "description": "Credit imobiliar pentru achiziție, construcție sau refinanțare locuință",
            "base_summary": "Credit imobiliar pentru cumpărarea sau refinanțarea casei tale, cu dobândă competitivă, perioadă până la 30 de ani și avans minim de 15%, inclusiv opțiuni prin programul Prima Casă.",
            "benefits": ["Sumă: 5.000-300.000 EUR echivalent", "Perioadă: 3-30 ani", "Avans minim: 15%", "Dobândă fixă 3-5 ani de la 5.10%, apoi variabilă (marjă 2.40% + IRCC)", "Refinanțare cu bonus 2.000 RON", "Program Noua Casă disponibil (avans 5-15%, dobândă 2%)"],
            "target_audience": "Familii tinere sau clienți care doresc să cumpere casă"
        },
        
        "credit_nevoi_personale": {
            "name": "Credit de Nevoi Personale Flexicredit",
            "description": "Credit rapid negarantat pentru orice scop personal",
            "base_summary": "Credit personal rapid cu aprobare în 24 de ore, fără garanții până la 50.000 EUR echivalent, cu rată flexibilă și perioadă de rambursare de până la 5 ani.",
            "benefits": ["Sumă: 500-50.000 EUR echivalent în RON", "Perioadă: 18 luni până la 5 ani", "Fără garanții", "Dobândă de la 5.75%", "DAE între 8.11%-36.66%", "Aprobare rapidă", "Necesare doar CI și consimțământ ANAF", "Venit net minim: 510 EUR"],
            "target_audience": "Clienți cu nevoi financiare pe termen scurt/mediu și venituri regulate"
        },
        
        "fonduri_investitii_smartinvest": {
            "name": "Planuri de Investiții SmartInvest",
            "description": "Portofolii de investiții diversificate gestionate profesional prin Raiffeisen Asset Management",
            "base_summary": "Planuri de investiții cu contribuții lunare automate gestionate de experți, cu opțiuni multiple de fonduri (obligațiuni, mixte, acțiuni) și avantaje fiscale pentru investiții pe termen lung.",
            "benefits": ["Investiție lunară automată de la 200 RON/50 EUR/50 USD", "Opțiuni multiple de fonduri (obligațiuni, mixte, acțiuni)", "Comisioane curente: 0.99%-2.43% în funcție de fond", "Costuri zero pentru deschidere/închidere plan", "Administrare 100% online prin Smart Mobile", "Avantaje fiscale (taxă 1% pentru dețineri peste 365 zile, 3% sub 365 zile)", "Gestiune profesională portofoliu", "Contribuții flexibile"],
            "target_audience": "Clienți cu toleranță medie/ridicată la risc care caută creștere de capital pe termen lung"
        },
        
        "pensie_privata_pilon3": {
            "name": "Pensie Privată Raiffeisen Acumulare (Pilon III)",
            "description": "Plan opțional de economisire pe termen lung pentru pensie cu avantaje fiscale",
            "base_summary": "Plan de pensie privată facultativă cu contribuții voluntare, avantaje fiscale de până la 400 EUR/an și investiții profesionale pentru menținerea nivelului de trai la pensionare.",
            "benefits": ["Contribuții voluntare cu conturi individuale", "Contribuție maximă: 15% din venitul brut lunar", "Contribuție minimă: 100 RON/lună (Raiffeisen Acumulare)", "Scutiri fiscale până la 400 EUR/an pentru contribuții angajat și angajator", "Investiții profesionale în instrumente financiare diverse", "Potențial de randament superior sistemului public de pensii", "Relație directă între contribuții și beneficii"],
            "target_audience": "Clienți angajați care plănuiesc pensionarea și doresc să mențină nivelul de trai"
        },
        
        "cont_junior_adolescenti": {
            "name": "Cont Junior pentru Adolescenți (14-17 ani)",
            "description": "Cont curent special pentru adolescenți cu vârste între 14-17 ani",
            "base_summary": "Cont curent pentru tinerii între 14-17 ani cu card de debit VISA inclus, zero comisioane, retrageri gratuite de numerar la orice bancomat din România și aplicație Smart Mobile pentru educație financiară.",
            "benefits": ["Zero comisioane cont și card", "Zero comisioane Smart Mobile", "Retrageri gratuite numerar la orice bancomat din România", "Card de debit inclus (VISA)", "Apple Pay și Google Pay", "Notificări în timp real", "Bonus financiar", "Supraveghere părintească", "Instrument de educație financiară"],
            "target_audience": "Părinți care doresc să învețe responsabilitatea financiară copiilor adolescenți (14-17 ani)"
        },
        
        "asigurare_viata_economii": {
            "name": "Asigurare de Viață cu Componentă de Economisire",
            "description": "Asigurare de viață cu economii garantate și protecție financiară pentru familie",
            "base_summary": "Asigurare de viață combinată cu economii garantate la dobândă fixă, oferind protecție financiară familiei în caz de deces sau invaliditate și sumă asigurată la scadență.",
            "benefits": ["Protecție financiară în caz de deces sau invaliditate permanentă din accident", "Componentă de economii garantată cu dobândă fixă", "Junior Protect Plus: economii pentru viitorul copiilor (educație, afacere)", "Senior Protect Plus: confort la pensionare și stabilitate financiară", "Primă lunară minimă: 100 RON", "Fără examen medical", "Emitere simplă poliță", "Sumă asigurată garantată plus beneficiu suplimentar la scadență", "Plata primei continuată de asigurător în caz de eveniment acoperit"],
            "target_audience": "Clienți cu familie care doresc protecție financiară și economii pe termen lung combinate"
        }
    }
    return products


@function_tool
def get_raiffeisen_products() -> str:
    """FunctionTool: Get the complete list of available Raiffeisen Bank products as JSON string."""
    return str(_get_products_catalog_dict())


def _calculate_product_score_internal(product_id: str, profile: UserProfile) -> float:
    """Internal scoring logic. Computes relevance score [0..1] for a product given user profile.
    
    TODO: Replace with ML model (sklearn) or fetch from database/API.
    Currently uses rule-based heuristics.
    """
    score = 0.5

    # Age-based scoring
    if profile.age is not None:
        if product_id == "pensie_privata_pilon3" and profile.age >= 40:
            score += 0.2
        if product_id == "cont_junior_adolescenti" and profile.has_children:
            score += 0.2
        if product_id == "credit_ipotecar_casa_ta" and 25 <= profile.age <= 45:
            score += 0.1

    # Risk tolerance
    if profile.risk_tolerance:
        rt = profile.risk_tolerance.lower()
        if product_id in {"depozite_termen", "cont_economii_super_acces"} and rt in {"scăzută", "scazuta", "low"}:
            score += 0.2
        if product_id == "fonduri_investitii_smartinvest" and rt in {"ridicată", "ridicata", "high"}:
            score += 0.2

    # Financial goals
    if profile.financial_goals:
        goals = {g.lower() for g in profile.financial_goals}
        if product_id == "credit_ipotecar_casa_ta" and any(
            goal in goals for goal in ["cumpărare casă", "cumparare casa", "cumparare casă", "casa", "casă", "home"]
        ):
            score += 0.25
        if product_id == "cont_economii_super_acces" and "economii" in " ".join(goals):
            score += 0.15
        if product_id == "depozite_termen" and "economii pe termen lung" in " ".join(goals):
            score += 0.1
        if product_id == "pensie_privata_pilon3" and "pensionare" in " ".join(goals):
            score += 0.15

    # Income-based scoring
    if profile.annual_income is not None:
        if product_id == "card_debit_platinum" and profile.annual_income >= 120_000:
            score += 0.1
        if product_id == "credit_ipotecar_casa_ta" and profile.annual_income >= 60_000:
            score += 0.1

    return max(0.0, min(score, 1.0))


@function_tool
def calculate_product_score(
    product_id: Annotated[str, "Product identifier"],
    user_profile: Annotated[str, "JSON string of user profile data"],
) -> float:
    """FunctionTool: Calculate relevance score for a product based on user profile."""
    profile = UserProfile.model_validate_json(user_profile)
    return _calculate_product_score_internal(product_id, profile)


def rank_products_for_profile(user_profile_json: str) -> list[dict]:
    """MAIN RANKING FUNCTION: Rank all products based on user profile.
    
    This is the core output of the Product Recommendation Agent. It returns
    a list of products sorted by relevance score (highest first).
    
    Args:
        user_profile_json: JSON string of UserProfile
    
    Returns:
        List of dicts with keys: product_id, score
        Sorted descending by score (most relevant first)
    
    Example output:
        [
            {"product_id": "cont_economii", "score": 0.85},
            {"product_id": "depozite_termen", "score": 0.75},
            ...
        ]
    
    TODO: Replace rule-based scoring with:
    - ML model (sklearn, lightgbm, etc.)
    - Collaborative filtering based on similar users
    - Fetch scores from database/API
    - A/B test different ranking strategies
    """
    profile = UserProfile.model_validate_json(user_profile_json)
    catalog = _get_products_catalog_dict()
    
    # Score all products
    scored_products = []
    for product_id in catalog.keys():
        score = _calculate_product_score_internal(product_id, profile)
        scored_products.append({
            "product_id": product_id,
            "score": round(score, 3),
        })
    
    # Sort by score descending (highest relevance first)
    scored_products.sort(key=lambda x: x["score"], reverse=True)
    
    return scored_products


@function_tool
def rank_products_for_user(
    user_profile_json: Annotated[str, "JSON representation of user profile"],
) -> str:

    """FunctionTool: Rank all products and return as JSON string."""
    ranked = rank_products_for_profile(user_profile_json)
    return json.dumps(ranked, ensure_ascii=False)


@function_tool
def generate_personalized_pitch(
    product_id: Annotated[str, "Product identifier"],
    user_profile_json: Annotated[str, "JSON representation of user profile"],
) -> str:
    """Generate personalized product description based on user profile."""
    # TODO: Implement personalization logic, potentially with LLM
    return f"Personalized pitch for {product_id} based on user profile."


# Product Analyzer Agent
product_analyzer_agent = Agent[ProductRecommendationContext](
    name="Product Analyzer",
    instructions="""You are a product analysis specialist for Raiffeisen Bank.
    
    Your role:
    1. Analyze user profiles to understand financial needs and preferences
    2. Calculate relevance scores for each product
    3. Identify the best product matches based on demographics and financial goals
    
    Consider factors like:
    - Income level and stability
    - Life stage (age, marital status, children)
    - Risk tolerance
    - Financial goals
    
    Be data-driven and objective in your analysis.""",
    tools=[get_raiffeisen_products, calculate_product_score, rank_products_for_user],
    model=build_default_litellm_model(),
)

# Personalization Agent
personalization_agent = Agent[ProductRecommendationContext](
    name="Personalization Specialist",
    instructions="""You are a personalization specialist for Raiffeisen Bank.
    
    Your role:
    1. Create personalized product descriptions that resonate with each customer
    2. Highlight benefits most relevant to the user's situation
    3. Use appropriate tone based on customer profile
    
    Tailor your communication to:
    - Customer's life stage and priorities
    - Financial literacy level (inferred from profile)
    - Specific needs and goals
    
    Always be clear, honest, and customer-focused.""",
    tools=[generate_personalized_pitch],
    model=build_default_litellm_model(),
)

# Product Recommendation Orchestrator
product_recommendation_orchestrator = Agent[ProductRecommendationContext](
    name="Product Recommendation Orchestrator",
    instructions="""You are the main orchestrator for personalized product recommendations at Raiffeisen Bank.
    
    Your workflow:
    1. Analyze the user profile using the Product Analyzer to rank products
    2. Use the Personalization Specialist to create tailored descriptions
    3. Present recommendations in order of relevance
    4. Explain why each product is recommended for this specific customer
    
    Always prioritize:
    - Customer needs over product sales
    - Transparency in recommendations
    - Suitability of products for the customer's situation
    
    Provide clear, actionable recommendations that help customers make informed decisions.""",
    handoffs=[product_analyzer_agent, personalization_agent],
    model=build_default_litellm_model(),
)
