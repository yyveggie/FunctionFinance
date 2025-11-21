import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler_classifier.MeetingMinutesCrawlers import MeetingMinutesCrawlerFunctions
import inspect
from langchain.tools import tool
from data_connection.cache_checker import DataChecker, CacheUtils


@tool('Crawl FOMC statements')
def get_FOMC_statement(query: str):
    '''
    Crawl latest statement and press conference transcript from the Federal Open Market Committee (FOMC).
    You can analyze the Fed's next monetary policy move from this, which will have an impact on the global economy.
    
    Parameters:
        - query (str): The information you want to query from the data.
    
    For example: 'What information about interest rates was revealed in the FOMC's last statement?'
    '''
    symbol = "fomc"
    fun_name = inspect.currentframe().f_code.co_name
    data_check = DataChecker(fun_name=fun_name, symbol=symbol, query=query)
    
    result = data_check.check()

    if result is not None:
        if result[0] == 1:
            return result[1]
        elif result[0] == 0:
            data = MeetingMinutesCrawlerFunctions().return_data()
            cache_utils = result[1]
            cache_utils.cache_data(data)
            results = cache_utils.search_data(query=query)
            return results
    elif result is None:
        data = MeetingMinutesCrawlerFunctions().return_data()
        cache_utils = CacheUtils(func_name=fun_name, symbol=symbol)
        cache_utils.cache_data(data)
        results = cache_utils.search_data(query=query)
        return results


def tools():
    return [get_FOMC_statement]


if __name__ == '__main__':
    print(get_FOMC_statement("What information about interest rates was revealed in the FOMC's last statement?"))
