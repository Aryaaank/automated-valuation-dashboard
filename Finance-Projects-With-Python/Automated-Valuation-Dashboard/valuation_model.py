import pandas as pd
import logging
import numpy as np

class DCFFinancialModel:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def calculate_enterprise_value(self,
                                   fcf_series: pd.Series,
                                   discount_rate: float = 0.10,
                                   terminal_growth: float = 0.02,
                                   projection_years: int = 5) -> dict:

        result = {
            'success': False,
            'error': None,
            'dcf_value': None,
            'terminal_value': None,
            'projection_years': projection_years
        }

        try:
            if fcf_series is None or len(fcf_series) < 2:
                raise ValueError("Insufficient FCF history")

            if terminal_growth >= discount_rate:
                raise ValueError("Growth rate must be less than discount rate")

            base_fcf = fcf_series.iloc[-1]

            projections = []
            for year in range(1, projection_years + 1):
                projected = base_fcf * (1 + terminal_growth) ** year
                discounted = projected / (1 + discount_rate) ** year
                projections.append(discounted)

            final_fcf = projections[-1]
            terminal_value = (final_fcf * (1 + terminal_growth) /
                              (discount_rate - terminal_growth))
            terminal_value_discounted = terminal_value / (1 + discount_rate) ** projection_years
            enterprise_value = np.sum(projections) + terminal_value_discounted

            result.update({
                'success': True,
                'dcf_value': round(enterprise_value, 2),
                'terminal_value': round(terminal_value_discounted, 2)
            })

        except Exception as e:
            self.logger.error(f"Valuation error: {str(e)}")
            result['error'] = str(e)

        return result
