class MarketSimulationData:
    def __init__(self):
        self.stock = "ABC Inc."
        
        self.institutional_behavioral_psychology = "Loss Aversion: 60%, Overconfidence: 70%, Anchoring: 65%, Mental Accounting: 75%, Herd Behavior: 55%, Disposition Effect: 60%"
        
        self.individual_behavioral_psychology = "Herd Behavior: 80%, Overconfidence: 60%, Disposition Effect: 70%, Anchoring: 75%, Mental Accounting: 65%, Loss Aversion: 80%"
        
        self.twenty_day_price = [
            "Day 1: $90, Day 2: $92, Day 3: $95, Day 4: $93, Day 5: $96",
            "Day 6: $100, Day 7: $98, Day 8: $102, Day 9: $105, Day 10: $110",
            "Day 11: $108, Day 12: $112, Day 13: $115, Day 14: $113, Day 15: $116",
            "Day 16: $120, Day 17: $118, Day 18: $122, Day 19: $125, Day 20: $130"
        ]
        
        self.twenty_day_trading_volume = [
            "Day 1: 80,000, Day 2: 90,000, Day 3: 85,000, Day 4: 70,000, Day 5: 75,000",
            "Day 6: 100,000, Day 7: 120,000, Day 8: 110,000, Day 9: 90,000, Day 10: 95,000",
            "Day 11: 105,000, Day 12: 115,000, Day 13: 130,000, Day 14: 120,000, Day 15: 125,000",
            "Day 16: 140,000, Day 17: 150,000, Day 18: 160,000, Day 19: 170,000, Day 20: 180,000"
        ]
        
        self.news = [
            "ABC Inc. plans to expand into new markets.",
            "Analysts predict strong growth for ABC Inc. in the upcoming quarter.",
            "ABC Inc. launches new marketing campaign.",
            "ABC Inc. reports strong quarterly earnings, beats market expectations.",
            "ABC Inc. announces new product launch, expected to boost sales.",
            "Market analysts upgrade ABC Inc.'s stock rating to 'Buy'.",
            "ABC Inc.'s CEO to step down, successor named.",
            "ABC Inc. faces legal challenges over patent infringement claims.",
            "ABC Inc. expands operations, opens new manufacturing facility.",
            "Rumors of potential acquisition of ABC Inc. by larger competitor.",
            "ABC Inc. announces strategic partnership with tech giant.",
            "ABC Inc.'s main competitor reports weak earnings, stock price plummets.",
            "Positive industry outlook expected to benefit ABC Inc.'s future growth.",
            "ABC Inc. receives prestigious industry award for innovation.",
            "ABC Inc. announces plans to buy back shares, boost investor confidence."
        ]
        
        self.financial_indicator = [
            "P/E Ratio: 12, ROE: 18%, Debt-to-Equity Ratio: 0.6",
            "P/E Ratio: 14, ROE: 20%, Debt-to-Equity Ratio: 0.55",
            "P/E Ratio: 15, ROE: 20%, Debt-to-Equity Ratio: 0.5",
            "P/E Ratio: 16, ROE: 22%, Debt-to-Equity Ratio: 0.45",
            "P/E Ratio: 17, ROE: 25%, Debt-to-Equity Ratio: 0.4",
            "P/E Ratio: 18, ROE: 23%, Debt-to-Equity Ratio: 0.5",
            "P/E Ratio: 20, ROE: 28%, Debt-to-Equity Ratio: 0.35",
            "P/E Ratio: 22, ROE: 30%, Debt-to-Equity Ratio: 0.3",
            "P/E Ratio: 21, ROE: 26%, Debt-to-Equity Ratio: 0.4",
            "P/E Ratio: 23, ROE: 32%, Debt-to-Equity Ratio: 0.25",
            "P/E Ratio: 24, ROE: 35%, Debt-to-Equity Ratio: 0.2",
            "P/E Ratio: 25, ROE: 38%, Debt-to-Equity Ratio: 0.15"
        ]