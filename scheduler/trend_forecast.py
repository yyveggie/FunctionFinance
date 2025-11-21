import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from scheduler import behavior_forecast, technical_forecast

class Trend_Analysis:
    def __init__(self, ticker, behavior_forecast, technical_forecast, user_knowledge) -> None:
        self.ticker = ticker
        self.behavior_forecast = behavior_forecast
        self.technical_forecast = technical_forecast
        self.user_knowledge = user_knowledge

    def __call__(self):
        results = []
        if self.technical_forecast:
            results.append(technical_forecast.run(ticker=self.ticker, user_knowledge=self.user_knowledge))
        elif self.behavior_forecast:
            results.append(behavior_forecast.run(ticker=self.ticker, user_knowledge=self.user_knowledge))
        return results

def run(ticker, behavior_forecast, technical_forecast, user_knowledge):
    parser = Trend_Analysis(ticker, behavior_forecast, technical_forecast, user_knowledge)
    return parser()

