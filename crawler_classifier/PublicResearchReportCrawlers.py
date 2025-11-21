import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载市场上公共的研究报告。
'''
from crawler.researchreport.sinaPublicResearchReport import Sina_Public_ResearchReport
import json
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PublicResearchReportCrawlerFunctions(object):
    def __init__(self, date) -> None:
        self.date = date
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Sina),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Sina(self):
        sina = Sina_Public_ResearchReport(self.date)
        try:
            data = sina.download()
            self.alldata["sina"] = data.to_json(orient='records', force_ascii=False)
        except Exception as e:
            logging.error("Error in sina_research_report: %s", e)

    def return_data(self):
        return json.dumps(self.alldata, ensure_ascii=False)


if __name__ == '__main__':
    c = PublicResearchReportCrawlerFunctions('2024-03-28')
    alldata = c.return_data()
    print(alldata)
