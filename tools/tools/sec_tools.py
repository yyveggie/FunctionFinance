import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import os
import requests
import inspect
from langchain.tools import tool
from sec_api import QueryApi
from data_connection.cache_checker import DataChecker, CacheUtils
from unstructured.partition.html import partition_html

queryApi = QueryApi(api_key=os.environ['SEC_API_KEY'])

@tool("Search 10-Q form")
def search_10q(data):
    """
    Useful to search information from the latest 10-Q form for a given stock.
    The input to this tool should be a pipe (|) separated text of length two, representing the stock ticker you are interested and what question you have from it.
        For example, `AAPL|what was last quarter's revenue`.
    """
    fun_name = inspect.currentframe().f_code.co_name
    stock, ask = data.split("|")
    symbol = "10Q" + stock
    data_checker = DataChecker(fun_name, symbol, ask)
    result = data_checker.check()
    query = {
            "query": {
                "query_string": {
                    "query": f"ticker:{stock} AND formType:\"10-Q\""
                }
            },
            "from": "0", 
            "size": "1",
            "sort": [{"filedAt": {"order": "desc"}}]
        }
    if result is not None:
        if result[0] == 1:
            return result[1]
        elif result[0] == 0:
            fillings = queryApi.get_filings(query)['filings']
            link = fillings[0]['linkToFilingDetails']
            text = __download_form_html(link)
            elements = partition_html(text=text)
            content = "\n".join([str(el) for el in elements])
            cache_utils = CacheUtils(func_name=fun_name, symbol=symbol)
            cache_utils.cache_data(content)
            results = cache_utils.search_data(ask)
            return results
    elif result is None:
        fillings = queryApi.get_filings(query)['filings']
        link = fillings[0]['linkToFilingDetails']
        text = __download_form_html(link)
        elements = partition_html(text=text)
        content = "\n".join([str(el) for el in elements])
        cache_utils = CacheUtils(func_name=fun_name, symbol=symbol)
        cache_utils.cache_data(content)
        results = cache_utils.search_data(query=ask)
    else:
        return "No filings found for the given stock and form type."


@tool("Search 10-K form")
def search_10k(data):
    """
    Useful to search information from the latest 10-K form for a given stock.
    The input to this tool should be a pipe (|) separated text of length two, representing the stock ticker you are interested, what question you have from it.
        For example, `AAPL|what was last year's revenue`.
    """
    fun_name = inspect.currentframe().f_code.co_name
    stock, ask = data.split("|")
    symbol = "10K" + stock
    data_checker = DataChecker(fun_name, symbol, ask)
    result = data_checker.check()
    query = {
            "query": {
                "query_string": {
                    "query": f"ticker:{stock} AND formType:\"10-K\""
                }
            },
            "from": "0",
            "size": "1",
            "sort": [{"filedAt": {"order": "desc"}}]
        }
    if result is not None:
        if result[0] == 1:
            return result[1]
        elif result[0] == 0:
            fillings = queryApi.get_filings(query)['filings']
            if fillings is not None:
                link = fillings[0]['linkToFilingDetails']
                text = __download_form_html(link)
                elements = partition_html(text=text)
                content = "\n".join([str(el) for el in elements])
                cache_utils = CacheUtils(func_name=fun_name, symbol=symbol)
                cache_utils.cache_data(content)
                results = cache_utils.search_data(ask)
                return results
    elif result is None:
        fillings = queryApi.get_filings(query)['filings']
        if fillings is not None:
            link = fillings[0]['linkToFilingDetails']
            text = __download_form_html(link)
            elements = partition_html(text=text)
            content = "\n".join([str(el) for el in elements])
            cache_utils = CacheUtils(func_name=fun_name, symbol=symbol)
            cache_utils.cache_data(content)
            results = cache_utils.search_data(query=ask)
    else:
        return "No filings found for the given stock and form type."


def __download_form_html(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Cache-Control': 'max-age=0',
        'Dnt': '1',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    return response.text


def tools():
    return [search_10q, search_10k]


if __name__ == '__main__':
    print(search_10k("AAPL|what was last quarter's revenue"))