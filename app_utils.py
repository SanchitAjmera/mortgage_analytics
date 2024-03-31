from typing import List
from analytics import compute_mortgage_analytics, compute_mortgage_cashflow_surface
import pandas as pd
from plotly import express as px
from streamlit_plotly_events import plotly_events
from analytics_utils import Scenario
import streamlit as st


def format_mortgage_analytics(results: pd.DataFrame) -> pd.DataFrame:
    # edit dataframe to display results
    results["interest_rate (%)"] = results["interest_rate"].apply(lambda x: x * 100)
    results.drop(columns=["interest_rate"], inplace=True, axis=1)

    col_order = [
        "scenario",
        "price",
        "deposit",
        "loan_to_value",
        "interest_rate (%)",
        "yearly_interest_payment",
        "monthly_interest_payment",
        "monthly_loan_payment",
        "monthly_mortgage_payment",
        "rent",
        "rental_yield",
        "taxable_amount",
        "tax",
        "cashflow",
    ]
    results = results[col_order]
    results = results.round(2)
    return results


def get_mortgage_analytics(
    rent: float,
    price: float,
    service_charge: float,
    term: int,
    scenarios: List[Scenario],
    additional_expenses: float = 0,
) -> pd.DataFrame:
    results = compute_mortgage_analytics(
        rent=rent,
        price=price,
        service_charge=service_charge,
        term=term,
        scenarios=scenarios,
        additional_expenses=additional_expenses,
    )
    return format_mortgage_analytics(results)


def get_mortgage_cashflow_surface(minimum_cashflow: float = 500):
    results = compute_mortgage_cashflow_surface(scenarios=["BLT interest-only ltd"])
    fig = px.scatter_3d(
        results,
        x="price",
        y="rent",
        z="cashflow",
        color="cashflow",
        symbol="scenario",
        labels={"price": "Price", "rent": "Rent", "cashflow": "Cashflow"},
    )
    fig.update_layout(
        scene=dict(
            xaxis_title="Price",
            yaxis_title="Rent",
            zaxis_title="Cashflow",
        ),
    )
    plotly_events(fig)
    viable_results = results[results["cashflow"] > minimum_cashflow]
    return viable_results


def get_scenarios(selected_scenarios: List[str]) -> List[Scenario]:
    scenarios: List[Scenario] = []
    mortgage_types = []
    repayment_types = []
    ownership_types = []

    for scenario in selected_scenarios:
        if "Buy To Let" in scenario or "Residential" in scenario:
            mortgage_types.append(scenario)
        if "Interest Only" in scenario or "Capital Repayment" in scenario:
            repayment_types.append(scenario)
        if "Limited Company" in scenario or "Private Purchase" in scenario:
            ownership_types.append(scenario)

    for mortgage_type in mortgage_types:
        for repayment_type in repayment_types:
            for ownership_type in ownership_types:
                buy_to_let = mortgage_type == "Buy To Let"
                interest_only = repayment_type == "Interest Only"
                limited_company = ownership_type == "Limited Company"
                scenarios.append(Scenario(buy_to_let, interest_only, limited_company))

    return scenarios


def display_scenarios(mortgage_results: pd.DataFrame):
    for scenario in mortgage_results["scenario"].unique():
        rent = mortgage_results["rent"].values[0]
        scenario_results = mortgage_results[mortgage_results["scenario"] == scenario]
        st.write(f"#### {scenario}")
        col1, col2, col3 = st.columns(3)
        cashflow = round(scenario_results["cashflow"].values[0])
        mortgage = round(scenario_results["monthly_mortgage_payment"].values[0])
        tax = round(scenario_results["tax"].values[0])
        col1.metric(
            "Mortgage Payment (£)", f"£{mortgage}", delta="-", delta_color="off"
        )
        col2.metric("Tax (£)", f"£{tax}", delta="-", delta_color="off")
        col3.metric(
            "Cashflow (£)", f"£{cashflow}", delta=f"{round((cashflow/rent)*100)}%"
        )
        with st.expander("View Calculations"):
            st.write("Price: £", scenario_results["price"].values[0])
            st.write("Deposit: £", scenario_results["deposit"].values[0])
            st.write("Loan to Value: ", scenario_results["loan_to_value"].values[0])
            st.write("Interest Rate: ", scenario_results["interest_rate (%)"].values[0])
            st.write(
                "Monthly Interest Payment: £",
                scenario_results["monthly_interest_payment"].values[0],
            )
            st.write(
                "Monthly Loan Payment: £",
                scenario_results["monthly_loan_payment"].values[0],
            )
            st.write(
                "Monthly Mortgage Payment: £",
                scenario_results["monthly_mortgage_payment"].values[0],
            )
            st.write("Rent: £", scenario_results["rent"].values[0])
            st.write("Rental Yield: ", scenario_results["rental_yield"].values[0])

            if scenario_results["scenario"].values[0] == "Limited Company":
                st.write(
                    "Taxable Amount: £", scenario_results["taxable_amount"].values[0]
                )
                st.write("Tax: £", scenario_results["tax"].values[0])
                st.write("Cashflow: £", scenario_results["cashflow"].values[0])

            else:
                st.write(
                    "Taxable Amount: £", scenario_results["taxable_amount"].values[0]
                )
                st.write("Tax: £", scenario_results["tax"].values[0])
                st.write("Cashflow: £", scenario_results["cashflow"].values[0])

            st.write("Taxable Amount: £", scenario_results["taxable_amount"].values[0])

        st.markdown("--------------------------")
