import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定加密货币的自媒体报道。
'''
from crawler.selfmedia.cryptopanicSpecificCryptocurrencySelfMedia import Cryptopanic_Specific_Cryptocurrency_Self_Media
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificCryptocurrencySelfMediaCrawlerFunctions(object):
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
        cryptopanic = Cryptopanic_Specific_Cryptocurrency_Self_Media(
            self.cryptocurrency)
        try:
            data = cryptopanic.download()
            self.alldata["cryptopanic"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in cryptopanic_selfmedia: %s", e)
            self.alldata["cryptopanic"] = "Error in collecting data"

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    c = SpecificCryptocurrencySelfMediaCrawlerFunctions('BTC')
    print(c.return_data())
