import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定公司指定时间的财报电话会议。
'''
from crawler.earningscall.discountingcashflowsSpecificCompanyEarningsCall import Discountingcashflows_Specific_Company_Earnings_Call
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class EarningsCallCrawlerFunctions(object):
    def __init__(self, ticker, year, quarter):
        self.ticker = ticker
        self.year = year
        self.quarter = quarter
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Discountingcashflows),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Discountingcashflows(self):
        discountingcashflows = Discountingcashflows_Specific_Company_Earnings_Call(
            self.ticker, self.year, self.quarter)
        try:
            data = discountingcashflows.download()
            self.alldata = data
        except Exception as e:
            logging.error("Error in discountingcashflows_earning_calls: %s", e)

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    c = EarningsCallCrawlerFunctions('AAPL', '2023', 'Q4')
    data = c.return_data()
    print(data)
