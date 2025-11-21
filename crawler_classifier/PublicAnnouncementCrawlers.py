import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    Download Public Announcements.
'''
from crawler.announcement.juchaoPublicAnnouncement import Juchao_Public_Announcement
from config import config
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PublicAnnouncementCrawlerFunctions(object):
    def __init__(self) -> None:
        self.alldata = {}
        self.all_filtered_data = {}
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
            data = {"Prompt": "This is the data downloaded from the Juchao.com, including description and pdfs. Users need to select pdf before analysis."}
            juchao_pdf = Juchao_Public_Announcement(config)
            data["description"] = juchao_pdf.download()
            self.alldata["juchao_announcement"] = data
        except Exception as e:
            logging.error("Error in juchao_announcement: %s", e)
            self.alldata["juchao_announcement"] = {
                "Prompt": "Error in collecting data", "data": "None"}

    def return_data(self):
        return self.alldata


if __name__ == "__main__":
    crawler = PublicAnnouncementCrawlerFunctions()
    crawler.run_in_parallel()
    print(crawler.return_data())
