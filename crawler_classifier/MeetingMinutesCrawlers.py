import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载 FOMC 的会议纪要。
'''
from crawler.statementsminutes.fomcStatementsMinutes import FOMC_Statements_Minutes
import json
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MeetingMinutesCrawlerFunctions(object):
    def __init__(self) -> None:
        self.statement = []
        self.press_conference_transcript = []
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.FOMC),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def FOMC(self):
        fomc = FOMC_Statements_Minutes()
        try:
            data = fomc.download()
            self.statement.append(data['statement'])
            self.press_conference_transcript.append(
                data['press_conference_transcript'])
        except Exception as e:
            logging.error("Error in fomc_meeting_minutes: %s", e)
            self.statement.append("Error in collecting data")
            self.press_conference_transcript.append("Error in collecting data")

    def return_data(self):
        data = {"statement": self.statement, "press_conference_transcript": self.press_conference_transcript}
        return json.dumps(data)


if __name__ == '__main__':
    c = MeetingMinutesCrawlerFunctions()
    statement, press_conference_transcript = c.return_data()
    print(statement)
