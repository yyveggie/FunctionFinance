import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    Download Announcements.
    You can specify a company and announcement type.
'''
from crawler.announcement.juchaoSpecificCompanySpecificAnnouncement import Juchao_Specific_Company_Specific_Announcement
from config import config
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificCompanySpecificAnnouncementCrawlerFunctions(object):
    def __init__(self) -> None:
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
        try:
            data = {
                "Prompt": "This is the data downloaded from the juchao.com, where the pdf file has been saved to the database."}
            juchao_pdf = Juchao_Specific_Company_Specific_Announcement(config)
            data["data"] = juchao_pdf.download()
            self.alldata["juchao_announcement"] = data
        except Exception as e:
            logging.error("Error in juchao_announcement: %s", e)
            self.alldata["juchao_announcement"] = {
                "Prompt": "Error in collecting data", "data": "None"}

    def return_data(self):
        return self.alldata

if __name__ == "__main__":
    crawler = SpecificCompanySpecificAnnouncementCrawlerFunctions()
    print(crawler.run_in_parallel())