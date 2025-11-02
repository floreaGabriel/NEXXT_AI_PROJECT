# Product Recommendation Agent - Refactored Architecture

## 📅 Date: November 2, 2025

## 🎯 Overview

This document describes the major refactoring of the Product Recommendation Agent from heuristic-based scoring to an **AI-powered justification system** using the OpenAI Agents SDK.

---

## 🔄 What Changed

### Before (Heuristic Approach)
```python
def _calculate_product_score_internal(product_id: str, profile: UserProfile) -> float:
    """Rule-based scoring with hardcoded conditions."""
    score = 0.5
    
    # Age-based scoring
    if profile.age >= 40 and product_id == "pensie_privata_pilon3":
        score += 0.2
    
    # Risk tolerance
    if profile.risk_tolerance == "low" and product_id == "depozite_termen":
        score += 0.2
    
    # ... more hardcoded rules
    return score
```

**Problems:**
- ❌ Rigid rules that don't adapt to complex scenarios
- ❌ Limited personalization (binary conditions)
- ❌ Requires manual updates for new products/rules
- ❌ Can't explain WHY a product is recommended
- ❌ No use of actual product descriptions

### After (AI-Powered Approach)
```python
# 1. Product Justification Agent (Tool Agent)
product_justification_agent = Agent[ProductRecommendationContext](
    name="Product Justification Expert",
    instructions="""You are an expert financial advisor analyzing product-customer fit.
    
    Consider:
    1. Life Stage Alignment: Age, family, career
    2. Financial Capacity: Income, savings, debt capacity
    3. Risk-Return Fit: Risk tolerance vs product risk
    4. Goal Alignment: How product helps achieve goals
    5. Practical Suitability: Can they realistically use/benefit?
    
    Output: JSON with relevance_score (0.0-1.0), justification, key_benefits, recommended_action
    """,
    model=build_default_litellm_model(),
)

# 2. Main ranking function uses this agent for each product
def rank_products_for_profile(user_profile_json: str) -> list[dict]:
    """Rank products using AI-powered justification."""
    profile = UserProfile.model_validate_json(user_profile_json)
    db_products = _get_products_from_database()  # From PostgreSQL
    
    scored_products = []
    for product in db_products:
        # Call AI agent to analyze fit
        justification = _analyze_product_fit_sync(
            product_name=product["product_name"],
            product_description=product["product_description"],
            user_profile=profile
        )
        
        scored_products.append({
            "product_id": product["product_name"],
            "score": justification.relevance_score,
            "justification": justification.justification,
            "key_benefits": justification.key_benefits,
            "recommended_action": justification.recommended_action,
        })
    
    scored_products.sort(key=lambda x: x["score"], reverse=True)
    return scored_products
```

**Benefits:**
- ✅ **Intelligent Analysis**: Claude 3.5 Sonnet analyzes product-user fit holistically
- ✅ **Explainable**: Every score includes a 2-3 sentence justification
- ✅ **Personalized Benefits**: Extracts relevant benefits for THIS user (not generic)
- ✅ **Actionable Recommendations**: Provides concrete next steps
- ✅ **Database Integration**: Uses real product data from PostgreSQL
- ✅ **Scalable**: No code changes needed for new products
- ✅ **Contextual**: Reads full product descriptions (not just metadata)

---

## 🏗️ New Architecture

### Components

#### 1. Product Justification Agent (AI Tool)
**File**: `src/agents/product_recommendation_agent.py`

**Type**: Agent tool (can be used as a tool by other agents)

**Inputs**:
- `product_name`: Name of the banking product
- `product_description`: Full markdown description from database
- `user_profile`: Complete UserProfile object

**Outputs** (JSON):
```json
{
  "product_name": "Cont de Economii Super Acces Plus",
  "relevance_score": 0.85,
  "justification": "Perfect fit for building emergency fund at age 28 with 65K income. Recommend 20K RON (3 months expenses) for flexibility and security.",
  "key_benefits": [
    "Instant access to money",
    "3% interest on balances >50K RON",
    "SavingBox automatic savings feature",
    "Zero administration fees",
    "Daily interest calculation"
  ],
  "recommended_action": "Open account with 20,000 RON initial deposit. Enable SavingBox at 3% for automatic savings."
}
```

**Scoring Guidelines**:
- **0.9-1.0**: Perfect fit, highly recommended
- **0.7-0.89**: Good fit, recommended
- **0.5-0.69**: Moderate fit, consider with other options
- **0.3-0.49**: Weak fit, not priority
- **0.0-0.29**: Poor fit, not suitable

#### 2. Database Integration
**File**: `src/utils/db.py`

**New Functions Used**:
- `get_all_products()`: Fetch all products from PostgreSQL
- Products stored with full markdown descriptions
- Real-time data (no hardcoded catalogs)

**Product Table Schema**:
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_name TEXT UNIQUE NOT NULL,
    product_description TEXT NOT NULL,  -- Full markdown content
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

#### 3. Helper Functions
**Markdown Parsing**:
- `_extract_product_summary()`: Extracts concise summary from markdown
- `_extract_product_benefits()`: Extracts key benefits from "Avantaje" section
- `_get_products_catalog_dict()`: Backward-compatible catalog for UI

**Synchronous Wrapper**:
- `_analyze_product_fit_sync()`: Wraps async agent call for sync usage
- Handles errors gracefully (returns neutral score on failure)
- Parses JSON output from LLM

---

## 📊 Comparison: Old vs New

| Aspect | Old (Heuristic) | New (AI-Powered) |
|--------|----------------|------------------|
| **Scoring Method** | Hardcoded if-else rules | Claude 3.5 Sonnet analysis |
| **Product Data** | Hardcoded dict in code | PostgreSQL database |
| **Personalization** | Basic (age, income buckets) | Deep (considers all profile aspects) |
| **Explainability** | None (just a score) | Full justification + benefits |
| **Scalability** | Requires code changes | Auto-adapts to new products |
| **Maintenance** | Manual rule updates | Self-maintaining |
| **Recommendations** | Generic | Specific (amounts, timeframes) |
| **Performance** | ~1ms per product | ~3-5s per product (LLM call) |

**Performance Note**: While the AI approach is slower (3-5 seconds per product), it's acceptable because:
1. Ranking happens once per user session (not per page load)
2. Users see "Analyzing..." spinner with clear feedback
3. Quality of recommendations is significantly higher
4. Can be optimized with caching or batch processing

---

## 🔧 Integration with Streamlit

### No Breaking Changes
The refactored agent maintains **backward compatibility** with the existing Streamlit page:

```python
# pages/2_Product_Recommendations_Florea.py (NO CHANGES NEEDED)

from src.agents.product_recommendation_agent import (
    UserProfile,
    rank_products_for_profile,  # ✅ Same function signature
    _get_products_catalog_dict,  # ✅ Still available for UI
)

# Usage remains identical
ranked_products = rank_products_for_profile(user_profile.model_dump_json())

# Output structure enhanced (but backward compatible):
# Old: [{"product_id": "...", "score": 0.85}]
# New: [{"product_id": "...", "score": 0.85, "justification": "...", "key_benefits": [...], "recommended_action": "..."}]
```

### Enhanced Display
The Streamlit page can now display:
1. **Score**: Relevance score (0.0-1.0)
2. **Justification**: AI-generated explanation (NEW)
3. **Key Benefits**: Personalized benefit list (NEW)
4. **Recommended Action**: Concrete next step (NEW)

---

## 🧪 Testing

### Test Script
Run the comprehensive test suite:
```bash
python test_product_recommendation_refactor.py
```

**Tests Included**:
1. ✅ Database connection & product retrieval
2. ✅ Catalog extraction (name, description, benefits)
3. ✅ AI ranking for young professional profile
4. ✅ AI ranking for retiree profile (validates low-risk products ranked high)

### Manual Testing
1. **Start the app**:
   ```bash
   streamlit run Homepage.py
   ```

2. **Navigate to Product Recommendations** (page 2)

3. **Fill in user profile**:
   - Age: 28
   - Income: 65,000 RON
   - Marital Status: Married
   - Risk Tolerance: Medium
   - Goals: Savings, Investment, Home Purchase

4. **Click "Obține Recomandări"**

5. **Expected Output**:
   - Spinner: "Analizăm profilul..." (30-60 seconds)
   - Top products with scores
   - Each product shows AI-generated justification
   - Benefits relevant to the user profile
   - Recommended actions with concrete amounts

---

## 📝 Example Output

### User Profile
```json
{
  "age": 28,
  "annual_income": 65000,
  "marital_status": "married",
  "employment_status": "employed",
  "has_children": false,
  "risk_tolerance": "medium",
  "financial_goals": ["savings", "investment", "home_purchase"],
  "education_level": "facultate"
}
```

### AI-Generated Rankings

**#1: Cont de Economii Super Acces Plus (Score: 0.88)**
- **Justification**: "At 28 years old with stable employment and 65K annual income (5,416 RON/month), this is perfect for building your emergency fund. With marriage and home purchase goals, you need 16,000-20,000 RON (3 months expenses) readily accessible. The progressive interest rate (up to 3%) and SavingBox feature align perfectly with your medium risk tolerance and savings goals."
- **Key Benefits**:
  - Instant access without penalties (critical for emergencies)
  - 3% interest on balances over 50K RON
  - SavingBox automatic savings (3-5% of card purchases)
  - Zero administration fees
  - Daily interest calculation with monthly capitalization
- **Recommended Action**: "Open with 15,000 RON initial deposit. Enable SavingBox at 3% to automatically save 150-200 RON monthly from your card purchases."

**#2: Credit Ipotecar Casa Ta (Score: 0.82)**
- **Justification**: "Your age (28) and income (65K) position you perfectly for home ownership. Combined household income likely supports a 150K-200K EUR mortgage (monthly payment ~2,500 RON = 40% of income). The home purchase goal is explicit, and starting now benefits from 30-year repayment period."
- **Key Benefits**:
  - 30-year repayment period (manageable monthly payments)
  - Fixed interest for first 3-5 years (predictability)
  - Minimum 15% down payment required
  - Noua Casă program eligible (5-15% down, 2% interest)
  - 2,000 RON refinancing bonus
- **Recommended Action**: "Start saving 25,000-30,000 EUR (15% down payment) over next 12-18 months. Calculate affordability: max 2,500 RON/month payment = ~150,000 EUR loan."

**#3: Planuri de Investiții SmartInvest (Score: 0.75)**
- **Justification**: "Your medium risk tolerance, investment goal, and long time horizon (40+ years to retirement) make systematic investing ideal. Monthly contributions of 1,000 RON (15% of income) compound significantly over time while maintaining liquidity for home purchase in 2-3 years."
- **Key Benefits**:
  - Automatic monthly investing from 200 RON (removes emotional decisions)
  - Mixed funds suitable for medium risk tolerance
  - Professional portfolio management
  - Tax advantages (1% tax for holdings >365 days vs 3%)
  - 100% online administration via Smart Mobile
- **Recommended Action**: "Begin with 500 RON/month in mixed funds (60% bonds, 40% stocks). Increase to 1,000 RON/month after emergency fund is built."

---

## 🚀 Future Enhancements

### Short Term (2-4 weeks)
1. **Caching**: Cache agent results for 24h to reduce LLM calls
2. **Batch Processing**: Analyze multiple products in parallel
3. **UI Enhancement**: Display justifications in Streamlit cards
4. **Logging**: Track agent decisions for analytics

### Medium Term (1-3 months)
1. **A/B Testing**: Compare AI rankings vs heuristic rankings
2. **User Feedback**: Allow users to rate recommendations
3. **Fine-tuning**: Use feedback to improve agent instructions
4. **Multi-language**: Support English justifications

### Long Term (3-6 months)
1. **RAG Integration**: Vector search over product catalog
2. **Collaborative Filtering**: Learn from similar user preferences
3. **Real-time Updates**: Re-rank when market conditions change
4. **Conversational Agent**: Chat interface to explore recommendations

---

## 🔍 Troubleshooting

### Error: "No products found in database"
**Solution**: Initialize the database first:
```bash
python init_database.py
```

### Error: "AWS Bedrock authentication failed"
**Solution**: Check your `.env` file:
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
LITELLM_MODEL=bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0
```

### Slow Performance (>60s per ranking)
**Causes**:
- Network latency to AWS
- Many products in database (each requires LLM call)

**Solutions**:
1. Use caching (implement in future)
2. Reduce number of products analyzed (top 10 only)
3. Use batch processing (analyze multiple products per call)

### JSON Parsing Errors
**Cause**: LLM sometimes returns malformed JSON

**Solution**: The code has fallback handling:
```python
try:
    parsed = json.loads(output)
    return ProductJustification(**parsed)
except:
    return ProductJustification(
        product_name=product_name,
        relevance_score=0.5,  # Neutral score
        justification="Could not generate detailed analysis",
        key_benefits=["Please review product details"],
        recommended_action="Contact advisor"
    )
```

---

## 📚 References

- **OpenAI Agents SDK**: Documentation for Agent creation and tool usage
- **LiteLLM**: Unified interface for multiple LLM providers (used for Bedrock)
- **Pydantic**: Data validation for agent inputs/outputs
- **PostgreSQL**: Product catalog storage

---

## 👥 Authors

**Refactoring Date**: November 2, 2025  
**Original Architecture**: See `AGENTS_ARCHITECTURE.md`  
**Project**: NEXXT AI Banking Assistant - Raiffeisen Bank România

---

## ✅ Checklist

Before deploying to production:

- [x] Refactor agent code
- [x] Add database integration
- [x] Create AI justification agent
- [x] Test with sample profiles
- [ ] Add caching mechanism
- [ ] Monitor LLM costs
- [ ] Add user feedback collection
- [ ] Performance optimization
- [ ] Load testing (100+ concurrent users)
- [ ] Security audit (user data handling)
