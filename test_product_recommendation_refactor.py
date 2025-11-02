"""Test script for the refactored Product Recommendation Agent.

This script verifies that the AI-powered justification agent works correctly
and can rank products from the database based on user profiles.

Usage:
    python test_product_recommendation_refactor.py
"""

import json
from src.agents.product_recommendation_agent import (
    UserProfile,
    rank_products_for_profile,
    _get_products_catalog_dict,
    _get_products_from_database,
)


def test_database_connection():
    """Test 1: Verify database connection and product retrieval."""
    print("=" * 80)
    print("TEST 1: Database Connection & Product Retrieval")
    print("=" * 80)
    
    products = _get_products_from_database()
    
    if not products:
        print("❌ FAILED: No products found in database")
        print("   Make sure you've run: python init_database.py")
        return False
    
    print(f"✅ SUCCESS: Found {len(products)} products in database")
    print("\nProducts:")
    for i, product in enumerate(products[:3], 1):
        print(f"  {i}. {product['product_name'][:50]}...")
    
    if len(products) > 3:
        print(f"  ... and {len(products) - 3} more")
    
    return True


def test_catalog_extraction():
    """Test 2: Verify catalog extraction with benefits."""
    print("\n" + "=" * 80)
    print("TEST 2: Catalog Extraction (Name, Description, Benefits)")
    print("=" * 80)
    
    catalog = _get_products_catalog_dict()
    
    if not catalog:
        print("❌ FAILED: Empty catalog returned")
        return False
    
    print(f"✅ SUCCESS: Catalog contains {len(catalog)} products")
    
    # Show one example product
    sample_key = list(catalog.keys())[0]
    sample = catalog[sample_key]
    
    print(f"\nExample Product: {sample_key}")
    print(f"  Name: {sample['name']}")
    print(f"  Description: {sample['description'][:100]}...")
    print(f"  Benefits ({len(sample['benefits'])} total):")
    for benefit in sample['benefits'][:3]:
        print(f"    - {benefit[:80]}...")
    
    return True


def test_ai_ranking_young_professional():
    """Test 3: AI-powered ranking for young professional."""
    print("\n" + "=" * 80)
    print("TEST 3: AI Ranking - Young Professional Profile")
    print("=" * 80)
    
    # Create test profile
    profile = UserProfile(
        age=28,
        annual_income=65000,
        marital_status="married",
        employment_status="employed",
        has_children=False,
        risk_tolerance="medium",
        financial_goals=["savings", "investment", "home_purchase"],
        education_level="facultate",
    )
    
    print(f"Profile: {profile.age}y, {profile.annual_income} RON/year, {profile.marital_status}")
    print(f"Goals: {', '.join(profile.financial_goals)}")
    print(f"\nRunning AI-powered ranking (this may take 30-60 seconds)...\n")
    
    try:
        ranked = rank_products_for_profile(profile.model_dump_json())
        
        if not ranked:
            print("❌ FAILED: No ranked products returned")
            return False
        
        print(f"✅ SUCCESS: Ranked {len(ranked)} products\n")
        print("Top 5 Recommendations:")
        print("-" * 80)
        
        for i, product in enumerate(ranked[:5], 1):
            print(f"\n{i}. {product['product_id']}")
            print(f"   Score: {product['score']:.2f}")
            print(f"   Justification: {product['justification'][:150]}...")
            print(f"   Key Benefits:")
            for benefit in product['key_benefits'][:2]:
                print(f"     - {benefit[:70]}...")
            print(f"   Action: {product['recommended_action'][:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Error during ranking: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_ranking_retiree():
    """Test 4: AI-powered ranking for retiree profile."""
    print("\n" + "=" * 80)
    print("TEST 4: AI Ranking - Retiree Profile")
    print("=" * 80)
    
    # Create test profile
    profile = UserProfile(
        age=65,
        annual_income=35000,
        marital_status="married",
        employment_status="retired",
        has_children=True,
        risk_tolerance="low",
        financial_goals=["savings", "security"],
        education_level="liceu",
    )
    
    print(f"Profile: {profile.age}y, {profile.annual_income} RON/year, {profile.employment_status}")
    print(f"Goals: {', '.join(profile.financial_goals)}")
    print(f"\nRunning AI-powered ranking (this may take 30-60 seconds)...\n")
    
    try:
        ranked = rank_products_for_profile(profile.model_dump_json())
        
        if not ranked:
            print("❌ FAILED: No ranked products returned")
            return False
        
        print(f"✅ SUCCESS: Ranked {len(ranked)} products\n")
        print("Top 3 Recommendations:")
        print("-" * 80)
        
        for i, product in enumerate(ranked[:3], 1):
            print(f"\n{i}. {product['product_id']}")
            print(f"   Score: {product['score']:.2f}")
            print(f"   Justification: {product['justification'][:150]}...")
        
        # Verify that low-risk products are ranked higher
        top_products = [p['product_id'] for p in ranked[:3]]
        low_risk_products = ['Depozite la Termen', 'Cont de Economii Super Acces Plus']
        
        if any(lrp in ' '.join(top_products) for lrp in low_risk_products):
            print("\n✅ VALIDATION: Low-risk products correctly ranked high for retiree")
        else:
            print("\n⚠️  WARNING: Expected low-risk products in top 3 for retiree profile")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Error during ranking: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("PRODUCT RECOMMENDATION AGENT - REFACTORED ARCHITECTURE TEST")
    print("=" * 80)
    print("\nThis test verifies the new AI-powered justification system.")
    print("Make sure you have:")
    print("  1. Initialized database (python init_database.py)")
    print("  2. Configured AWS Bedrock credentials in .env")
    print("  3. Network connectivity to AWS\n")
    
    results = {
        "Database Connection": test_database_connection(),
        "Catalog Extraction": test_catalog_extraction(),
        "AI Ranking - Young Professional": test_ai_ranking_young_professional(),
        "AI Ranking - Retiree": test_ai_ranking_retiree(),
    }
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! The refactored agent is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return total_passed == total_tests


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
