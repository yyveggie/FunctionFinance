import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from scheduler.stock_selection_groups import behavior_technical_selection
from scheduler.debate.reach_consensus import Consensus

class StockSelection:
    def __init__(self, stock_ticker, king_select, consensus, user_knowledge) -> None:
        self.stock_ticker = stock_ticker
        self.king_select = king_select
        self.consensus = consensus
        self.user_knowledge = user_knowledge

    def __call__(self):
        results = []
        if self.king_select:
            results.append(behavior_technical_selection.behavior_technical_group(self.stock_ticker))
        elif self.consensus:
            analyzer = Consensus(self.stock_ticker, self.user_knowledge)
            results.append(analyzer.analyze())
        return results

def run(stock_ticker, king_select, consensus, user_knowledge):
    parser = StockSelection(stock_ticker, king_select, consensus, user_knowledge)
    return parser()