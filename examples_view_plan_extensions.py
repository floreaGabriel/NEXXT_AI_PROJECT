"""
Example: How to extend the View Plan page with new features
===========================================================

This file shows examples of common extensions you might want to add.
"""


# =============================================================================
# EXAMPLE 1: Add a new deterministic calculation
# =============================================================================

def calculate_tax_savings(user_profile: dict, products: list) -> dict:
    """
    Calculate tax savings from pension contributions and other products.
    
    Args:
        user_profile: User profile with income
        products: List of products including pension
    
    Returns:
        Dictionary with tax savings breakdown
    """
    annual_income = user_profile.get("annual_income", 50000)
    
    # Romanian tax rates (2025)
    INCOME_TAX_RATE = 0.10  # 10% income tax
    PENSION_DEDUCTION_LIMIT = 400  # EUR ~= 2000 RON (simplified)
    
    tax_savings = {
        "pension_contribution_annual": 0,
        "tax_deduction": 0,
        "effective_savings": 0,
        "net_cost_percentage": 0,
    }
    
    # Check if user has pension product
    has_pension = any("pensie" in p.lower() or "pension" in p.lower() for p in products)
    
    if has_pension:
        # Assume 10% of income to pension (common recommendation)
        pension_contribution = min(annual_income * 0.10, PENSION_DEDUCTION_LIMIT * 5)
        
        # Tax deduction
        tax_deduction = min(pension_contribution, PENSION_DEDUCTION_LIMIT * 5) * INCOME_TAX_RATE
        
        # Net cost
        net_cost = pension_contribution - tax_deduction
        net_cost_percentage = (net_cost / pension_contribution) * 100
        
        tax_savings = {
            "pension_contribution_annual": round(pension_contribution, 2),
            "tax_deduction": round(tax_deduction, 2),
            "effective_savings": round(tax_deduction, 2),
            "net_cost_percentage": round(net_cost_percentage, 1),
        }
    
    return tax_savings


# Usage in page:
# tax_info = calculate_tax_savings(user_profile, products)
# st.metric("Tax Savings", f"{tax_info['effective_savings']:,.0f} RON")


# =============================================================================
# EXAMPLE 2: Add comparison with previous plan version
# =============================================================================

def compare_plan_versions(current_plan: dict, previous_plan: dict) -> dict:
    """
    Compare current plan with previous version to show improvements.
    
    Args:
        current_plan: Current statistics
        previous_plan: Previous statistics
    
    Returns:
        Comparison metrics with deltas
    """
    comparison = {
        "savings_increase": 0,
        "return_improvement": 0,
        "risk_change": 0,
        "new_products": [],
        "removed_products": [],
    }
    
    if not previous_plan:
        return comparison
    
    # Savings comparison
    current_savings = current_plan.get("savings_capacity", {}).get("monthly_savings_potential", 0)
    previous_savings = previous_plan.get("savings_capacity", {}).get("monthly_savings_potential", 0)
    comparison["savings_increase"] = current_savings - previous_savings
    
    # Return comparison
    current_return = current_plan.get("risk_return_analysis", {}).get("average_return", 0)
    previous_return = previous_plan.get("risk_return_analysis", {}).get("average_return", 0)
    comparison["return_improvement"] = current_return - previous_return
    
    # Risk comparison
    current_risk = current_plan.get("risk_return_analysis", {}).get("risk_score", 0)
    previous_risk = previous_plan.get("risk_return_analysis", {}).get("risk_score", 0)
    comparison["risk_change"] = current_risk - previous_risk
    
    # Products comparison
    current_products = set(current_plan.get("plan_metrics", {}).get("products", []))
    previous_products = set(previous_plan.get("plan_metrics", {}).get("products", []))
    comparison["new_products"] = list(current_products - previous_products)
    comparison["removed_products"] = list(previous_products - current_products)
    
    return comparison


# Usage in page:
# if previous_plan:
#     comparison = compare_plan_versions(statistics, previous_plan)
#     st.metric("Savings Capacity", value, delta=comparison["savings_increase"])


# =============================================================================
# EXAMPLE 3: Add Monte Carlo simulation for risk scenarios
# =============================================================================

def monte_carlo_wealth_simulation(
    user_profile: dict,
    years: int = 10,
    simulations: int = 1000
) -> dict:
    """
    Run Monte Carlo simulation for wealth projection with uncertainty.
    
    Args:
        user_profile: User profile
        years: Years to simulate
        simulations: Number of simulation runs
    
    Returns:
        Statistics: mean, median, percentiles, best/worst case
    """
    import numpy as np
    from src.utils.plan_analytics import calculate_savings_capacity
    
    savings = calculate_savings_capacity(user_profile)
    monthly_contribution = savings["monthly_savings_potential"]
    
    # Risk-based return parameters (mean and volatility)
    risk_level = user_profile.get("risk_tolerance", "medie").lower()
    return_params = {
        "scăzută": {"mean": 0.04, "std": 0.02},
        "medie": {"mean": 0.06, "std": 0.05},
        "ridicată": {"mean": 0.08, "std": 0.10},
    }
    
    params = return_params.get(risk_level, return_params["medie"])
    
    # Run simulations
    final_balances = []
    
    for _ in range(simulations):
        balance = 0
        for year in range(years):
            # Random return for this year
            annual_return = np.random.normal(params["mean"], params["std"])
            
            # Add contributions and apply return
            balance += monthly_contribution * 12
            balance *= (1 + annual_return)
        
        final_balances.append(balance)
    
    final_balances = np.array(final_balances)
    
    return {
        "mean": float(np.mean(final_balances)),
        "median": float(np.median(final_balances)),
        "std": float(np.std(final_balances)),
        "percentile_10": float(np.percentile(final_balances, 10)),
        "percentile_25": float(np.percentile(final_balances, 25)),
        "percentile_75": float(np.percentile(final_balances, 75)),
        "percentile_90": float(np.percentile(final_balances, 90)),
        "best_case": float(np.max(final_balances)),
        "worst_case": float(np.min(final_balances)),
    }


# Usage in page:
# mc_results = monte_carlo_wealth_simulation(user_profile, years=10)
# st.write(f"Expected: {mc_results['median']:,.0f} RON")
# st.write(f"Best case (90%): {mc_results['percentile_90']:,.0f} RON")
# st.write(f"Worst case (10%): {mc_results['percentile_10']:,.0f} RON")


# =============================================================================
# EXAMPLE 4: Add notification system for milestones
# =============================================================================

def check_milestone_notifications(user_email: str, statistics: dict) -> list:
    """
    Check if user is approaching any milestones and generate notifications.
    
    Args:
        user_email: User email
        statistics: Current plan statistics
    
    Returns:
        List of notification messages
    """
    notifications = []
    
    # Check emergency fund completion
    savings_capacity = statistics.get("savings_capacity", {})
    months_to_emergency = savings_capacity.get("months_to_emergency_fund", 0)
    
    if months_to_emergency <= 3:
        notifications.append({
            "type": "success",
            "title": "🎉 Emergency Fund Almost Ready!",
            "message": f"You're only {months_to_emergency:.0f} months away from your emergency fund goal!",
            "action": "Keep up the great work!"
        })
    
    # Check goal timelines
    for goal in statistics.get("goal_timelines", []):
        months_needed = goal.get("months_needed", 0)
        
        # Alert for goals <6 months away
        if months_needed <= 6:
            notifications.append({
                "type": "info",
                "title": f"🎯 Goal: {goal['goal']}",
                "message": f"You're on track to reach this goal in {months_needed:.0f} months!",
                "action": f"Stay consistent with {goal['monthly_contribution']:,.0f} RON/month"
            })
    
    # Check risk-return balance
    risk_analysis = statistics.get("risk_return_analysis", {})
    diversification = risk_analysis.get("diversification_score", 0)
    
    if diversification < 40:
        notifications.append({
            "type": "warning",
            "title": "⚠️ Low Diversification",
            "message": f"Your portfolio diversification is at {diversification:.0f}%",
            "action": "Consider adding products from different categories"
        })
    
    return notifications


# Usage in page:
# notifications = check_milestone_notifications(user_email, statistics)
# for notif in notifications:
#     if notif["type"] == "success":
#         st.success(f"{notif['title']}\n\n{notif['message']}\n\n{notif['action']}")


# =============================================================================
# EXAMPLE 5: Add interactive scenario planning
# =============================================================================

def calculate_what_if_scenario(
    base_profile: dict,
    scenario_changes: dict
) -> dict:
    """
    Calculate impact of life changes on financial plan.
    
    Args:
        base_profile: Current user profile
        scenario_changes: Dictionary of changes to apply
            e.g., {"income_change": 10000, "new_child": True, "risk_increase": True}
    
    Returns:
        Comparison of base vs scenario statistics
    """
    from src.utils.plan_analytics import (
        calculate_savings_capacity,
        calculate_wealth_projection
    )
    
    # Base calculations
    base_savings = calculate_savings_capacity(base_profile)
    base_wealth = calculate_wealth_projection(base_profile, years=10)
    
    # Apply scenario changes
    scenario_profile = base_profile.copy()
    
    if "income_change" in scenario_changes:
        scenario_profile["annual_income"] += scenario_changes["income_change"]
    
    if "new_child" in scenario_changes and scenario_changes["new_child"]:
        scenario_profile["has_children"] = True
        scenario_profile["number_of_children"] = scenario_profile.get("number_of_children", 0) + 1
    
    if "risk_increase" in scenario_changes and scenario_changes["risk_increase"]:
        risk_map = {"scăzută": "medie", "medie": "ridicată"}
        current_risk = scenario_profile.get("risk_tolerance", "medie").lower()
        scenario_profile["risk_tolerance"] = risk_map.get(current_risk, "ridicată")
    
    # Scenario calculations
    scenario_savings = calculate_savings_capacity(scenario_profile)
    scenario_wealth = calculate_wealth_projection(scenario_profile, years=10)
    
    return {
        "base": {
            "monthly_savings": base_savings["monthly_savings_potential"],
            "10y_wealth": base_wealth["summary"]["final_balance"],
        },
        "scenario": {
            "monthly_savings": scenario_savings["monthly_savings_potential"],
            "10y_wealth": scenario_wealth["summary"]["final_balance"],
        },
        "delta": {
            "monthly_savings": scenario_savings["monthly_savings_potential"] - base_savings["monthly_savings_potential"],
            "10y_wealth": scenario_wealth["summary"]["final_balance"] - base_wealth["summary"]["final_balance"],
        }
    }


# Usage in page:
# st.subheader("What-If Scenario Planner")
# 
# income_change = st.number_input("Income change (RON)", value=0, step=1000)
# new_child = st.checkbox("Add a child")
# risk_increase = st.checkbox("Increase risk tolerance")
# 
# if st.button("Calculate Scenario"):
#     scenario = calculate_what_if_scenario(
#         user_profile,
#         {"income_change": income_change, "new_child": new_child, "risk_increase": risk_increase}
#     )
#     
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Base Savings", f"{scenario['base']['monthly_savings']:,.0f} RON")
#     col2.metric("Scenario Savings", f"{scenario['scenario']['monthly_savings']:,.0f} RON",
#                 delta=f"{scenario['delta']['monthly_savings']:,.0f} RON")


# =============================================================================
# EXAMPLE 6: Add gamification with achievements
# =============================================================================

ACHIEVEMENTS = {
    "first_plan": {
        "name": "🌟 First Plan Created",
        "description": "You've created your first financial plan!",
        "criteria": lambda stats: stats.get("plan_metrics", {}).get("total_products", 0) > 0
    },
    "emergency_ready": {
        "name": "🛡️ Emergency Fund Champion",
        "description": "You have 6+ months of expenses saved",
        "criteria": lambda stats: stats.get("savings_capacity", {}).get("emergency_fund_target", 0) > 0
    },
    "diversified": {
        "name": "📊 Diversification Master",
        "description": "Your portfolio is well-diversified (>60%)",
        "criteria": lambda stats: stats.get("risk_return_analysis", {}).get("diversification_score", 0) > 60
    },
    "long_term": {
        "name": "🔮 Long-Term Planner",
        "description": "You're planning 10+ years ahead",
        "criteria": lambda stats: any(g.get("years_needed", 0) > 10 for g in stats.get("goal_timelines", []))
    },
}


def check_achievements(statistics: dict) -> list:
    """Check which achievements user has unlocked."""
    unlocked = []
    
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement["criteria"](statistics):
            unlocked.append({
                "id": achievement_id,
                "name": achievement["name"],
                "description": achievement["description"]
            })
    
    return unlocked


# Usage in page:
# achievements = check_achievements(statistics)
# if achievements:
#     st.subheader("🏆 Your Achievements")
#     cols = st.columns(len(achievements))
#     for idx, achievement in enumerate(achievements):
#         with cols[idx]:
#             st.info(f"{achievement['name']}\n\n{achievement['description']}")


# =============================================================================
# EXAMPLE 7: Add export to different formats
# =============================================================================

def export_plan_to_pdf(plan_text: str, statistics: dict, user_profile: dict) -> bytes:
    """
    Export plan to PDF format (requires reportlab or similar).
    
    This is a placeholder - you'd need to implement with reportlab or weasyprint.
    """
    # Placeholder - implement with PDF library
    # from reportlab.lib.pagesizes import letter
    # from reportlab.pdfgen import canvas
    # ...
    pass


def export_plan_to_excel(statistics: dict, user_profile: dict) -> bytes:
    """
    Export plan statistics to Excel format.
    
    Args:
        statistics: Plan statistics
        user_profile: User profile
    
    Returns:
        Excel file as bytes
    """
    import pandas as pd
    from io import BytesIO
    
    # Create Excel writer
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: User Profile
        profile_df = pd.DataFrame([user_profile])
        profile_df.to_excel(writer, sheet_name='Profile', index=False)
        
        # Sheet 2: Savings Capacity
        savings_df = pd.DataFrame([statistics['savings_capacity']])
        savings_df.to_excel(writer, sheet_name='Savings', index=False)
        
        # Sheet 3: Wealth Projection
        projection_df = pd.DataFrame(statistics['wealth_projection']['projections'])
        projection_df.to_excel(writer, sheet_name='Projection', index=False)
        
        # Sheet 4: Goals
        if statistics['goal_timelines']:
            goals_df = pd.DataFrame(statistics['goal_timelines'])
            goals_df.to_excel(writer, sheet_name='Goals', index=False)
    
    output.seek(0)
    return output.read()


# Usage in page:
# excel_data = export_plan_to_excel(statistics, user_profile)
# st.download_button(
#     label="📊 Download Excel Report",
#     data=excel_data,
#     file_name=f"financial_plan_{user_email}_{datetime.now().strftime('%Y%m%d')}.xlsx",
#     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
# )
