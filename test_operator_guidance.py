"""Test script for Operator Guidance Agent.

Quick validation that the agent generates relevant guidance for different client profiles.
"""

from src.agents.operator_guidance_agent import generate_operator_guidance

# Test Case 1: Young student with low financial literacy
print("=" * 80)
print("TEST 1: Young Student (22, high school, 18K income)")
print("=" * 80)

client_profile_1 = {
    "age": 22,
    "education_level": "liceu",
    "annual_income": 18000,
    "marital_status": "necăsătorit/ă",
    "has_children": False,
    "employment_status": "student",
    "risk_tolerance": "scăzută",
}

product_info_1 = {
    "product_name": "Cont de Economii Super Acces Plus",
    "description": "Cont de economii cu acces instant la bani, dobândă progresivă 2-3% și funcție SavingBox pentru economisire automată.",
    "benefits": ["Acces instant la bani", "Dobândă progresivă", "SavingBox economisire automată"],
}

guidance_1 = generate_operator_guidance(client_profile_1, product_info_1)
print(f"\nCommunication Tone: {guidance_1.get('communication_tone')}")
print(f"Financial Literacy: {guidance_1.get('financial_literacy_level')}")
print(f"\nRecommended Approach:\n{guidance_1.get('recommended_approach')}")
print(f"\nKey Phrases: {guidance_1.get('key_phrases_to_use')}")
print(f"Terms to Avoid: {guidance_1.get('terms_to_avoid')}")
print(f"\nConcrete Example:\n{guidance_1.get('concrete_example')}")

# Test Case 2: Mature professional with high financial literacy
print("\n\n" + "=" * 80)
print("TEST 2: Mature Professional (55, master's, 80K income, married)")
print("=" * 80)

client_profile_2 = {
    "age": 55,
    "education_level": "master",
    "annual_income": 80000,
    "marital_status": "căsătorit/ă",
    "has_children": True,
    "employment_status": "angajat",
    "risk_tolerance": "medie",
}

product_info_2 = {
    "product_name": "Fonduri de Investiții SmartInvest",
    "description": "Investiții profesionale în fonduri mutuale cu gestiune activă, diversificare automată și depuneri lunare flexibile de la 200 RON.",
    "benefits": ["Gestiune profesională", "Diversificare automată", "Depuneri lunare flexibile"],
}

guidance_2 = generate_operator_guidance(client_profile_2, product_info_2)
print(f"\nCommunication Tone: {guidance_2.get('communication_tone')}")
print(f"Financial Literacy: {guidance_2.get('financial_literacy_level')}")
print(f"\nRecommended Approach:\n{guidance_2.get('recommended_approach')}")
print(f"\nKey Phrases: {guidance_2.get('key_phrases_to_use')}")
print(f"Terms to Avoid: {guidance_2.get('terms_to_avoid')}")
print(f"\nConcrete Example:\n{guidance_2.get('concrete_example')}")

print("\n\n" + "=" * 80)
print("✅ Test completed! Check if guidance is relevant and actionable.")
print("=" * 80)
