#!/usr/bin/env python3
"""
Test script to verify database products functionality.
"""

from src.utils.db import get_all_products, get_product_by_name

print("=" * 60)
print("Testing Products Database Integration")
print("=" * 60)

# Test 1: Get all products
print("\n1. Testing get_all_products():")
products = get_all_products()
print(f"   Found {len(products)} products")

for product in products:
    desc_preview = product['product_description'][:100].replace('\n', ' ')
    print(f"   - {product['product_name']} ({len(product['product_description'])} chars)")

# Test 2: Get specific product
print("\n2. Testing get_product_by_name():")
test_product_name = "Flexidepozit"
product = get_product_by_name(test_product_name)

if product:
    print(f"   ✓ Found product: {product['product_name']}")
    print(f"   Description length: {len(product['product_description'])} characters")
    print(f"   First 200 chars: {product['product_description'][:200]}...")
else:
    print(f"   ✗ Product '{test_product_name}' not found")

# Test 3: Get non-existent product
print("\n3. Testing non-existent product:")
product = get_product_by_name("NonExistentProduct")
if product is None:
    print("   ✓ Correctly returned None for non-existent product")
else:
    print("   ✗ Should have returned None")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
