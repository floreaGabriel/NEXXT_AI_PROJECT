"""Plan Analytics Module - Deterministic analysis functions for financial plans.

This module provides rational, justified calculations based on:
- User profile characteristics
- Financial plan content
- Product features and timelines
- Historical financial data patterns

All functions are deterministic and mathematically justified - no hallucinations.
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime
from dateutil.relativedelta import relativedelta


def extract_plan_metrics(plan_text: str, user_profile: dict) -> Dict:
    """
    Extract quantifiable metrics from the financial plan text.
    
    Args:
        plan_text: The full financial plan markdown text
        user_profile: User profile dictionary
    
    Returns:
        Dictionary with extracted metrics
    """
    metrics = {
        "total_products": 0,
        "short_term_goals": [],
        "medium_term_goals": [],
        "long_term_goals": [],
        "monthly_income": user_profile.get("annual_income", 0) / 12,
        "annual_income": user_profile.get("annual_income", 0),
        "age": user_profile.get("age", 30),
        "has_children": user_profile.get("has_children", False),
        "risk_level": user_profile.get("risk_tolerance", "medie"),
    }
    
    # Count products mentioned (look for "### 3." pattern)
    product_sections = re.findall(r'### 3\.\d+', plan_text)
    metrics["total_products"] = len(product_sections)
    
    # Extract goals from the objectives section
    goals_section = re.search(r'\*\*Obiective Financiare:\*\*(.*?)(?=\n##|\Z)', plan_text, re.DOTALL)
    if goals_section:
        goals_text = goals_section.group(1)
        
        # Short term (1-3 years)
        short_match = re.search(r'termen scurt.*?:(.*?)(?=termen mediu|\Z)', goals_text, re.DOTALL | re.IGNORECASE)
        if short_match:
            metrics["short_term_goals"] = [g.strip('- \n') for g in short_match.group(1).split('\n') if g.strip('- \n')]
        
        # Medium term (3-7 years)
        medium_match = re.search(r'termen mediu.*?:(.*?)(?=termen lung|\Z)', goals_text, re.DOTALL | re.IGNORECASE)
        if medium_match:
            metrics["medium_term_goals"] = [g.strip('- \n') for g in medium_match.group(1).split('\n') if g.strip('- \n')]
        
        # Long term (7+ years)
        long_match = re.search(r'termen lung.*?:(.*?)(?=\n##|\Z)', goals_text, re.DOTALL | re.IGNORECASE)
        if long_match:
            metrics["long_term_goals"] = [g.strip('- \n') for g in long_match.group(1).split('\n') if g.strip('- \n')]
    
    return metrics


def calculate_savings_capacity(user_profile: dict) -> Dict:
    """
    Calculate realistic savings capacity based on income and expenses.
    Uses standard Romanian household expense ratios.
    
    Args:
        user_profile: User profile with income and family data
    
    Returns:
        Dictionary with savings calculations
    """
    annual_income = user_profile.get("annual_income", 50000)
    monthly_income = annual_income / 12
    age = user_profile.get("age", 35)
    has_children = user_profile.get("has_children", False)
    num_children = user_profile.get("number_of_children", 0)
    marital_status = user_profile.get("marital_status", "necăsătorit/ă")
    
    # Base expense ratio (housing, utilities, food, transport)
    base_expense_ratio = 0.60  # 60% of income for basic needs
    
    # Adjustments based on profile
    if marital_status.lower() in ["căsătorit/ă", "casatorit/a"]:
        base_expense_ratio -= 0.05  # Married couples have economies of scale
    
    if has_children and num_children > 0:
        base_expense_ratio += (0.10 * num_children)  # +10% per child
    
    if age > 50:
        base_expense_ratio += 0.05  # Higher healthcare costs
    
    # Cap expense ratio at 85%
    base_expense_ratio = min(base_expense_ratio, 0.85)
    
    # Calculate savings
    monthly_expenses = monthly_income * base_expense_ratio
    monthly_savings_potential = monthly_income - monthly_expenses
    annual_savings_potential = monthly_savings_potential * 12
    
    # Recommended savings allocation
    emergency_fund_target = monthly_expenses * 6  # 6 months of expenses
    
    return {
        "monthly_income": round(monthly_income, 2),
        "monthly_expenses": round(monthly_expenses, 2),
        "monthly_savings_potential": round(monthly_savings_potential, 2),
        "annual_savings_potential": round(annual_savings_potential, 2),
        "expense_ratio": round(base_expense_ratio * 100, 1),
        "savings_ratio": round((1 - base_expense_ratio) * 100, 1),
        "emergency_fund_target": round(emergency_fund_target, 2),
        "months_to_emergency_fund": round(emergency_fund_target / monthly_savings_potential, 1) if monthly_savings_potential > 0 else 0,
    }


def calculate_investment_projections(
    initial_amount: float,
    monthly_contribution: float,
    annual_return_rate: float,
    years: int
) -> List[Dict]:
    """
    Calculate year-by-year investment growth projections.
    
    Args:
        initial_amount: Starting investment amount
        monthly_contribution: Monthly contribution
        annual_return_rate: Expected annual return (e.g., 0.05 for 5%)
        years: Number of years to project
    
    Returns:
        List of yearly projections with breakdown
    """
    projections = []
    current_balance = initial_amount
    total_contributions = initial_amount
    
    for year in range(1, years + 1):
        # Add monthly contributions
        yearly_contributions = monthly_contribution * 12
        total_contributions += yearly_contributions
        current_balance += yearly_contributions
        
        # Apply annual return
        yearly_return = current_balance * annual_return_rate
        current_balance += yearly_return
        
        projections.append({
            "year": year,
            "balance": round(current_balance, 2),
            "total_contributions": round(total_contributions, 2),
            "total_returns": round(current_balance - total_contributions, 2),
            "yearly_return": round(yearly_return, 2),
        })
    
    return projections


def estimate_product_returns(user_profile: dict, products: List[str]) -> Dict:
    """
    Estimate realistic returns based on product types and user risk profile.
    Uses conservative estimates based on historical Romanian market data.
    
    Args:
        user_profile: User profile dictionary
        products: List of product names/IDs
    
    Returns:
        Dictionary with estimated returns per product category
    """
    risk_level = user_profile.get("risk_tolerance", "medie").lower()
    
    # Conservative return estimates (annual %)
    return_estimates = {
        "cont_economii": {
            "scăzută": 0.02,    # 2% - savings account
            "medie": 0.025,     # 2.5%
            "ridicată": 0.03    # 3%
        },
        "depozit": {
            "scăzută": 0.04,    # 4% - fixed deposit
            "medie": 0.045,     # 4.5%
            "ridicată": 0.05    # 5%
        },
        "fond_investitii": {
            "scăzută": 0.05,    # 5% - conservative fund
            "medie": 0.07,      # 7% - balanced fund
            "ridicată": 0.09    # 9% - growth fund
        },
        "pensie_privata": {
            "scăzută": 0.04,    # 4% - conservative pension
            "medie": 0.06,      # 6% - balanced pension
            "ridicată": 0.08    # 8% - aggressive pension
        },
        "titluri_venit_fix": {
            "scăzută": 0.045,   # 4.5% - bonds
            "medie": 0.05,      # 5%
            "ridicată": 0.055   # 5.5%
        },
    }
    
    estimated_returns = {}
    for product in products:
        # Match product to category
        product_lower = product.lower()
        if "economii" in product_lower or "savings" in product_lower:
            category = "cont_economii"
        elif "depozit" in product_lower or "deposit" in product_lower:
            category = "depozit"
        elif "fond" in product_lower or "invest" in product_lower:
            category = "fond_investitii"
        elif "pensie" in product_lower or "pension" in product_lower:
            category = "pensie_privata"
        elif "titlu" in product_lower or "bond" in product_lower:
            category = "titluri_venit_fix"
        else:
            category = "cont_economii"  # Default
        
        estimated_returns[product] = {
            "annual_return_rate": return_estimates[category].get(risk_level, return_estimates[category]["medie"]),
            "category": category,
            "risk_adjusted": True
        }
    
    return estimated_returns


def calculate_goal_timeline(user_profile: dict, goal: str) -> Dict:
    """
    Calculate realistic timeline for achieving specific financial goals.
    
    Args:
        user_profile: User profile dictionary
        goal: Financial goal name
    
    Returns:
        Dictionary with timeline and milestones
    """
    savings_capacity = calculate_savings_capacity(user_profile)
    monthly_savings = savings_capacity["monthly_savings_potential"]
    age = user_profile.get("age", 35)
    
    # Goal estimates (conservative amounts in RON)
    goal_amounts = {
        "economii pe termen scurt": 15000,
        "economii pe termen lung": 100000,
        "investiții": 50000,
        "cumpărare casă": 150000,  # Down payment (30% of 500K)
        "cumpărare locuință": 150000,
        "educație copii": 80000,  # University costs
        "pensionare": 500000,  # Retirement fund
        "călătorii": 20000,
        "achiziții mari": 30000,
        "fond urgență": savings_capacity["emergency_fund_target"],
    }
    
    # Find matching goal
    goal_lower = goal.lower()
    target_amount = 50000  # Default
    
    for key, amount in goal_amounts.items():
        if key in goal_lower:
            target_amount = amount
            break
    
    # Calculate timeline
    if monthly_savings > 0:
        # Assuming 5% annual return on savings
        months_needed = calculate_months_to_goal(target_amount, monthly_savings, 0.05)
        years_needed = months_needed / 12
    else:
        months_needed = 0
        years_needed = 0
    
    # Create milestones
    milestones = []
    if years_needed > 0:
        milestone_intervals = [0.25, 0.5, 0.75, 1.0]  # 25%, 50%, 75%, 100%
        for interval in milestone_intervals:
            milestone_months = int(months_needed * interval)
            milestone_date = datetime.now() + relativedelta(months=milestone_months)
            milestones.append({
                "percentage": int(interval * 100),
                "amount": round(target_amount * interval, 2),
                "date": milestone_date.strftime("%B %Y"),
                "months_from_now": milestone_months,
            })
    
    return {
        "goal": goal,
        "target_amount": round(target_amount, 2),
        "monthly_contribution": round(monthly_savings, 2),
        "months_needed": round(months_needed, 1),
        "years_needed": round(years_needed, 1),
        "estimated_completion": (datetime.now() + relativedelta(months=int(months_needed))).strftime("%B %Y") if months_needed > 0 else "N/A",
        "milestones": milestones,
        "feasibility": "realistic" if years_needed < 10 else "long-term" if years_needed < 20 else "ambitious",
    }


def calculate_months_to_goal(target: float, monthly_contribution: float, annual_return: float) -> float:
    """
    Calculate months needed to reach a goal with compound interest.
    
    Args:
        target: Target amount
        monthly_contribution: Monthly contribution
        annual_return: Annual return rate (e.g., 0.05 for 5%)
    
    Returns:
        Number of months needed
    """
    if monthly_contribution <= 0:
        return float('inf')
    
    if annual_return <= 0:
        # Simple division without interest
        return target / monthly_contribution
    
    # Monthly interest rate
    monthly_rate = annual_return / 12
    
    # Future value of annuity formula solved for n (periods)
    # FV = PMT * ((1 + r)^n - 1) / r
    # Solving for n when FV = target
    import math
    
    try:
        if monthly_rate == 0:
            return target / monthly_contribution
        
        numerator = math.log(1 + (target * monthly_rate) / monthly_contribution)
        denominator = math.log(1 + monthly_rate)
        months = numerator / denominator
        
        return max(1, months)  # At least 1 month
    except:
        # Fallback to simple calculation
        return target / monthly_contribution


def calculate_wealth_projection(user_profile: dict, years: int = 10) -> Dict:
    """
    Project wealth growth over time based on profile and savings.
    
    Args:
        user_profile: User profile dictionary
        years: Number of years to project
    
    Returns:
        Dictionary with wealth projection data
    """
    savings_capacity = calculate_savings_capacity(user_profile)
    monthly_savings = savings_capacity["monthly_savings_potential"]
    risk_level = user_profile.get("risk_tolerance", "medie").lower()
    
    # Conservative return rates based on risk
    return_rates = {
        "scăzută": 0.04,   # 4% conservative
        "medie": 0.06,     # 6% balanced
        "ridicată": 0.08,  # 8% growth
    }
    
    annual_return = return_rates.get(risk_level, 0.06)
    
    # Calculate projections
    projections = calculate_investment_projections(
        initial_amount=0,  # Starting from zero
        monthly_contribution=monthly_savings,
        annual_return_rate=annual_return,
        years=years
    )
    
    # Calculate key metrics
    final_balance = projections[-1]["balance"] if projections else 0
    total_contributions = projections[-1]["total_contributions"] if projections else 0
    total_returns = final_balance - total_contributions
    
    return {
        "projections": projections,
        "summary": {
            "years": years,
            "monthly_contribution": round(monthly_savings, 2),
            "annual_return_rate": round(annual_return * 100, 1),
            "final_balance": round(final_balance, 2),
            "total_contributions": round(total_contributions, 2),
            "total_returns": round(total_returns, 2),
            "roi_percentage": round((total_returns / total_contributions * 100), 1) if total_contributions > 0 else 0,
        }
    }


def analyze_plan_risk_return(user_profile: dict, products: List[str]) -> Dict:
    """
    Analyze the risk-return profile of the financial plan.
    
    Args:
        user_profile: User profile dictionary
        products: List of products in the plan
    
    Returns:
        Dictionary with risk-return analysis
    """
    product_returns = estimate_product_returns(user_profile, products)
    
    # Calculate weighted average return
    total_return = sum(p["annual_return_rate"] for p in product_returns.values())
    avg_return = total_return / len(product_returns) if product_returns else 0
    
    # Risk categorization
    risk_scores = {
        "cont_economii": 1,      # Very low risk
        "depozit": 1,            # Very low risk
        "titluri_venit_fix": 2,  # Low risk
        "pensie_privata": 3,     # Medium risk
        "fond_investitii": 4,    # Medium-high risk
    }
    
    # Calculate portfolio risk
    total_risk_score = 0
    for product in products:
        category = product_returns.get(product, {}).get("category", "cont_economii")
        total_risk_score += risk_scores.get(category, 2)
    
    avg_risk_score = total_risk_score / len(products) if products else 0
    
    # Risk level
    if avg_risk_score < 1.5:
        risk_level = "Foarte Scăzut"
    elif avg_risk_score < 2.5:
        risk_level = "Scăzut"
    elif avg_risk_score < 3.5:
        risk_level = "Mediu"
    else:
        risk_level = "Mediu-Ridicat"
    
    # Risk-return ratio (Sharpe-like ratio, simplified)
    risk_free_rate = 0.02  # 2% risk-free rate
    risk_premium = avg_return - risk_free_rate
    sharpe_ratio = risk_premium / (avg_risk_score / 4) if avg_risk_score > 0 else 0
    
    return {
        "average_return": round(avg_return * 100, 2),
        "risk_level": risk_level,
        "risk_score": round(avg_risk_score, 2),
        "sharpe_ratio": round(sharpe_ratio, 3),
        "products_analysis": product_returns,
        "diversification_score": round(len(set(p.get("category") for p in product_returns.values())) / 5 * 100, 1),
    }


def generate_key_statistics(user_profile: dict, plan_text: str, products: List[str]) -> Dict:
    """
    Generate all key statistics for the plan view page.
    
    Args:
        user_profile: Complete user profile
        plan_text: Financial plan text
        products: List of product names/IDs
    
    Returns:
        Comprehensive statistics dictionary
    """
    # Extract metrics from plan
    plan_metrics = extract_plan_metrics(plan_text, user_profile)
    
    # Calculate savings capacity
    savings_capacity = calculate_savings_capacity(user_profile)
    
    # Calculate wealth projection (10 years)
    wealth_projection = calculate_wealth_projection(user_profile, years=10)
    
    # Analyze risk-return
    risk_return = analyze_plan_risk_return(user_profile, products)
    
    # Calculate timelines for goals
    goal_timelines = []
    all_goals = (
        plan_metrics.get("short_term_goals", []) +
        plan_metrics.get("medium_term_goals", []) +
        plan_metrics.get("long_term_goals", [])
    )
    
    for goal in all_goals[:3]:  # Top 3 goals
        if goal and len(goal) > 5:
            timeline = calculate_goal_timeline(user_profile, goal)
            goal_timelines.append(timeline)
    
    return {
        "plan_metrics": plan_metrics,
        "savings_capacity": savings_capacity,
        "wealth_projection": wealth_projection,
        "risk_return_analysis": risk_return,
        "goal_timelines": goal_timelines,
        "generated_at": datetime.now().isoformat(),
    }
