# 🚀 Quick Start Guide - Refactored Product Recommendation Agent

## ⚡ TL;DR

**What changed**: Heuristic scoring → AI-powered justification agent  
**Impact**: Better recommendations with explanations  
**Breaking changes**: None (backward compatible)

---

## 🏃 Quick Test

```bash
# 1. Ensure database is initialized
python init_database.py

# 2. Run test suite
python test_product_recommendation_refactor.py

# 3. Test in UI
streamlit run Homepage.py
# Navigate to page 2 (Product Recommendations)
```

---

## 📖 Key Files

| File | Purpose |
|------|---------|
| `src/agents/product_recommendation_agent.py` | **MAIN FILE** - Refactored agent |
| `test_product_recommendation_refactor.py` | Test suite |
| `PRODUCT_RECOMMENDATION_REFACTOR_README.md` | Detailed documentation |
| `REFACTORING_SUMMARY.md` | Executive summary |
| `AGENTS_ARCHITECTURE.md` | Updated architecture (Flow 1) |

---

## 🔍 What's New

### New Agent: Product Justification Expert
```python
product_justification_agent = Agent[ProductRecommendationContext](
    name="Product Justification Expert",
    instructions="Expert financial advisor analyzing product-customer fit..."
)
```

**Analyzes**:
- Life stage alignment
- Financial capacity
- Risk-return fit
- Goal alignment
- Practical suitability

**Returns**:
- Relevance score (0.0-1.0)
- Justification (WHY this score)
- Key benefits (user-specific)
- Recommended action (concrete next step)

---

## 💻 Usage (No Code Changes Needed!)

```python
# Same as before - backward compatible
from src.agents.product_recommendation_agent import (
    UserProfile,
    rank_products_for_profile,
)

profile = UserProfile(
    age=28,
    annual_income=65000,
    marital_status="married",
    risk_tolerance="medium",
    financial_goals=["savings", "investment"],
)

# Returns enhanced output (old fields + new fields)
ranked = rank_products_for_profile(profile.model_dump_json())

for product in ranked[:3]:
    print(f"{product['product_id']}: {product['score']}")
    print(f"  Why: {product['justification']}")  # NEW
    print(f"  Benefits: {product['key_benefits']}")  # NEW
    print(f"  Action: {product['recommended_action']}")  # NEW
```

---

## ⚙️ Configuration

Ensure `.env` has:
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
LITELLM_MODEL=bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0
```

---

## 🐛 Troubleshooting

### "No products in database"
```bash
python init_database.py
```

### "AWS authentication failed"
Check `.env` credentials

### Slow performance (>60s)
Normal for first run. Each product needs AI analysis (~3-5s per product).

**Future optimization**: Caching will reduce this to <1s after first run.

---

## 📈 Performance

| Metric | Old | New |
|--------|-----|-----|
| **Time** | ~1ms | ~30-60s |
| **Quality** | Basic | High |
| **Explainability** | None | Full |

**Why slower is acceptable**:
- Runs once per session (not per page load)
- User sees progress spinner
- Quality improvement is significant
- Will be cached in future

---

## ✅ Verification Checklist

Before considering done:

- [x] Code refactored
- [x] Tests pass
- [x] No breaking changes
- [x] Documentation updated
- [ ] **Manual UI test** (you should do this!)
- [ ] Performance acceptable in production
- [ ] User feedback collected

---

## 🎯 Next Steps

### For Developers
1. Run test suite: `python test_product_recommendation_refactor.py`
2. Test in UI: `streamlit run Homepage.py`
3. Review code: `src/agents/product_recommendation_agent.py`

### For Product Team
1. Test with real user profiles
2. Compare recommendations quality: old vs new
3. Collect user feedback on justifications

### For Future Sprints
1. Add caching mechanism
2. Implement batch processing
3. Display justifications in UI cards
4. Add user feedback buttons

---

## 📚 Documentation

- **Detailed Guide**: `PRODUCT_RECOMMENDATION_REFACTOR_README.md`
- **Summary**: `REFACTORING_SUMMARY.md`
- **Architecture**: `AGENTS_ARCHITECTURE.md` (Flow 1 updated)

---

## 🆘 Need Help?

1. Read detailed docs (see above)
2. Run tests to verify setup
3. Check troubleshooting section
4. Review code comments in agent file

---

**Last Updated**: November 2, 2025  
**Status**: ✅ Ready for testing
