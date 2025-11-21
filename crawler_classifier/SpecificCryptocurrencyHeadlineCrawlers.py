import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定加密货币的头条。
'''
from crawler.headline.cryptopanicSpecificCryptocurrencyHeadline import Cryptopanic_Specific_Cryptocurrency_Headline
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificCryptocurrencyHeadlineCrawlerFunctions(object):
    def __init__(self, cryptocurrency) -> None:
        self.cryptocurrency = cryptocurrency
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Cryptopanic),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Cryptopanic(self):
        cryptopanic = Cryptopanic_Specific_Cryptocurrency_Headline(
            self.cryptocurrency)
        try:
            data = cryptopanic.download()
            self.alldata["cryptopanic"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in cryptopanic_headlines: %s", e)
            self.alldata["cryptopanic"] = "Error in collecting data"

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    c = SpecificCryptocurrencyHeadlineCrawlerFunctions('BTC')
    data = c.return_data()
    print(data)
