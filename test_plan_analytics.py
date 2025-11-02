"""
Test Script for Plan Analytics Functions
========================================

Run this to verify all analytics functions work correctly.
"""

from src.utils.plan_analytics import (
    calculate_savings_capacity,
    calculate_investment_projections,
    estimate_product_returns,
    calculate_goal_timeline,
    calculate_wealth_projection,
    analyze_plan_risk_return,
    generate_key_statistics,
    extract_plan_metrics,
)


def test_savings_capacity():
    """Test savings capacity calculation"""
    print("=" * 60)
    print("TEST 1: Savings Capacity Calculation")
    print("=" * 60)
    
    profile = {
        "annual_income": 72000,
        "age": 32,
        "has_children": True,
        "number_of_children": 1,
        "marital_status": "Căsătorit/ă"
    }
    
    result = calculate_savings_capacity(profile)
    
    print(f"\nProfile: Age {profile['age']}, Income {profile['annual_income']:,} RON/year")
    print(f"Married with {profile['number_of_children']} child\n")
    
    print(f"Monthly Income:       {result['monthly_income']:>10,.2f} RON")
    print(f"Monthly Expenses:     {result['monthly_expenses']:>10,.2f} RON")
    print(f"Monthly Savings:      {result['monthly_savings_potential']:>10,.2f} RON")
    print(f"Annual Savings:       {result['annual_savings_potential']:>10,.2f} RON")
    print(f"Expense Ratio:        {result['expense_ratio']:>10.1f}%")
    print(f"Savings Ratio:        {result['savings_ratio']:>10.1f}%")
    print(f"Emergency Fund Target:{result['emergency_fund_target']:>10,.2f} RON")
    print(f"Months to Emergency:  {result['months_to_emergency_fund']:>10.1f} months")
    print()


def test_investment_projections():
    """Test investment projection calculations"""
    print("=" * 60)
    print("TEST 2: Investment Projections (10 years)")
    print("=" * 60)
    
    projections = calculate_investment_projections(
        initial_amount=5000,
        monthly_contribution=1200,
        annual_return_rate=0.07,  # 7%
        years=10
    )
    
    print(f"\nInitial: 5,000 RON | Monthly: 1,200 RON | Return: 7%\n")
    print(f"{'Year':<6} {'Balance':>12} {'Contributions':>15} {'Returns':>12} {'Yearly Return':>15}")
    print("-" * 60)
    
    for p in projections:
        print(f"{p['year']:<6} {p['balance']:>12,.2f} {p['total_contributions']:>15,.2f} "
              f"{p['total_returns']:>12,.2f} {p['yearly_return']:>15,.2f}")
    
    final = projections[-1]
    print(f"\nFinal Balance:      {final['balance']:>12,.2f} RON")
    print(f"Total Contributed:  {final['total_contributions']:>12,.2f} RON")
    print(f"Total Returns:      {final['total_returns']:>12,.2f} RON")
    print(f"ROI:                {(final['total_returns']/final['total_contributions']*100):>12.1f}%")
    print()


def test_product_returns():
    """Test product return estimation"""
    print("=" * 60)
    print("TEST 3: Product Return Estimates")
    print("=" * 60)
    
    profile = {"risk_tolerance": "Medie"}
    products = [
        "Cont de Economii Super Acces Plus",
        "Fond de Pensii Facultative Raiffeisen Acumulare",
        "SmartInvest - Planuri de Investiții Inteligente"
    ]
    
    returns = estimate_product_returns(profile, products)
    
    print(f"\nRisk Profile: {profile['risk_tolerance']}\n")
    
    for product, data in returns.items():
        print(f"Product: {product}")
        print(f"  Category: {data['category'].replace('_', ' ').title()}")
        print(f"  Annual Return: {data['annual_return_rate']*100:.1f}%")
        print(f"  Risk Adjusted: {data['risk_adjusted']}")
        print()


def test_goal_timeline():
    """Test goal timeline calculation"""
    print("=" * 60)
    print("TEST 4: Goal Timeline Calculation")
    print("=" * 60)
    
    profile = {
        "annual_income": 72000,
        "age": 32,
        "has_children": True,
        "number_of_children": 1,
        "marital_status": "Căsătorit/ă"
    }
    
    goals = [
        "Economii pe termen scurt",
        "Educație copii",
        "Pensionare"
    ]
    
    for goal in goals:
        result = calculate_goal_timeline(profile, goal)
        
        print(f"\nGoal: {result['goal']}")
        print(f"Target Amount:        {result['target_amount']:>12,.2f} RON")
        print(f"Monthly Contribution: {result['monthly_contribution']:>12,.2f} RON")
        print(f"Time Needed:          {result['years_needed']:>12.1f} years ({result['months_needed']:.0f} months)")
        print(f"Completion Date:      {result['estimated_completion']}")
        print(f"Feasibility:          {result['feasibility']}")
        
        if result['milestones']:
            print("\nMilestones:")
            for m in result['milestones']:
                print(f"  {m['percentage']:>3}% ({m['amount']:>10,.2f} RON) - {m['date']} ({m['months_from_now']} months)")


def test_wealth_projection():
    """Test complete wealth projection"""
    print("\n" + "=" * 60)
    print("TEST 5: 10-Year Wealth Projection")
    print("=" * 60)
    
    profile = {
        "annual_income": 72000,
        "age": 32,
        "has_children": True,
        "number_of_children": 1,
        "marital_status": "Căsătorit/ă",
        "risk_tolerance": "Medie"
    }
    
    result = calculate_wealth_projection(profile, years=10)
    summary = result['summary']
    
    print(f"\nProfile: {profile['age']} years old, {profile['annual_income']:,} RON/year")
    print(f"Risk Tolerance: {profile['risk_tolerance']}\n")
    
    print(f"Monthly Contribution: {summary['monthly_contribution']:>12,.2f} RON")
    print(f"Annual Return Rate:   {summary['annual_return_rate']:>12.1f}%")
    print(f"Time Horizon:         {summary['years']:>12} years")
    print(f"\nAfter {summary['years']} years:")
    print(f"Total Contributions:  {summary['total_contributions']:>12,.2f} RON")
    print(f"Total Returns:        {summary['total_returns']:>12,.2f} RON")
    print(f"Final Balance:        {summary['final_balance']:>12,.2f} RON")
    print(f"ROI:                  {summary['roi_percentage']:>12.1f}%")
    print()


def test_risk_return_analysis():
    """Test portfolio risk-return analysis"""
    print("=" * 60)
    print("TEST 6: Portfolio Risk-Return Analysis")
    print("=" * 60)
    
    profile = {"risk_tolerance": "Medie"}
    products = [
        "Cont de Economii Super Acces Plus",
        "Fond de Pensii Facultative Raiffeisen Acumulare",
        "SmartInvest - Planuri de Investiții Inteligente"
    ]
    
    result = analyze_plan_risk_return(profile, products)
    
    print(f"\nPortfolio Analysis:\n")
    print(f"Average Return:       {result['average_return']:>12.2f}%")
    print(f"Risk Level:           {result['risk_level']:>12}")
    print(f"Risk Score:           {result['risk_score']:>12.2f} / 4.0")
    print(f"Sharpe Ratio:         {result['sharpe_ratio']:>12.3f}")
    print(f"Diversification:      {result['diversification_score']:>12.1f}%")
    print()


def test_complete_statistics():
    """Test complete statistics generation"""
    print("=" * 60)
    print("TEST 7: Complete Statistics Generation")
    print("=" * 60)
    
    profile = {
        "annual_income": 72000,
        "age": 32,
        "has_children": True,
        "number_of_children": 1,
        "marital_status": "Căsătorit/ă",
        "risk_tolerance": "Medie",
        "education_level": "Facultate",
        "employment_status": "Angajat",
        "financial_goals": ["Economii pe termen lung", "Educație copii", "Investiții"]
    }
    
    plan_text = """
    # Plan Financiar
    
    ## 3. Strategia de Produse
    
    ### 3.1 Cont de Economii Super Acces Plus
    
    ### 3.2 Fond de Pensii Facultative
    
    ### 3.3 SmartInvest
    """
    
    products = [
        "Cont de Economii Super Acces Plus",
        "Fond de Pensii Facultative",
        "SmartInvest"
    ]
    
    stats = generate_key_statistics(profile, plan_text, products)
    
    print("\nGenerated Statistics Summary:\n")
    print(f"Total Products: {stats['plan_metrics']['total_products']}")
    print(f"Monthly Savings: {stats['savings_capacity']['monthly_savings_potential']:,.2f} RON")
    print(f"10-Year Balance: {stats['wealth_projection']['summary']['final_balance']:,.2f} RON")
    print(f"Average Return: {stats['risk_return_analysis']['average_return']:.2f}%")
    print(f"Risk Level: {stats['risk_return_analysis']['risk_level']}")
    print(f"Goals Analyzed: {len(stats['goal_timelines'])}")
    print()


if __name__ == "__main__":
    print("\n" + "🧪 TESTING PLAN ANALYTICS FUNCTIONS" + "\n")
    print("=" * 60)
    
    try:
        test_savings_capacity()
        test_investment_projections()
        test_product_returns()
        test_goal_timeline()
        test_wealth_projection()
        test_risk_return_analysis()
        test_complete_statistics()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
