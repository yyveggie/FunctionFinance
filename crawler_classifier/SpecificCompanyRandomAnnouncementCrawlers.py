import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    Download Announcements.
    You can specify a company, but you cannot specify the announcement type.
'''
from crawler.announcement.sinaSpecificCompanyRandomAnnouncement import Sina_Specific_Company_Random_Announcement
from crawler.announcement.juchaoSpecificCompanyRandomAnnouncement import Juchao_Specific_Company_Random_Announcement
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificCompanyTimeWindowRandomAnnouncementCrawlerFunctions(object):
    def __init__(self, company, start_date, end_date) -> None:
        self.company = company
        self.start_date = start_date
        self.end_date = end_date
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Juchao),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Juchao(self):
        juchao = Juchao_Specific_Company_Random_Announcement(
            self.company, self.start_date, self.end_date)
        try:
            data = juchao.download()
            self.alldata["juchao"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in juchao_announcement: %s", e)
            self.alldata["juchao"] = "Error in collecting data"

    def return_data(self):
        return self.alldata


class SpecificCompanyStreamingRandomAnnouncementCrawlerFunctions(object):
    def __init__(self, ticker) -> None:
        self.ticker = ticker
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Sina)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Sina(self):
        sina = Sina_Specific_Company_Random_Announcement(self.ticker)
        try:
            data = sina.download()
            self.alldata["sina"] = data.to_dict(orient='split')
        except Exception as e:
            logging.error("Error in sina_announcement: %s", e)
            self.alldata["sina"] = "Error in collecting data"

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    # c = SpecificCompanyStreamingRandomAnnouncementCrawlerFunctions(
    #     ticker='600519')
    c = SpecificCompanyTimeWindowRandomAnnouncementCrawlerFunctions(
        company='中国平安', start_date='2020-01-01', end_date='2020-01-20')
    data = c.return_data()
    print(data)
