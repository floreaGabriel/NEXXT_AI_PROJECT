"""Product Recommendation Agent - Personalized banking product recommendations.

This agent uses an AI-powered justification system to rank products based on user profiles.
Instead of heuristic scoring, it leverages a specialized tool agent to analyze product relevance.

Architecture:
1. Product Justification Agent (as_a_tool): Analyzes product-user fit with detailed justification
2. Product Recommendation Agent: Orchestrates ranking by calling the tool agent for each product
"""

# Disable tracing BEFORE importing agents to prevent OpenAI API errors
import os as _env_os
_env_os.environ["AGENTS_TRACING_DISABLED"] = "true"
_env_os.environ["OPENAI_TRACING_DISABLED"] = "true"
_env_os.environ["AGENTS_DISABLE_TRACING"] = "true"

# Disable LiteLLM logging and callbacks completely
_env_os.environ["LITELLM_SUCCESS_CALLBACK"] = ""
_env_os.environ["LITELLM_FAILURE_CALLBACK"] = ""
_env_os.environ["LITELLM_DROP_PARAMS"] = "True"

# Import and configure litellm BEFORE any other imports
import warnings
warnings.filterwarnings("ignore")  # Suppress all warnings including async logging errors

import litellm
litellm.suppress_debug_info = True
litellm.set_verbose = False
# Disable success/failure handlers completely
litellm.success_callback = []
litellm.failure_callback = []
# Disable the async logging worker
litellm._async_success_callback = []
litellm._async_failure_callback = []

from agents import Agent, function_tool
from typing import Annotated, List, Dict, Any
from pydantic import BaseModel
import json
import asyncio
import re
import threading
import concurrent.futures
from src.config.settings import build_default_litellm_model
from src.utils.db import get_all_products, get_user_by_email


# ============================================================================
# DATA MODELS
# ============================================================================

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


class ProductJustification(BaseModel):
    """Justification result from the tool agent."""
    product_name: str
    relevance_score: float  # 0.0 to 1.0
    justification: str
    key_benefits: List[str]
    recommended_action: str


class ProductRecommendationContext(BaseModel):
    """Context for product recommendation operations."""
    user_profile: UserProfile | None = None
    session_id: str | None = None



# ============================================================================
# DATABASE HELPERS
# ============================================================================

def _get_products_from_database() -> List[Dict[str, Any]]:
    """Fetch all products from PostgreSQL database.
    
    Returns:
        List of products with id, product_name, product_description
    """
    return get_all_products()


def _extract_product_summary(markdown_content: str) -> str:
    """Extract a concise summary from markdown product description.
    
    Args:
        markdown_content: Full markdown product description
        
    Returns:
        Extracted summary (first 300 chars of general description)
    """
    # Try to extract content after "## Descriere Generală" or similar
    description_match = re.search(
        r'## Descriere.*?\n\n(.*?)(?:\n##|\Z)',
        markdown_content,
        re.DOTALL | re.IGNORECASE
    )
    
    if description_match:
        summary = description_match.group(1).strip()
        # Clean up markdown formatting
        summary = re.sub(r'\*\*', '', summary)
        summary = re.sub(r'\n+', ' ', summary)
        return summary[:300]
    
    # Fallback: return first paragraph
    lines = markdown_content.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            return line[:300]
    
    return "Produs bancar disponibil"


def _extract_product_benefits(markdown_content: str) -> List[str]:
    """Extract key benefits from markdown product description.
    
    Args:
        markdown_content: Full markdown product description
        
    Returns:
        List of benefit strings (up to 5)
    """
    benefits = []
    
    # Try to find "Avantaje" or "Beneficii" section
    benefits_match = re.search(
        r'## (?:Avantaje|Beneficii).*?\n(.*?)(?:\n##|\Z)',
        markdown_content,
        re.DOTALL | re.IGNORECASE
    )
    
    if benefits_match:
        content = benefits_match.group(1)
        # Extract bullet points or numbered items
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Match bullets like "- text" or "* text" or "### number. text"
            if re.match(r'^[-*]\s+', line) or re.match(r'^###\s+\d+\.', line):
                benefit = re.sub(r'^[-*]\s+', '', line)
                benefit = re.sub(r'^###\s+\d+\.\s+', '', benefit)
                benefit = re.sub(r'\*\*', '', benefit)
                if benefit:
                    benefits.append(benefit[:150])
                if len(benefits) >= 5:
                    break
    
    # Fallback: extract from "Caracteristici Principale"
    if not benefits:
        char_match = re.search(
            r'## Caracteristici.*?\n(.*?)(?:\n##|\Z)',
            markdown_content,
            re.DOTALL | re.IGNORECASE
        )
        if char_match:
            content = char_match.group(1)
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 10:
                    benefits.append(line[:150])
                if len(benefits) >= 5:
                    break
    
    return benefits[:5] if benefits else ["Consulta descrierea completa pentru detalii"]


def _get_products_catalog_dict() -> dict:
    """Get products catalog from database with structured information.
    
    This function fetches products from the database and structures them
    for backward compatibility with the UI components.
    
    Returns:
        Dict mapping product names to structured data with keys:
        - name: Product display name
        - description: Concise product summary
        - benefits: List of key benefits
    """
    db_products = _get_products_from_database()
    
    catalog = {}
    for product in db_products:
        product_name = product["product_name"]
        markdown_content = product["product_description"]
        
        # Extract structured data from markdown
        summary = _extract_product_summary(markdown_content)
        benefits = _extract_product_benefits(markdown_content)
        
        # Extract display name from markdown (first H1 heading) or use product_name
        title_match = re.search(r'^#\s+(.+?)(?:\s*-\s*Raiffeisen)?$', markdown_content, re.MULTILINE)
        display_name = title_match.group(1).strip() if title_match else product_name.replace('_', ' ').title()
        
        catalog[product_name] = {
            "name": display_name,
            "description": summary,
            "benefits": benefits,
        }
    
    return catalog



# ============================================================================
# PRODUCT JUSTIFICATION TOOL AGENT
# ============================================================================

# This agent analyzes product-user profile fit and provides detailed justification
product_justification_agent = Agent[ProductRecommendationContext](
    name="Product Justification Expert",
    instructions="""You are a banking product expert. Analyze product-user fit and respond IMMEDIATELY with ONLY valid JSON.

Scoring Guide:
- 0.9-1.0: Perfect fit
- 0.7-0.89: Good fit
- 0.5-0.69: Moderate fit
- 0.3-0.49: Weak fit
- 0.0-0.29: Poor fit

Consider: age, income, family, risk tolerance, goals, life stage.

CRITICAL: Output ONLY JSON, nothing else. No explanations, no markdown, just JSON:

{
  "product_name": "exact product name from input",
  "relevance_score": 0.0-1.0,
  "justification": "2-3 sentences why this score based on user specifics",
  "key_benefits": ["3-5 benefits relevant to THIS user"],
  "recommended_action": "concrete next step with amounts/timeframes"
}

DO NOT use tools. DO NOT ask questions. Respond IMMEDIATELY with JSON.""",
    model=build_default_litellm_model(),
)



# ============================================================================
# SYNCHRONOUS WRAPPER FOR AGENT TOOL
# ============================================================================

async def _analyze_product_fit_async(
    product_name: str,
    product_description: str,
    user_profile: UserProfile
) -> ProductJustification:
    """Async function to call the justification agent tool.
    
    Args:
        product_name: Name of the product
        product_description: Full product description from database
        user_profile: User's financial profile
        
    Returns:
        ProductJustification with score and reasoning
    """
    from agents import Runner
    
    # Build the analysis prompt - simplified to reduce turns
    prompt = f"""Analyze this banking product for the user and output ONLY valid JSON.

PRODUCT: {product_name}
DESCRIPTION: {product_description[:1500]}

USER: {user_profile.age}y, {user_profile.annual_income} RON/year, {user_profile.marital_status}, {user_profile.employment_status}, children={user_profile.has_children}, risk={user_profile.risk_tolerance}, goals={user_profile.financial_goals}

OUTPUT ONLY THIS JSON (no other text):
{{
  "product_name": "{product_name}",
  "relevance_score": 0.0-1.0,
  "justification": "2-3 sentences why this score",
  "key_benefits": ["benefit1", "benefit2", "benefit3"],
  "recommended_action": "concrete next step"
}}"""
    
    # Run the agent asynchronously
    try:
        result = await Runner.run(product_justification_agent, prompt, max_turns=3)
        
        # Extract and parse the output
        output = result.final_output if hasattr(result, 'final_output') else str(result)
        print(f"[Agent Output] {product_name[:30]}: {output[:100]}...")
        
        # Try to parse JSON from output
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return ProductJustification(**parsed)
        else:
            # Fallback if JSON parsing fails
            return ProductJustification(
                product_name=product_name,
                relevance_score=0.5,
                justification="Could not generate detailed analysis",
                key_benefits=["Please review product details"],
                recommended_action="Contact advisor for more information"
            )
    except Exception as e:
        print(f"Error analyzing product {product_name}: {e}")
        # Return neutral score on error
        return ProductJustification(
            product_name=product_name,
            relevance_score=0.5,
            justification=f"Analysis error: {str(e)[:100]}",
            key_benefits=["Review product details manually"],
            recommended_action="Contact advisor for personalized recommendation"
        )


def _analyze_product_fit_sync(
    product_name: str,
    product_description: str,
    user_profile: UserProfile
) -> ProductJustification:
    """Synchronous wrapper that handles event loop properly.
    
    Works in Streamlit (no event loop in thread) and tests.
    Always creates a new event loop in a separate thread for safety.
    """
    result_container = []
    exception_container = []
    
    def run_in_thread():
        """Run async function in a new thread with its own event loop."""
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            result = new_loop.run_until_complete(
                _analyze_product_fit_async(product_name, product_description, user_profile)
            )
            result_container.append(result)
        except Exception as e:
            exception_container.append(e)
        finally:
            new_loop.close()
    
    try:
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join(timeout=45)  # 45 second timeout per product
        
        if not thread.is_alive():
            # Thread completed
            if exception_container:
                raise exception_container[0]
            if result_container:
                return result_container[0]
            else:
                raise RuntimeError("Thread completed but no result returned")
        else:
            # Thread is still running - timeout
            raise TimeoutError(f"Product analysis timed out after 45 seconds")
            
    except Exception as e:
        print(f"Error in sync wrapper for {product_name}: {e}")
        return ProductJustification(
            product_name=product_name,
            relevance_score=0.5,
            justification=f"Analysis error: {str(e)[:100]}",
            key_benefits=["Review product details manually"],
            recommended_action="Contact advisor for personalized recommendation"
        )


# ============================================================================
# MAIN RANKING FUNCTION (NEW AI-POWERED APPROACH)
# ============================================================================

def rank_products_for_profile(user_profile_json: str, max_products: int = None) -> list[dict]:
    """MAIN RANKING FUNCTION: Rank all products using AI-powered justification agent.
    
    This is the core output of the Product Recommendation Agent. Instead of heuristic
    scoring, it uses a specialized AI agent to analyze each product's relevance.
    
    Architecture:
    1. Fetch all products from database
    2. For each product, call the Justification Agent Tool
    3. Agent analyzes product-user fit and returns score + justification
    4. Sort products by relevance score
    
    Args:
        user_profile_json: JSON string of UserProfile
        max_products: Optional limit on number of products to analyze (for performance)
    
    Returns:
        List of dicts with keys: product_id, score, justification
        Sorted descending by score (most relevant first)
    
    Example output:
        [
            {
                "product_id": "cont_economii_super_acces",
                "score": 0.85,
                "justification": "Excellent fit because...",
                "key_benefits": ["benefit1", "benefit2"],
                "recommended_action": "Open account with 1000 RON"
            },
            ...
        ]
    """
    print(f"[Product Recommendation] Starting analysis for user profile...")
    
    # Parse user profile
    profile = UserProfile.model_validate_json(user_profile_json)
    
    # Fetch products from database
    db_products = _get_products_from_database()
    
    if not db_products:
        print("Warning: No products found in database. Returning empty list.")
        return []
    
    # Optionally limit number of products for performance
    if max_products and len(db_products) > max_products:
        print(f"[Product Recommendation] Limiting analysis to {max_products} products (out of {len(db_products)})")
        db_products = db_products[:max_products]
    
    print(f"[Product Recommendation] Analyzing {len(db_products)} products...")
    
    # Score all products using AI agent
    scored_products = []
    
    for idx, product in enumerate(db_products, 1):
        product_name = product["product_name"]
        product_description = product["product_description"]
        
        print(f"[Product Recommendation] {idx}/{len(db_products)}: Analyzing {product_name[:50]}...")
        
        try:
            # Call the AI justification agent
            justification = _analyze_product_fit_sync(
                product_name=product_name,
                product_description=product_description,
                user_profile=profile
            )
            
            scored_products.append({
                "product_id": product_name,  # Using product_name as ID
                "score": round(justification.relevance_score, 3),
                "justification": justification.justification,
                "key_benefits": justification.key_benefits,
                "recommended_action": justification.recommended_action,
            })
            
            print(f"[Product Recommendation] ✓ {product_name[:50]}: Score {justification.relevance_score:.2f}")
            
        except Exception as e:
            print(f"[Product Recommendation] ✗ Error analyzing {product_name}: {e}")
            # Add product with neutral score on error
            scored_products.append({
                "product_id": product_name,
                "score": 0.5,
                "justification": f"Could not analyze: {str(e)[:100]}",
                "key_benefits": ["Contact advisor for details"],
                "recommended_action": "Contact advisor",
            })
    
    # Sort by score descending (highest relevance first)
    scored_products.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"[Product Recommendation] Analysis complete. Top product: {scored_products[0]['product_id'][:50]} ({scored_products[0]['score']})")
    
    return scored_products


# ============================================================================
# MAIN ORCHESTRATOR AGENT
# ============================================================================

product_recommendation_orchestrator = Agent[ProductRecommendationContext](
    name="Product Recommendation Orchestrator",
    instructions="""You are the main orchestrator for personalized product recommendations at Raiffeisen Bank Romania.
    
    Your role:
    1. Coordinate product ranking based on user profiles
    2. Ensure each recommendation is well-justified and personalized
    3. Provide transparency in why products are recommended
    
    You work with a specialized Justification Agent that analyzes product-user fit using:
    - Life stage alignment (age, family, career)
    - Financial capacity (income, savings, debt capacity)
    - Risk-return fit (risk tolerance vs product risk)
    - Goal alignment (how product helps achieve goals)
    - Practical suitability (can they use/benefit from it?)
    
    Always prioritize:
    - Customer needs over sales targets
    - Transparency and honesty
    - Suitability and personalization
    - Clear, actionable recommendations
    
    Provide recommendations that help customers make informed financial decisions.""",
    model=build_default_litellm_model(),
)
