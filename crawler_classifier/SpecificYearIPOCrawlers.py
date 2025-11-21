import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定时间段的 IPOs
'''
from crawler.ipodate.stockanalysisSpecificYearIPO import StockAnalysis_Specific_Year_IPOs
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificYearIPOCrawlerFunctions(object):
    def __init__(self, year) -> None:
        self.alldata = {}
        self.year = year
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
        stockanalysis = StockAnalysis_Specific_Year_IPOs(self.year)
        data = stockanalysis.download()
        self.alldata["stockanalysis"] = data.to_dict(orient='split')

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    from config import config
    c = SpecificYearIPOCrawlerFunctions('2023')
    data = c.return_data()
    print(data)
