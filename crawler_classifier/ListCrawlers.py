import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载根据条件筛选后的指定股票的列表。
'''
from crawler.list.stockanalysisList import StockAnalysis_List
from config import config
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ListCrawlerFunctions(object):
    def __init__(self) -> None:
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.StockAnalysis),
            threading.Thread(target=self.StockAnalysis_list_by_country)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def StockAnalysis(self):
        try:
            data = {
                "Prompt": "This is a filtered list based on the selected criteria downloaded from the stockanalysis.com."}
            stockanalysis = StockAnalysis_List(config)
            data["data"] = stockanalysis.download_lists()
            self.alldata["stockanalysis_list"] = data
        except Exception as e:
            logging.error("Error in stockanalysis_list: %s", e)
            self.alldata["stockanalysis_list"] = {
                "Prompt": "Error in collecting data", "data": "None"}

    def StockAnalysis_list_by_country(self):
        try:
            data = {
                "Prompt": "This is a filtered list based on the selected country downloaded from the stockanalysis.com."}
            stockanalysis = StockAnalysis_List(config)
            data["data"] = stockanalysis.download_lists_by_country()
            self.alldata["stockanalysis_list_by_country"] = data
        except Exception as e:
            logging.error("Error in StockAnalysis_list_by_country: %s", e)
            self.alldata["stockanalysis_list_by_country"] = {
                "Prompt": "Error in collecting data", "data": "None"}

    def return_data(self):
        return self.alldata
