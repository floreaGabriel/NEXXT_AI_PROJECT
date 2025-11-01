"""User Experience Summary Personalization Agent

Takes pre-generated English product summaries and personalizes them for individual user profiles.
This agent is part of a three-stage pipeline:
1. Bank product description → NLP summarization (reduces long descriptions)
2. NLP-generated summary → THIS AGENT → Personalized summary for user profile
3. Display personalized content to create bank-user connection

Design principles:
- Receives English summaries as input, returns personalized English summaries
- NEVER hallucinates or adds information not in original summary
- NEVER removes key product information or benefits
- Focuses on reframing existing content to resonate with specific user characteristics
- Creates emotional connection between bank products and user's life situation
- Maintains accuracy and relevance to banking context

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
def personalize_product_summary(
    base_summary: Annotated[str, "Pre-generated English summary from NLP stage"],
    product_name: Annotated[str, "Name of the banking product"],
    user_context: Annotated[str, "User's life situation and financial profile description"],
    relevance_tone: Annotated[str, "Relevance indicator: 'excellent match', 'strong fit', or 'potential option'"],
) -> str:
    """Personalize a banking product summary for a specific user profile.
    
    CRITICAL INSTRUCTIONS FOR LLM:
    - You MUST preserve ALL factual information from the base_summary
    - DO NOT add features, benefits, or details not mentioned in base_summary
    - DO NOT remove any key product information or banking terms
    - Your ONLY job is to adjust language and tone to resonate with user_context
    - Keep the summary concise (2-3 sentences maximum)
    - Maintain professional banking language while being relatable
    - Use relevance_tone to adjust enthusiasm level
    - Connect product features to user's life situation naturally
    - Stay accurate to banking regulations and product reality
    
    Example transformation:
    Base: "Savings account with flexible withdrawals and competitive interest rates."
    User context: "young professional starting financial journey, preferring low-risk"
    Result: "This savings account offers you a secure way to build your financial foundation 
    with flexible access to your money and competitive interest rates—ideal for starting your 
    savings journey without taking unnecessary risks."
    
    Args:
        base_summary: Original NLP-generated summary (source of truth)
        product_name: Product name for context
        user_context: User's profile characteristics
        relevance_tone: Match quality indicator
    
    Returns:
        Personalized English summary (same facts, personalized framing)
    """
    # This tool will be called by the LLM agent
    # The LLM will use the instructions above to generate the personalized summary
    return f"Personalizing {product_name} for user with context: {user_context} (match: {relevance_tone})"


# --- Specialized Personalization Agent ------------------------------------------------------

personalization_specialist = Agent[PersonalizationContext](
    name="Summary Personalization Specialist",
    instructions=(
        "You are a banking content personalization expert. Your ONLY responsibility is to "
        "take pre-generated English product summaries and adapt them for specific user profiles.\n\n"
        
        "CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY:\n"
        "1. NEVER add information not present in the base_summary\n"
        "2. NEVER remove key product features or benefits\n"
        "3. NEVER hallucinate features, rates, or terms\n"
        "4. NEVER change factual banking information\n"
        "5. PRESERVE all product capabilities and limitations mentioned\n\n"
        
        "YOUR TASK:\n"
        "- Adjust language tone to match user's life stage and situation\n"
        "- Connect product features to user's specific needs naturally\n"
        "- Use relevance_tone to modulate enthusiasm (excellent match = warmer tone)\n"
        "- Keep summaries concise: 2-3 sentences maximum\n"
        "- Maintain professional banking language while being relatable\n"
        "- Create emotional connection between product and user's goals\n\n"
        
        "EXAMPLES OF GOOD PERSONALIZATION:\n"
        "Base: 'Fixed-term deposit with guaranteed returns.'\n"
        "User: 'young professional, low-risk preference'\n"
        "Good: 'This fixed-term deposit gives you guaranteed returns—a secure way to grow your "
        "savings without market volatility as you build your financial foundation.'\n\n"
        
        "Base: 'Investment fund with diversified portfolio.'\n"
        "User: 'parent, planning for children's education'\n"
        "Good: 'This diversified investment fund helps you build an education fund for your children "
        "through professional portfolio management that balances growth with risk control.'\n\n"
        
        "EXAMPLES OF BAD PERSONALIZATION (DO NOT DO THIS):\n"
        "❌ Adding: 'This product includes insurance' (if not in base_summary)\n"
        "❌ Removing: 'Fixed-term' constraint if mentioned in base\n"
        "❌ Inventing: Specific rates, terms, or features not mentioned\n"
        "❌ Being too lengthy: More than 3 sentences\n\n"
        
        "When you receive a personalization request, respond with ONLY the personalized summary. "
        "No explanations, no metadata—just the refined English text that maintains accuracy "
        "while resonating with the user's life situation."
    ),
    tools=[personalize_product_summary],
    model=build_default_litellm_model(),
)


personalization_orchestrator = Agent[PersonalizationContext](
    name="Personalization Orchestrator",
    instructions=(
        "You coordinate the summary personalization process for banking products. "
        "You receive products with base summaries and user profile information, then delegate "
        "to the Personalization Specialist to create user-specific versions.\n\n"
        
        "Your workflow:\n"
        "1. Receive list of products with base_summary fields\n"
        "2. Extract user_context and relevance indicators\n"
        "3. For each product, call personalize_product_summary tool\n"
        "4. Return products with personalized_summary fields\n\n"
        
        "Remember: The specialist handles the creative work. You just orchestrate the flow "
        "and ensure all products get personalized versions."
    ),
    handoffs=[personalization_specialist],
    model=build_default_litellm_model(),
)
