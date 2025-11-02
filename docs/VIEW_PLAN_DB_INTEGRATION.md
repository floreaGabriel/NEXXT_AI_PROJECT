"""
Database Integration Guide for View Plan Page
==============================================

This document explains how to replace mock data with real database queries
in the View Plan page (5_View_Plan.py).

Current Status:
--------------
The page currently uses mock data in the `get_user_financial_plan()` function.
This allows the page to work immediately without database dependency.

Database Schema Required:
------------------------
The `users` table already has the necessary columns:
- email (TEXT, unique)
- user_plan (TEXT) - stores the financial plan markdown
- All user profile fields (age, marital_status, annual_income, etc.)

Integration Steps:
-----------------

1. REPLACE MOCK DATA FUNCTION:

In file: pages/5_View_Plan.py

Current mock function (lines ~50-140):
```python
def get_user_financial_plan(email: str) -> dict:
    # MOCK DATA - Replace this entire function with DB query
    mock_user_profile = {...}
    mock_plan = "..."
    return {
        "plan_text": mock_plan,
        "user_profile": mock_user_profile,
        "products": [...]
    }
```

Replace with:
```python
def get_user_financial_plan(email: str) -> dict:
    \"\"\"
    Get user's financial plan from database.
    
    Args:
        email: User email
    
    Returns:
        Dictionary with plan_text, user_profile, and products
    \"\"\"
    from src.utils.db import get_user_by_email
    
    # Fetch user data from database
    user_data = get_user_by_email(email)
    
    if not user_data:
        raise ValueError(f"User not found: {email}")
    
    # Extract plan text
    plan_text = user_data.get("user_plan")
    
    if not plan_text:
        return {
            "plan_text": None,
            "user_profile": None,
            "products": []
        }
    
    # Build user profile from database fields
    user_profile = {
        "email": user_data.get("email"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "age": user_data.get("age"),
        "marital_status": user_data.get("marital_status"),
        "annual_income": user_data.get("extra", {}).get("annual_income", 50000.0),
        "employment_status": user_data.get("employment_status"),
        "has_children": user_data.get("has_children", False),
        "number_of_children": user_data.get("number_of_children", 0),
        "risk_tolerance": user_data.get("extra", {}).get("risk_tolerance", "Medie"),
        "education_level": user_data.get("extra", {}).get("education_level", "Facultate"),
        "financial_goals": user_data.get("extra", {}).get("financial_goals", []),
    }
    
    # Extract products from plan text (parse ### 3.X sections)
    import re
    product_matches = re.findall(r'### 3\.\d+ (.+)', plan_text)
    products = product_matches if product_matches else []
    
    return {
        "plan_text": plan_text,
        "user_profile": user_profile,
        "products": products
    }
```

2. UPDATE DATABASE SCHEMA (if needed):

If additional fields need to be stored in the `extra` JSONB column:
- annual_income
- risk_tolerance
- education_level
- financial_goals

These are already handled by the `upsert_user()` function in src/utils/db.py.

3. ENSURE PLAN IS SAVED:

In file: pages/2_Product_Recommendations_Florea.py

After generating the financial plan, ensure it's saved to database:

```python
from src.utils.db import save_financial_plan

# After generating plan
plan_text = generate_financial_plan(user_profile, selected_products)

# Save to database
user_email = st.session_state["auth"]["email"]
success = save_financial_plan(user_email, plan_text)

if success:
    st.success("Plan saved successfully!")
else:
    st.error("Failed to save plan to database")
```

4. TESTING THE INTEGRATION:

a) Test with mock data first (current implementation works)
b) Set up database connection:
   - Ensure .env has correct DB credentials
   - Run: src/utils/db.py init_users_table()
c) Generate a plan through page 2_Product_Recommendations_Florea.py
d) Navigate to page 5_View_Plan.py
e) Verify plan loads correctly

5. ERROR HANDLING:

The page already handles missing plans gracefully:
```python
if not plan_text:
    st.warning("Nu aveți încă un plan financiar generat...")
    st.stop()
```

6. ADDITIONAL ENHANCEMENTS:

Consider adding:
- Plan version history (create `user_plans` table with history)
- Last updated timestamp display
- Plan regeneration button
- Comparison with previous plans

Database Schema Enhancement (Optional):
--------------------------------------

For better plan management, consider creating a dedicated table:

```sql
CREATE TABLE user_financial_plans (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL REFERENCES users(email),
    plan_text TEXT NOT NULL,
    products JSONB,
    statistics JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    version INT DEFAULT 1
);

CREATE INDEX idx_user_plans_email ON user_financial_plans(user_email);
CREATE INDEX idx_user_plans_created ON user_financial_plans(created_at DESC);
```

This allows:
- Multiple plan versions per user
- Separate storage of statistics
- Better querying and history tracking

Migration Steps:
---------------
1. Test current mock implementation
2. Verify database connection works
3. Replace mock function with DB query
4. Test with real data
5. Deploy to production

Notes:
------
- Mock data remains in code comments for testing/reference
- Database connection errors are handled gracefully
- User experience remains smooth with or without DB
- Statistics are computed dynamically from plan text
"""
