import streamlit as st
import pandas as pd
import plotly.express as px
from analytics import compute_mortgage_analytics, compute_mortgage_cashflow_surface
from streamlit_plotly_events import plotly_events


def format_mortgage_analytics(results: pd.DataFrame) -> pd.DataFrame:
    # edit dataframe to display results
    results["interest_rate (%)"] = results["interest_rate"].apply(lambda x: x * 100)
    results.drop(columns=["interest_rate"], inplace=True, axis=1)

    col_order = [
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
    rent: float, price: float, service_charge: float, term: int
) -> pd.DataFrame:
    results = compute_mortgage_analytics(
        rent=rent, price=price, service_charge=service_charge, term=term
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


st.set_page_config(layout="wide")
st.header("Mortgage Yield Analytics")
st.write(
    "This app calculates the yield of a property based on various scenarios. It doesn't take into account estate agent fees, maintenance costs, or other expenses. Althought adding these expenses can be deducted from the taxable amount"
)
st.sidebar.subheader("Property Attributes")
PRICE = st.sidebar.slider("Price (£)", value=300000, min_value=100000, max_value=500000)
RENT = st.sidebar.slider("Rent p.m.", value=1800, min_value=500, max_value=3000)
SERVICE_CHARGE = st.sidebar.slider(
    "Service charge p.a.", value=2000, min_value=0, max_value=6000
)
TERM = st.sidebar.slider("Term", value=25, min_value=10, max_value=40)

mortgage_results = get_mortgage_analytics(
    rent=RENT, price=PRICE, service_charge=SERVICE_CHARGE, term=TERM
)

st.dataframe(
    mortgage_results, use_container_width=True, height=35 * len(mortgage_results) + 39
)

st.write(get_mortgage_cashflow_surface())
