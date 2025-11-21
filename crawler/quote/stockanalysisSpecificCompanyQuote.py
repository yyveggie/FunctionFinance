import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定公司的实时报价。
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import re


class StockAnalysis_Specific_Company_Quote(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = MongoConnection('Quote')
        self.source = "stockanalysis.com"

    def download(self):
        headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random
        }
        url = "https://stockanalysis.com/stocks/" + self.ticker + "/financials/"
        text = self.request_get_sync(url=url, headers=headers)
        script_text = self.find_last_script(text)
        quote_str = re.search(r'quote:(.*?),state:',
                              script_text, re.DOTALL).group(1)  # type: ignore
        quote = self.str_to_dict(quote_str)
        self.db_connection.save_data(self.ticker, self.source, quote)
        return quote

    def find_last_script(self, html_content):
        script_tags = re.findall(
            r'<script.*?>.*?</script>', html_content, re.DOTALL)
        if not script_tags:
            return None
        last_script = script_tags[-1]
        content_start = last_script.find('>') + 1
        content_end = last_script.rfind('<')
        return last_script[content_start:content_end].strip()

    # '{c:.02,cdr:1,cl:71.37,cp:.03,days:0,e:true,ec:.33,ecp:.46,ep:71.72,epd:71.72,es:"After-hours",eu:"Dec 12, 2023, 7:59 PM EST",ex:"NYSE",exp:1702458900000,h:71.96,h52:121.3,l:70.93,l52:70.08,mc:181677553401,ms:"closed",o:71.38,p:71.39,pd:71.39,symbol:"baba",td:"2023-12-12",ts:1702414866528,u:"Dec 12, 2023, 4:01 PM",v:14514406}'
    def str_to_dict(self, str):
        parsed_dict = {}
        elements = str.replace(', ', ' ').strip('{}').split(',')
        for element in elements:
            key, value = element.split(':', 1)  # Split on the first colon only
            if value.startswith('"') and value.endswith('"'):
                value = value.strip('"')
            else:
                # Attempt to convert numeric values
                try:
                    value = float(value) if '.' in value else int(value)
                except ValueError:
                    pass
            parsed_dict[key] = value
        return parsed_dict


if __name__ == "__main__":
    c = StockAnalysis_Specific_Company_Quote('aapl')
    print(c.download())
