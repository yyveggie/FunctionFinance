import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import asyncio
from scheduler import fundamental_analysis
from scheduler.full_analysis_groups import macro_financial_analysis_group, meso_financial_analysis_group, micro_financial_analysis_group

class Trend_Analysis:
    def __init__(self, query, macroeconomic_analysis, industry_analysis, stock_analysis, auto_full_analysis, user_knowledge) -> None:
        self.query = query
        self.macroeconomic_analysis=macroeconomic_analysis, 
        self.industry_analysis=industry_analysis, 
        self.stock_analysis=stock_analysis,
        self.auto_full_analysis=auto_full_analysis
        self.user_knowledge = user_knowledge

    def __call__(self):
        results = []
        if self.auto_full_analysis:
            return asyncio.run(fundamental_analysis.run(self.query))
        elif self.macroeconomic_analysis:
            results.append(macro_financial_analysis_group.run(self.query))
        elif self.industry_analysis:
            results.append(meso_financial_analysis_group.run(self.query))
        elif self.stock_analysis:
            results.append(micro_financial_analysis_group.run(self.query))
        return results

def run(query, macroeconomic_analysis, industry_analysis, stock_analysis, auto_full_analysis, user_knowledge):
    parser = Trend_Analysis(query, macroeconomic_analysis, industry_analysis, stock_analysis, auto_full_analysis, user_knowledge)
    return parser()

