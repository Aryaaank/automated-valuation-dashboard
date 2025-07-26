# app.py
import streamlit as st
import logging
import pandas as pd
from valuation_model import DCFFinancialModel
from utils.data_fetcher import FinancialDataFetcher

st.set_page_config(page_title="DCF Valuation Dashboard")
st.title("📊 Automated DCF Valuation")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sidebar inputs
st.sidebar.header("Enter Valuation Parameters")
ticker = st.sidebar.text_input("Stock Ticker (e.g., AAPL)", "AAPL")
discount_rate = st.sidebar.slider("Discount Rate (%)", 3.0, 15.0, 8.0)
terminal_growth = st.sidebar.slider("Terminal Growth Rate (%)", 1.0, 6.0, 2.5)
projection_years = st.sidebar.slider("Projection Years", 3, 10, 5)

# Peer selection
st.sidebar.header("Peer Comparison (Optional)")
peers = st.sidebar.multiselect(
    "Select Peers",
    options=["MSFT", "GOOG", "AMZN", "META", "NFLX", "TSLA"],
    default=["MSFT", "GOOG"]
)

if st.sidebar.button("Run Valuation"):
    st.subheader(f"📈 Valuation Results for {ticker.upper()}")

    try:
        fetcher = FinancialDataFetcher()
        model = DCFFinancialModel()

        # Main company valuation
        st.info("Fetching financial data...")
        fcf_series = fetcher.get_fcf_series(ticker)

        st.success("Data fetched successfully.")
        st.write("### Free Cash Flow (FCF) History")
        st.line_chart(fcf_series)

        result = model.calculate_enterprise_value(
            fcf_series=fcf_series,
            discount_rate=discount_rate / 100,
            terminal_growth=terminal_growth / 100,
            projection_years=projection_years
        )

        if result['success']:
            st.write("### 🧮 DCF Valuation Summary")
            st.metric("Enterprise Value ($)", f"{result['dcf_value']:,}")
            st.metric("Terminal Value ($)", f"{result['terminal_value']:,}")
        else:
            st.error(f"Valuation failed: {result['error']}")

        # Peer comparison
        if peers:
            st.write("### 👥 Peer Comparison")

            peer_results = {}

            for peer in peers:
                try:
                    peer_fcf = fetcher.get_fcf_series(peer)
                    peer_valuation = model.calculate_enterprise_value(
                        fcf_series=peer_fcf,
                        discount_rate=discount_rate / 100,
                        terminal_growth=terminal_growth / 100,
                        projection_years=projection_years
                    )
                    if peer_valuation['success']:
                        peer_results[peer] = peer_valuation['dcf_value']
                    else:
                        peer_results[peer] = None
                except Exception as e:
                    peer_results[peer] = None
                    logger.warning(f"Peer valuation failed for {peer}: {e}")

            peer_df = pd.DataFrame({
                "Ticker": list(peer_results.keys()),
                "Enterprise Value ($)": [
                    f"{v:,.2f}" if v is not None else "Valuation Failed"
                    for v in peer_results.values()
                ]
            })
            st.dataframe(peer_df)

            # Bar chart only if numeric values exist
            try:
                peer_chart_data = {
                    k: v for k, v in peer_results.items() if v is not None
                }
                if peer_chart_data:
                    chart_df = pd.DataFrame.from_dict(
                        peer_chart_data, orient='index', columns=["Enterprise Value"]
                    )
                    st.bar_chart(chart_df)
                else:
                    st.warning("No successful peer valuations for chart.")
            except Exception as e:
                st.warning(f"Unable to generate chart: {e}")

    except Exception as e:
        st.error(f"❌ Failed to complete valuation: {str(e)}")
