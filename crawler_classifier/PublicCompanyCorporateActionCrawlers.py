import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    Download Public Company Corporate Actions. Including Actions, Listed, Delisted, Splits, Changes, Spinoffs, Bankruptcies, Acquisitions.
'''
from crawler.corporateaction.stockanalysisSpecificYearPublicCompanyCorporateAction import StockAnalysis_Specific_Year_Public_Corporate_Actions
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class CorporateActionCrawlerFunctions(object):
    def __init__(self, year, type) -> None:
        self.year = year
        self.type = type
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.StockAnalysis),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def StockAnalysis(self):
        stockanalysis = StockAnalysis_Specific_Year_Public_Corporate_Actions(
            self.year, self.type)
        try:
            data = stockanalysis._download_data()
            self.alldata[self.type] = data.to_dict(orient='split')
        except Exception as e:
            logging.error("Error in StockAnalysis corporate_actions: %s", e)
            self.alldata[self.type] = "Error in collecting data"

    def return_data(self):
        return self.alldata


if __name__ == "__main__":
    crawler = CorporateActionCrawlerFunctions('2023', 'Delisted')
    data = crawler.return_data()
    print(data)
