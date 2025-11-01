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

    

class ProductRecommendationContext(BaseModel):
    """Context for product recommendation operations."""
    user_profile: UserProfile | None = None
    session_id: str | None = None



def _get_products_catalog_dict() -> dict:
    """Internal helper: return products catalog as dict."""
    products = {
        "carduri_cumparaturi": {
            "name": "Card de Cumpărături",
            "description": "Card de credit special pentru cumpărături cu rate fixe și fără dobândă",
            "benefits": ["Rate fără dobândă la parteneri", "Cashback până la 5%", "Asigurare achizitii"],
            "target_audience": "Clienți cu venituri regulate care fac cumpărături frecvente"
        },
        "depozite_termen": {
            "name": "Depozit la Termen",
            "description": "Depozit bancar cu dobândă fixă și garantată",
            "benefits": ["Dobânzi competitive", "Sumă garantată", "Diverse perioade (1-60 luni)"],
            "target_audience": "Clienți care doresc să economisească fără risc"
        },
        "cont_economii": {
            "name": "Cont de Economii",
            "description": "Cont flexibil de economii cu acces rapid la fonduri",
            "benefits": ["Dobândă variabilă", "Retragere fără penalizări", "Fără comision administrare"],
            "target_audience": "Clienți care vor flexibilitate și acces rapid la economii"
        },
        "card_debit": {
            "name": "Card de Debit Premium",
            "description": "Card de debit cu beneficii extinse și asigurări incluse",
            "benefits": ["Cashback 2%", "Asigurare călătorii", "Acces lounge aeroporturi"],
            "target_audience": "Clienți cu venituri mari care călătoresc frecvent"
        },
        "credit_imobiliar": {
            "name": "Credit Imobiliar",
            "description": "Împrumut pentru achiziție sau refinanțare locuință",
            "benefits": ["Dobândă competitivă", "Perioadă până la 30 ani", "Posibilitate avans 0%"],
            "target_audience": "Familii tinere sau clienți care doresc să cumpere casă"
        },
        "credit_nevoi_personale": {
            "name": "Credit Nevoi Personale",
            "description": "Împrumut rapid pentru orice scop",
            "benefits": ["Aprobare rapidă", "Fără garanții până la 50.000 RON", "Rată flexibilă"],
            "target_audience": "Clienți cu nevoi financiare pe termen scurt/mediu"
        },
        "investitii_fonduri": {
            "name": "Fonduri de Investiții",
            "description": "Portofolii diversificate de investiții gestionate profesional",
            "benefits": ["Diversificare risc", "Gestiune profesională", "Multiple strategii"],
            "target_audience": "Clienți cu toleranță medie/ridicată la risc"
        },
        "pensie_privata": {
            "name": "Pensie Privată (Pilon III)",
            "description": "Plan de economii pe termen lung pentru pensie",
            "benefits": ["Avantaje fiscale", "Contribuții flexibile", "Randament pe termen lung"],
            "target_audience": "Clienți angajați care plănuiesc pensionarea"
        },
        "cont_copii": {
            "name": "Cont Junior",
            "description": "Cont de economii special pentru copii",
            "benefits": ["Dobândă bonificată", "Educație financiară", "Card pentru adolescenți"],
            "target_audience": "Părinți care vor să economisească pentru copii"
        },
        "asigurare_viata": {
            "name": "Asigurare de Viață",
            "description": "Protecție financiară pentru familie",
            "benefits": ["Protecție financiară", "Opțiuni investiționale", "Deducere fiscală"],
            "target_audience": "Clienți cu familie care doresc protecție financiară"
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
        if product_id == "pensie_privata" and profile.age >= 40:
            score += 0.2
        if product_id == "cont_copii" and profile.has_children:
            score += 0.2
        if product_id == "credit_imobiliar" and 25 <= profile.age <= 45:
            score += 0.1

    # Risk tolerance
    if profile.risk_tolerance:
        rt = profile.risk_tolerance.lower()
        if product_id in {"depozite_termen", "cont_economii"} and rt in {"scăzută", "scazuta"}:
            score += 0.2
        if product_id == "investitii_fonduri" and rt in {"ridicată", "ridicata"}:
            score += 0.2

    # Financial goals
    if profile.financial_goals:
        goals = {g.lower() for g in profile.financial_goals}
        if product_id == "credit_imobiliar" and any(
            goal in goals for goal in ["cumpărare casă", "cumparare casa", "cumparare casă"]
        ):
            score += 0.25
        if product_id == "cont_economii" and "economii" in " ".join(goals):
            score += 0.15
        if product_id == "depozite_termen" and "economii pe termen lung" in goals:
            score += 0.1
        if product_id == "pensie_privata" and "pensionare" in goals:
            score += 0.15

    # Income-based scoring
    if profile.annual_income is not None:
        if product_id == "card_debit" and profile.annual_income >= 120_000:
            score += 0.1
        if product_id == "credit_imobiliar" and profile.annual_income >= 60_000:
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
