import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler_classifier.SpecificCompanyRandomAnnouncementCrawlers import (
    SpecificCompanyStreamingRandomAnnouncementCrawlerFunctions,
    SpecificCompanyTimeWindowRandomAnnouncementCrawlerFunctions
)
from langchain.tools import tool


@tool('Crawl Announcements Within TimeWindow')
def get_time_window_announcement(company: str, start_date: str, end_date: str):
    '''
    Crawl announcements within the time window for a specified chinese company you are interested in.

    Parameters:
        - company (str): The chinese name of the company.
        - start_date (str): The starting date of the time window.
        - end_date (str): The ending date of the time window.
    For example: '茅台', '2023-12-01', '2024-02-09'.
    '''
    tw = SpecificCompanyTimeWindowRandomAnnouncementCrawlerFunctions(
        company, start_date, end_date)
    return tw.return_data()


@tool('Crawl Company Streaming Announcements')
def get_streaming_announcement(ticker: str):
    '''
    Crawl recent(streaming) announcements for a specified chinese company you are interested in.

    Parameter:
        - ticker (str): The ticker symbol of the company's stock.
    For example: 'AAPL'.
    '''
    s = SpecificCompanyStreamingRandomAnnouncementCrawlerFunctions(ticker)
    return s.return_data()


def tools():
    return [get_time_window_announcement, get_streaming_announcement]


if __name__ == '__main__':
    print(get_time_window_announcement('茅台', '2023-12-01', '2024-02-09'))
