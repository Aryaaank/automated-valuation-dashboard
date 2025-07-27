import yfinance as yf
import pandas as pd
import logging
import requests

class FinancialDataFetcher:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("utils.data_fetcher")
        self.news_api_key = "563860f42dc0482fa9d6f017dc2c6eb4"

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

    def get_company_news(self, query: str, limit: int = 5) -> list:
        try:
            url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&pageSize={limit}&apiKey={self.news_api_key}"
            response = requests.get(url)
            data = response.json()

            if data.get("status") != "ok":
                raise Exception(data.get("message", "Failed to fetch news"))

            return [
                {
                    "title": article["title"],
                    "url": article["url"],
                    "source": article["source"]["name"]
                }
                for article in data["articles"]
            ]
        except Exception as e:
            self.logger.error(f"Error fetching news for {query}: {str(e)}")
            return []
