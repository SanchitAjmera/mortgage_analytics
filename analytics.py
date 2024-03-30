import pandas as pd
from typing import Dict, Optional, List, Tuple

SCENARIO_ASSUMPTIONS: Dict[str, Dict] = {
    "BLT interest-only private": {
        "deposit_pc": 0.25,
        "interest_rate": 0.045,
        "lenders_fee": 1000,
        "company": False,
    },
    "BLT repayment private": {
        "deposit_pc": 0.25,
        "interest_rate": 0.045,
        "lenders_fee": 1000,
        "company": False,
    },
    "Residential Repayment": {
        "deposit_pc": 0.1,
        "interest_rate": 0.049,
        "lenders_fee": 1000,
        "company": False,
    },
    "BLT interest-only ltd": {
        "deposit_pc": 0.25,
        "interest_rate": 0.0544,
        "lenders_fee": 2000,
        "company": True,
    },
    "BLT repayment ltd": {
        "deposit_pc": 0.25,
        "interest_rate": 0.0544,
        "lenders_fee": 2000,
        "company": True,
    },
}


def compute_mortgage_analytics(
    rent: float,
    price: float,
    service_charge: float,
    term: int,
    scenario_assumptions: Dict[str, Dict] = SCENARIO_ASSUMPTIONS,
    scenarios: List[str] = list(SCENARIO_ASSUMPTIONS.keys()),
) -> pd.DataFrame:
    """
    Computes the mortgage analytics for each scenario in the scenario_assumptions dictionary
    it includes analutics on tax, cashflow, rental yield, and monthly payments for each scenario
    """
    results = []
    for scenario, assumptions in scenario_assumptions.items():
        if scenario not in scenarios:
            continue

        deposit = price * assumptions["deposit_pc"]
        loan_to_value = price - deposit
        yearly_interest_payment = loan_to_value * assumptions["interest_rate"]
        monthly_interest_payment = yearly_interest_payment / 12
        payments = term * 12
        monthly_service_charge = service_charge / 12
        monthly_interest_rate = assumptions["interest_rate"] / 12
        total_monthly_mortgage_payment = (
            loan_to_value
            * monthly_interest_rate
            * ((1 + monthly_interest_rate) ** payments)
            / ((1 + monthly_interest_rate) ** payments - 1)
        )
        monthly_loan_payment = total_monthly_mortgage_payment - monthly_interest_payment
        rental_yield = rent / price * 100

        if "interest-only" in scenario:
            total_monthly_mortgage_payment = monthly_interest_payment
            monthly_loan_payment = 0

        if assumptions["company"]:
            # calculating rental yield with corporation tax on profits
            taxable_amount = (
                rent - monthly_service_charge - total_monthly_mortgage_payment
            )
            corporation_tax_rate = 0.19
            tax = taxable_amount * corporation_tax_rate
            rental_profit = (
                rent - monthly_service_charge - total_monthly_mortgage_payment - tax
            )
            rental_yield = rental_profit / rent
        else:
            # calculating rental yield with income tax on revenue
            taxable_amount = rent - monthly_service_charge
            income_tax_rate = 0.4
            tax_relief = 0.2 * monthly_interest_payment
            tax = taxable_amount * income_tax_rate - tax_relief
            rental_profit = (
                rent - monthly_service_charge - total_monthly_mortgage_payment - tax
            )

        if "Residential" in scenario:
            # residential properties dont have any rental income
            tax = 0
            rental_profit = -total_monthly_mortgage_payment
            rental_yield = 0

        result = {
            "scenario": scenario,
            "price": price,
            "deposit": deposit,
            "loan_to_value": loan_to_value,
            "interest_rate": assumptions["interest_rate"],
            "yearly_interest_payment": yearly_interest_payment,
            "monthly_interest_payment": monthly_interest_payment,
            "monthly_loan_payment": monthly_loan_payment,
            "monthly_mortgage_payment": total_monthly_mortgage_payment,
            "rent": 0 if "Residential" in scenario else rent,
            "taxable_amount": taxable_amount,
            "tax": tax,
            "cashflow": rental_profit,
            "rental_yield": rental_yield,
        }

        results.append(result)

    df = pd.DataFrame(results)
    df.set_index("scenario", inplace=True)
    return df


def compute_mortgage_cashflow_surface(
    service_charge: float = 2000,
    term: int = 25,
    scenarios: List[str] = list(SCENARIO_ASSUMPTIONS.keys()),
) -> pd.DataFrame:
    """
    Computes the cashflow surface for a range of prices and rents
    this should be vectorised in the compute mortgage analytics function to be honest
    """

    def _get_minmax_rent_for_price(price: float) -> Tuple[int, int]:
        if price < 250000:
            return 1000, 1250
        elif price < 300000:
            return 1250, 1750
        elif price < 350000:
            return 1750, 2250
        else:
            return 2000, 4000

    price_min = 200000
    price_max = 400000
    rent_min = 1000
    rent_max = 3000
    scenario_cashflow_surfaces = []

    for price in range(price_min, price_max, 10000):
        rent_min, rent_max = _get_minmax_rent_for_price(price)
        for rent in range(rent_min, rent_max, 10):
            results: pd.DataFrame = compute_mortgage_analytics(
                rent=rent,
                price=price,
                service_charge=service_charge,
                term=term,
                scenarios=scenarios,
            )
            cashflows = results["cashflow"]
            for scenario in scenarios:
                scenario_cashflow_surfaces.append(
                    (scenario, price, rent, cashflows[scenario])
                )

    scenario_cashflow_surfaces = pd.DataFrame(
        scenario_cashflow_surfaces, columns=["scenario", "price", "rent", "cashflow"]
    )
    return scenario_cashflow_surfaces
