import re
import streamlit as st
from app_utils import get_mortgage_analytics, get_scenarios, display_scenarios
from plotly import express as px

st.set_page_config(page_title="Mortgage Analytics", page_icon="🏠")
st.header("Mortgage Analytics")
st.write(
    "Calculate mortgage cash flows of different scenarios and analyse the impact of different variables on the cash flow."
)
scenarios = [
    "Buy To Let",
    "Residential",
    "Interest Only",
    "Capital Repayment",
    "Limited Company",
    "Private Purchase",
]
st.markdown("#### Scenario Selection")
selected_scenarios = st.multiselect(
    "Select scenarios you want to include to compare in the analysis. Default is all scenarios.",
    scenarios,
    default=scenarios,
    help="Selecting Buy to Let will include analytics specific to Buy to Let properties interest rates and deposit for example",
)

SCENARIOS = get_scenarios(selected_scenarios)
st.markdown("#### Property Attributes")

left_column, right_column = st.columns(2)
PRICE = left_column.slider(
    "Price (£)", value=300000, min_value=100000, max_value=500000
)
RENT = right_column.slider("Rent p.m. (£)", value=1800, min_value=500, max_value=3000)

expander = st.expander("Additional Configurations")
with expander:
    left_column, middle_column, right_column = expander.columns(3)
    SERVICE_CHARGE = left_column.slider(
        "Service Charge p.a. (£)",
        value=2000,
        min_value=0,
        max_value=6000,
        help="Service Charge of property per year.",
    )
    ADDITIONAL_EXPENSES = middle_column.slider(
        "Additional Expenses p.a. (£)",
        value=2000,
        min_value=0,
        max_value=6000,
        help="Deductive Expenses per year i.e. ground rent, maintenance, agent fees etc.",
    )
    TERM = right_column.slider(
        "Mortgage Term (years)", value=25, min_value=5, max_value=40
    )

mortgage_results = get_mortgage_analytics(
    rent=RENT,
    price=PRICE,
    service_charge=SERVICE_CHARGE,
    term=TERM,
    scenarios=SCENARIOS,
    additional_expenses=ADDITIONAL_EXPENSES,
)
st.markdown("--------------------------")

display_scenarios(mortgage_results)
# st.write(fig)

st.dataframe(
    mortgage_results, use_container_width=True, height=35 * len(mortgage_results) + 39
)


# st.write(get_mortgage_cashflow_surface())
