import numpy as np
import pandas as pd

class DCFValuationModel:
    def __init__(self, growth_rate: float, discount_rate: float):
        self.growth_rate = growth_rate
        self.discount_rate = discount_rate

    def calculate_intrinsic_value(self, fcf_series: pd.Series) -> dict:
        if fcf_series.empty:
            raise ValueError("Free Cash Flow data is empty.")

        latest_fcf = fcf_series.iloc[-1]
        projected_fcf = latest_fcf * (1 + self.growth_rate)

        if self.discount_rate <= self.growth_rate:
            raise ValueError("Discount rate must be greater than growth rate for DCF calculation.")

        intrinsic_value = projected_fcf / (self.discount_rate - self.growth_rate)

        return {
            "latest_fcf": latest_fcf,
            "projected_fcf": projected_fcf,
            "intrinsic_value": intrinsic_value
        }
