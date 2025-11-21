import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载某个关键词的市场信息。
    数据不好处理，暂时搁置。
'''
from crawler.marketdynamic.googlefinanceSpecificKeywordMarketDynamic import GoogleFinance_Specific_Keyword_Market_Dynamic
from config import config
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificKeywordMarketDynamicClawlerFunctions(object):
    def __init__(self) -> None:
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.GoogleFinance),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def GoogleFinance(self):
        try:
            cnbc = GoogleFinance_Specific_Keyword_Market_Dynamic(config)
            data["data"] = cnbc.download()
            self.alldata["googlefinance_marketdynamics"] = data
        except Exception as e:
            logging.error("Error in googlefinance_marketdynamics: %s", e)
            self.alldata["googlefinance_marketdynamics"] = {
                "Prompt": "Error in collecting data", "data": "None"}

    def return_data(self):
        return self.alldata
