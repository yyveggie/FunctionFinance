import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler_classifier.PublicResearchReportCrawlers import PublicResearchReportCrawlerFunctions
from data_connection.cache_checker import DataChecker, CacheUtils
from crawler.datetime_utils import today
from langchain.tools import tool
import inspect


@tool('Crawl research reports on Chinese market')
def get_random_research_reports(query: str, date=today()):
    '''
    Crawl research reports on the chinese market, however, you cannot specify the report type.

    Parameter:
        - query (str): The information you want to query from the data.
        - date (str): The date of the research reports report, by default, is today. If you want get today's data, don't input any parameter.
    For example: "What are the report's views on China's clean energy industry?", '2023-12-09'.
    '''
    symbol = "china_research_reports"
    fun_name = inspect.currentframe().f_code.co_name
    data_check = DataChecker(fun_name=fun_name, symbol=symbol, query=query)

    result = data_check.check()

    if result is not None:
        if result[0] == 1:
            return result[1]
        elif result[0] == 0:
            data = PublicResearchReportCrawlerFunctions(date).return_data()
            cache_utils = result[1]
            cache_utils.cache_data(data)
            results = cache_utils.search_data(query=query)
            return results
    elif result is None:
        data = PublicResearchReportCrawlerFunctions(date).return_data()
        cache_utils = CacheUtils(func_name=fun_name, symbol=symbol)
        cache_utils.cache_data(data)
        results = cache_utils.search_data(query=query)
        return results
    

def tools():
    return [get_random_research_reports]


# if __name__ == '__main__':
#     print(get_random_research_reports("What are the report's views on China's clean energy industry?"))
