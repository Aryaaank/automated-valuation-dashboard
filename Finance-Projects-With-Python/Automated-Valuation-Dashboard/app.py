import streamlit as st
import logging
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

if st.sidebar.button("Run Valuation"):
    st.subheader(f"📈 Valuation Results for {ticker.upper()}")

    try:
        fetcher = FinancialDataFetcher()
        model = DCFFinancialModel()

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

    except Exception as e:
        st.error(f"❌ Failed to complete valuation: {str(e)}")
