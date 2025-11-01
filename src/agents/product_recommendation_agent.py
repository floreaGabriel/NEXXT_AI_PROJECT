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
        "shopping_credit_card": {
            "name": "Shopping Credit Card",
            "description": "Credit card with interest-free installment options at partner merchants",
            "benefits": ["Up to 12 interest-free installments", "Available for purchases at partner stores", "Maximum transaction value 40,000 RON or 10,000 EUR"],
            "target_audience": "Customers with regular income who make frequent purchases at partner merchants"
        },
        
        "term_deposits": {
            "name": "Term Deposits",
            "description": "Bank deposits with fixed and guaranteed interest rates in RON, EUR, and USD",
            "benefits": ["Competitive interest rates (5.70% for 3-month RON, 5.20% for 12-month RON)", "Minimum deposit: 500 RON, 200 EUR/USD", "Deposit periods: 1-12 months", "Additional 0.30% bonus interest for salary clients", "Guaranteed by Deposit Guarantee Fund"],
            "target_audience": "Clients who want to save without risk and seek guaranteed returns"
        },
        
        "savings_account": {
            "name": "Super Acces Plus Savings Account",
            "description": "Flexible savings account with tiered interest rates and unlimited access to funds",
            "benefits": ["Variable interest rates tiered by balance (2-3% RON, 0.50% EUR, 0.30% USD)", "Minimum opening amount: 1 RON/EUR/USD", "Unlimited withdrawals without penalties", "Zero administration fees", "Daily interest calculation, monthly capitalization", "SavingBox automatic savings feature (1%, 3%, 5%, 10% of debit card payments)"],
            "target_audience": "Clients who want flexibility and immediate access to their savings"
        },
        
        "debit_card_premium": {
            "name": "Visa Debit Platinum Card",
            "description": "Premium debit card with extended benefits and included insurance",
            "benefits": ["Zero commission for merchant payments", "LoungeKey airport lounge access", "Travel insurance included", "Exclusive discounts and offers", "BlackCab service", "Premium roadside assistance", "Concierge service"],
            "target_audience": "High-income clients who travel frequently and seek premium banking services"
        },
        
        "mortgage_credit": {
            "name": "Casa Ta Mortgage Credit",
            "description": "Real estate loan for purchasing, constructing or refinancing a home",
            "benefits": ["Amount: 5,000-300,000 EUR equivalent", "Period: 3-30 years", "Minimum down payment: 15%", "Fixed interest for 3 or 5 years starting from 5.10%, then variable (margin 2.40% + IRCC)", "Refinancing option with bonus of 2,000 RON", "Noua Casa government program available (5-15% down payment, 2% interest)"],
            "target_audience": "Young families or clients who want to purchase a home"
        },
        
        "personal_loan": {
            "name": "Flexicredit Personal Loan",
            "description": "Fast unsecured loan for any purpose",
            "benefits": ["Amount: 500-50,000 EUR equivalent in RON", "Period: 18 months to 5 years", "No collateral required", "Interest from 5.75%", "APR between 8.11%-36.66%", "Fast approval", "Only ID and ANAF consent required", "Minimum net income: 510 EUR"],
            "target_audience": "Clients with short/medium-term financial needs and regular income"
        },
        
        "investment_funds": {
            "name": "SmartInvest Investment Plans",
            "description": "Professionally managed diversified investment portfolios through Raiffeisen Asset Management",
            "benefits": ["Monthly automatic investment from 200 RON/50 EUR/50 USD", "Multiple fund options (bonds, mixed, equity)", "Current fees: 0.99%-2.43% depending on fund", "Zero costs for opening/closing investment plan", "100% online management via Smart Mobile", "Tax advantages (1% tax for holdings over 365 days, 3% under 365 days)", "Professional portfolio management", "Flexible contributions"],
            "target_audience": "Clients with medium/high risk tolerance seeking long-term capital growth"
        },
        
        "private_pension": {
            "name": "Raiffeisen Acumulare Private Pension (Pillar III)",
            "description": "Optional long-term pension savings plan with tax advantages",
            "benefits": ["Voluntary contributions with individual accounts", "Maximum contribution: 15% of gross monthly income", "Minimum contribution: 100 RON/month (Raiffeisen Acumulare)", "Tax exemptions up to 400 EUR/year for both employee and employer contributions", "Professionally invested in various financial instruments", "Potential for better returns than public pension system", "Direct relationship between contributions and benefits"],
            "target_audience": "Employed clients planning for retirement who want to maintain living standards after retirement"
        },
        
        "junior_account": {
            "name": "Teen Account (14-17 years)",
            "description": "Special current account for adolescents aged 14-17 years",
            "benefits": ["Zero fees for account and card administration", "Zero fees for Smart Mobile app", "Free cash withdrawals at any ATM in Romania", "Debit card included (VISA)", "Apple Pay and Google Pay enrollment", "Real-time notifications", "Financial bonus up to unspecified amount", "Parental supervision features", "Financial education tool"],
            "target_audience": "Parents who want to teach financial responsibility to their teenage children (14-17 years old)"
        },
        
        "life_insurance": {
            "name": "Life Insurance with Guaranteed Savings Component",
            "description": "Life insurance with savings and financial protection for family",
            "benefits": ["Financial protection in case of death or permanent disability from accident", "Guaranteed savings component with fixed interest rate", "Junior Protect Plus: savings for children's future (education, business start)", "Senior Protect Plus: retirement comfort and financial stability", "Minimum monthly premium: 100 RON", "No medical exam required", "Simple policy issuance", "Guaranteed sum insured plus supplementary benefit at maturity", "Premium payment continues by insurer in case of covered event"],
            "target_audience": "Clients with families who want financial protection and long-term savings combined"
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
