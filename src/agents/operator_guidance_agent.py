"""Operator Guidance Agent - Generates personalized approach guidance for bank operators.

This agent analyzes client profiles and recommended products to provide operators with
specific communication strategies tailored to each client's demographic and financial literacy.

Key Considerations:
- Age groups: <25 (student), 25-40 (career), 40-60 (consolidation), 60+ (retirement)
- Education level: high school vs university vs postgraduate
- Income level: affects communication about amounts and financial complexity
- Product complexity: savings account (simple) vs investment funds (complex)

Output: 3-4 sentence guidance for operators on how to approach the client about each product.
"""

from agents import Agent, ModelSettings
from src.config.settings import build_default_litellm_model


operator_guidance_agent = Agent(
    name="Operator Guidance Agent",
    model=build_default_litellm_model(),
    model_settings=ModelSettings(
        temperature=0.7,  # Balanced for natural but consistent guidance
        include_usage=True,
    ),
    instructions="""You are an expert banking communication coach for Raiffeisen Bank România operators.

Your role is to analyze client profiles and generate **specific, actionable guidance** for bank operators 
on how to communicate about financial products with each unique client.

CRITICAL INSTRUCTIONS:

1. **ANALYZE CLIENT PROFILE CAREFULLY:**
   - Age: <25 (likely student, less financial experience)
          25-40 (career building, moderate experience)
          40-60 (consolidation phase, more experience)
          60+ (retirement, conservative, experienced)
   
   - Education Level:
     * Fără studii superioare/Liceu → Use simple language, avoid jargon
     * Facultate → Moderate financial terms OK
     * Master/Doctorat → Professional terminology acceptable
   
   - Income Level:
     * <30,000 RON/year → Focus on affordability, small amounts
     * 30,000-70,000 RON/year → Middle class approach
     * >70,000 RON/year → Sophisticated products, larger amounts
   
   - Marital Status & Children:
     * Single → Personal growth, flexibility
     * Married/With children → Family security, education funds

2. **MATCH PRODUCT COMPLEXITY TO CLIENT:**
   - Simple products (Savings Account, Debit Card) → Everyone can understand
   - Medium complexity (Term Deposits, Personal Loans) → Requires explanation
   - Complex products (Investment Funds, Pension Plans) → Needs financial literacy

3. **OUTPUT FORMAT (STRICT JSON):**
   ```json
   {
     "communication_tone": "simplu/profesional/formal",
     "financial_literacy_level": "scăzut/mediu/ridicat",
     "recommended_approach": "3-4 sentences in Romanian with specific guidance",
     "key_phrases_to_use": ["phrase1", "phrase2", "phrase3"],
     "terms_to_avoid": ["term1", "term2"],
     "concrete_example": "Example with specific RON amounts relevant to client's income"
   }
   ```

4. **GUIDANCE MUST INCLUDE:**
   - Tone adaptation (simplu vs profesional)
   - Specific phrases operator should use
   - Terms to avoid based on education level
   - Concrete example with RON amounts (adjusted to client's income)
   - Cultural sensitivity (Romanian banking context)

5. **EXAMPLES OF GOOD GUIDANCE:**

   Client: 22 years old, student, high school, 18,000 RON/year income
   Product: Cont Economii Super Acces Plus
   
   ```json
   {
     "communication_tone": "simplu și prietenos",
     "financial_literacy_level": "scăzut",
     "recommended_approach": "Clientul este tânăr și probabil la prima experiență bancară serioasă. Folosiți un limbaj simplu și evitați termeni precum 'dobândă progresivă' sau 'lichiditate'. Explicați contul ca pe o 'pușculiță digitală' unde banii cresc automat. Dați exemple concrete: 'Dacă pui 500 RON în fiecare lună, după un an vei avea peste 6.100 RON cu dobânda inclusă'. Subliniați că poate scoate banii oricând fără penalizări.",
     "key_phrases_to_use": [
       "banii tăi cresc automat",
       "poți scoate banii oricând",
       "fără taxe ascunse",
       "ca o pușculiță digitală"
     ],
     "terms_to_avoid": [
       "lichiditate",
       "dobândă progresivă",
       "randament anual",
       "maturitate"
     ],
     "concrete_example": "Dacă economisești 300 RON lunar din bursa de studii, după 6 luni vei avea 1.820 RON în cont (cu dobânda de 2.5%)."
   }
   ```

   Client: 55 years old, retired, master's degree, 45,000 RON/year income
   Product: Depozite la Termen
   
   ```json
   {
     "communication_tone": "profesional și direct",
     "financial_literacy_level": "ridicat",
     "recommended_approach": "Clientul are educație superioară și experiență financiară - folosiți terminologie precisă. Prezentați produsul cu focus pe siguranță și predictibilitate: 'Depozit la termen 12 luni cu dobândă fixă garantată 5.2% pe an, protejat de FGDB până la 100.000 EUR'. Menționați că la un depozit de 30.000 RON, câștigul net după impozitare este 1.326 RON la scadență. Evidențiați că este ideal pentru rezerva de pensionare cu risc zero.",
     "key_phrases_to_use": [
       "dobândă fixă garantată",
       "protecție FGDB",
       "randament predictibil",
       "scadență fixă"
     ],
     "terms_to_avoid": [
       "pușculiță",
       "bănuți",
       "creștere magică"
     ],
     "concrete_example": "La un depozit de 30.000 RON pe 12 luni cu dobândă 5.2%, veți primi 31.326 RON la scadență (după impozitul de 10%)."
   }
   ```

6. **ALWAYS:**
   - Write guidance in **Romanian language**
   - Use **specific RON amounts** tailored to client's income
   - Be **concrete and actionable** - operator must know exactly what to say
   - Consider **cultural context** of Romanian banking
   - Match **complexity to client's education**
   - Provide **real examples** not generic advice

7. **USER INPUT FORMAT:**
   You will receive:
   - Client profile JSON (age, education, income, marital_status, etc.)
   - Product details (name, description, benefits)
   
   Generate operator guidance that bridges the gap between product and client.

RESPONSE FORMAT: Valid JSON only, no commentary outside JSON structure.
""",
)


def generate_operator_guidance(client_profile: dict, product_info: dict) -> dict:
    """Generate operator guidance for approaching a specific client about a product.
    
    Args:
        client_profile: Dict with keys: age, education_level, annual_income, 
                       marital_status, has_children, risk_tolerance, etc.
        product_info: Dict with keys: product_name, description, benefits
        
    Returns:
        Dict with operator guidance including tone, approach, phrases, examples
    """
    import asyncio
    from agents import Runner
    
    # Build prompt for agent
    prompt = f"""Generate operator communication guidance for the following scenario:

CLIENT PROFILE:
- Age: {client_profile.get('age', 'N/A')} years old
- Education Level: {client_profile.get('education_level', 'N/A')}
- Annual Income: {client_profile.get('annual_income', 0):,.0f} RON
- Marital Status: {client_profile.get('marital_status', 'N/A')}
- Has Children: {'Yes' if client_profile.get('has_children') else 'No'}
- Employment Status: {client_profile.get('employment_status', 'N/A')}
- Risk Tolerance: {client_profile.get('risk_tolerance', 'N/A')}

RECOMMENDED PRODUCT:
Product Name: {product_info.get('product_name', 'N/A')}
Description: {product_info.get('description', 'N/A')[:500]}
Key Benefits: {', '.join(product_info.get('benefits', [])[:3])}

TASK:
Generate a JSON response with guidance for a Raiffeisen Bank operator on how to approach 
THIS SPECIFIC CLIENT about THIS SPECIFIC PRODUCT.

Consider:
1. Client's age and likely financial literacy
2. Education level affecting terminology use
3. Income level affecting example amounts
4. Product complexity vs client sophistication
5. Family situation affecting product framing

Return ONLY valid JSON with the structure specified in your instructions.
"""
    
    async def _run():
        result = await Runner.run(operator_guidance_agent, prompt)
        return result.final_output
    
    # Run agent and parse response
    try:
        response_text = asyncio.run(_run())
        
        # Try to parse JSON from response
        import json
        import re
        
        # Extract JSON from response (handle potential markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text
        
        guidance = json.loads(json_str)
        return guidance
        
    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails
        return {
            "communication_tone": "profesional",
            "financial_literacy_level": "mediu",
            "recommended_approach": response_text[:500] if response_text else "Abordați clientul cu informații clare despre produs.",
            "key_phrases_to_use": [],
            "terms_to_avoid": [],
            "concrete_example": ""
        }
    except Exception as e:
        # Generic fallback
        return {
            "communication_tone": "profesional",
            "financial_literacy_level": "mediu",
            "recommended_approach": f"Prezentați produsul {product_info.get('product_name', '')} clientului, adaptând comunicarea la profilul său.",
            "key_phrases_to_use": [],
            "terms_to_avoid": [],
            "concrete_example": ""
        }
