import streamlit as st
import plotly.express as px
from utils.data_fetcher import FinancialDataFetcher
from valuation_model import DCFFinancialModel


class ValuationDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="Advanced DCF Valuation",
            layout="wide",
            page_icon="📈"
        )
        self.fetcher = FinancialDataFetcher()
        self.model = DCFFinancialModel()

    def _create_sidebar(self):
        with st.sidebar:
            st.header("Valuation Parameters")
            self.ticker = st.text_input("Stock Ticker", "AAPL").upper()
            self.discount_rate = st.slider("Discount Rate (%)", 5.0, 20.0, 10.0, 0.5) / 100
            self.growth_rate = st.slider("Terminal Growth (%)", 0.0, 5.0, 2.0, 0.1) / 100
            st.markdown("---")
            st.caption("Adjust parameters and click refresh")

    def display_valuation(self):
        try:
            data = self.fetcher.get_all_data(self.ticker)

            if not data['success']:
                st.error(f"❌ Data Error: {data.get('error', 'Unknown error')}")
                return

            # Display data visualizations
            col1, col2 = st.columns(2)

            with col1:
                if data['fcf'] is not None:
                    fig = px.line(
                        data['fcf'].reset_index(),
                        x='Date',
                        y=data['fcf'].name,
                        title="Free Cash Flow Trend"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No FCF data available")

            with col2:
                if data['prices'] is not None:
                    fig = px.line(
                        data['prices'].reset_index(),
                        x='Date',
                        y=data['prices'].name,
                        title="Price History"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No price data available")

            # Run valuation calculation
            valuation_result = self.model.calculate_enterprise_value(
                data['fcf'],
                self.discount_rate,
                self.growth_rate
            )

            if not valuation_result.get('success'):
                st.error(f"❌ Valuation Error: {valuation_result.get('error', 'Unknown error')}")
                return

            # Display successful valuation
            st.success(f"""
            **📊 Valuation Results for {self.ticker}**

            - **DCF Value:** ${valuation_result['dcf_value']:,.2f}  
            - **Terminal Value:** ${valuation_result['terminal_value']:,.2f}  
            - **Projection Period:** {valuation_result['projection_years']} years
            """)

        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

    def run(self):
        self._create_sidebar()
        st.title(f"DCF Valuation for {self.ticker}")
        self.display_valuation()


if __name__ == "__main__":
    dashboard = ValuationDashboard()
    dashboard.run()
