import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from valuation_model import DCFValuationModel
from utils.data_fetcher import FinancialDataFetcher

st.set_page_config(page_title="Automated DCF Valuation", layout="wide")
st.title("📊 Automated DCF Valuation Dashboard")

# --- Sidebar Inputs ---
ticker = st.sidebar.text_input("Enter Ticker Symbol (e.g. AAPL, INFY.NS)", value="AAPL")

# Enforce: Discount rate must always be greater than growth rate
default_growth = 8
default_discount = 12

growth_rate = st.sidebar.slider("Expected Growth Rate (%)", 0, 25, default_growth)
discount_rate = st.sidebar.slider("Discount Rate (%)", growth_rate + 1, 30, max(default_discount, growth_rate + 1))

# Instantiate fetcher and valuation model
fetcher = FinancialDataFetcher()
model = DCFValuationModel(growth_rate=growth_rate / 100, discount_rate=discount_rate / 100)

# --- Main Valuation Trigger ---
if st.button("🚀 Run Valuation"):
    try:
        ticker_info = yf.Ticker(ticker).info
        fcf_series = fetcher.get_fcf_series(ticker)
        valuation = model.calculate_intrinsic_value(fcf_series)
        current_price = ticker_info.get("currentPrice", None)

        # 🏢 Business Description
        st.subheader("🏢 Business Description")
        st.write(ticker_info.get("longBusinessSummary", "Description not available."))

        # 💰 Valuation Summary
        st.subheader("💰 Valuation Summary")
        col1, col2 = st.columns(2)
        col1.metric("Current Market Price", f"${current_price:.2f}" if current_price else "N/A")
        col2.metric("Intrinsic Value (DCF)", f"${valuation['intrinsic_value']:.2f}")

        # Verdict
        if current_price:
            if valuation["intrinsic_value"] > current_price:
                st.success("📈 The stock appears **undervalued** based on DCF.")
            elif valuation["intrinsic_value"] < current_price:
                st.error("📉 The stock appears **overvalued** based on DCF.")
            else:
                st.info("⚖️ The stock appears **fairly valued**.")

        # 📊 Valuation Ratios
        st.subheader("📊 Valuation Ratios")
        col3, col4, col5 = st.columns(3)
        col3.metric("Trailing P/E", f"{ticker_info.get('trailingPE', 'N/A')}")
        col3.metric("Forward P/E", f"{ticker_info.get('forwardPE', 'N/A')}")
        col4.metric("P/B Ratio", f"{ticker_info.get('priceToBook', 'N/A')}")
        col4.metric("EV/EBITDA", f"{ticker_info.get('enterpriseToEbitda', 'N/A')}")
        col5.metric("PEG Ratio", f"{ticker_info.get('pegRatio', 'N/A')}")
        col5.metric("ROE (%)", f"{round(ticker_info['returnOnEquity'] * 100, 2) if ticker_info.get('returnOnEquity') else 'N/A'}")

        # ⚠️ Risk Flags
        st.subheader("⚠️ Risk Flags")
        if valuation["latest_fcf"] < 0:
            st.error("Negative Free Cash Flow")
        if current_price and valuation["intrinsic_value"] < current_price:
            st.warning("Intrinsic value is below market price")

        # 📈 FCF Chart (with year formatting)
        st.subheader("📈 Free Cash Flow Trend")
        fig, ax = plt.subplots()
        fcf_series.index = fcf_series.index.year  # Convert x-axis to year only
        fcf_series.plot(kind="bar", ax=ax, color="lightgreen")
        ax.set_title("Free Cash Flow Over Years")
        ax.set_ylabel("FCF (in $)")
        ax.set_xlabel("Year")
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))
        st.pyplot(fig)

        # 📰 News
        st.subheader("📰 Latest News")
        news_articles = fetcher.get_company_news(query=ticker_info.get("shortName", ticker))
        if news_articles:
            for article in news_articles:
                st.markdown(f"**[{article['title']}]({article['url']})**  \n*{article['source']}*")
        else:
            st.info("No recent news articles found.")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
