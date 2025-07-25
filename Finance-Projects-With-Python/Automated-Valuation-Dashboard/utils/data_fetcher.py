import yfinance as yf
import pandas as pd
import logging

class FinancialDataFetcher:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("utils.data_fetcher")

    def get_fcf_series(self, ticker_symbol: str) -> pd.Series:
        try:
            ticker = yf.Ticker(ticker_symbol)
            cf = ticker.cashflow

            if cf.empty:
                raise ValueError("Cash flow statement is empty")

            ocf_keys = [
                'Total Cash From Operating Activities',
                'Operating Cash Flow',
                'NetCashProvidedByUsedInOperatingActivities'
            ]
            capex_keys = [
                'Capital Expenditures',
                'Capital Expenditure',
                'Purchase Of Property Plant And Equipment'
            ]

            ocf_key = next((key for key in ocf_keys if key in cf.index), None)
            capex_key = next((key for key in capex_keys if key in cf.index), None)

            if not ocf_key or not capex_key:
                raise ValueError("Missing OCF or CapEx in cashflow statement")

            fcf = cf.loc[ocf_key] - cf.loc[capex_key]
            return fcf.sort_index(ascending=True).rename("Free Cash Flow")

        except Exception as e:
            self.logger.error(f"Error fetching FCF for {ticker_symbol}: {str(e)}")
            raise ValueError("Free Cash Flow data not available.")

