from typing import Dict


class Scenario:
    def __init__(self, buy_to_let: bool, interest_only: bool, limited_company: bool):
        self.buy_to_let = buy_to_let
        self.interest_only = interest_only
        self.limited_company = limited_company

    def __repr__(self) -> str:
        scenario = "Buy To Let" if self.buy_to_let else "Residential"
        scenario += " Interest Only" if self.interest_only else " Capital Repayment"
        scenario += " Limited Company" if self.limited_company else " Private Purchase"
        return scenario

    @property
    def interest_rate(self) -> float:
        # TODO: find a better way to source interest rate
        if self.buy_to_let:
            if self.interest_only:
                if self.limited_company:
                    return 0.0544
                return 0.045
            if self.limited_company:
                return 0.0544
            return 0.045
        return 0.049

    @property
    def deposit_pc(self) -> float:
        if self.buy_to_let:
            return 0.25
        return 0.1

    @property
    def lenders_fee(self) -> float:
        if self.limited_company:
            return 2000
        return 1000
