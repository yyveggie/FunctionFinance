import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 gurufocus 主页中收集各个其余网页的金融头条新闻。
    05.19: 部分解析有问题
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from crawler.utils import check_url, check_url_sync, save_urls, save_urls_sync
from crawler import headless_scrape
from fake_useragent import UserAgent
from lxml import etree
from datetime import datetime


def convert_date(date_string):
    month_map = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }
    month_str, day_str = date_string.split(' ')
    current_year = datetime.now().year
    month_num = month_map[month_str]
    formatted_date = f"{current_year}-{month_num}-{day_str}"
    return formatted_date

class Gurufocus_News(Usable_IP):
    def __init__(self, args={}):
        super().__init__(args)
        self.db_connection = MongoConnection('News')
        self.rounds = 1
        self.headers = {
            'User-Agent': UserAgent().random,
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImJhMjY5YmNkNDBmNDRlYzZiNjAyZDQ5MTczNDgzYWQxNThiNzExYzU4MGIwYmEzMzE4ZTcxMzE1YmRmZDM0YzFjMjQ3YmFmZmM0MTgyMDdjIn0.eyJhdWQiOiIyIiwianRpIjoiYmEyNjliY2Q0MGY0NGVjNmI2MDJkNDkxNzM0ODNhZDE1OGI3MTFjNTgwYjBiYTMzMThlNzEzMTViZGZkMzRjMWMyNDdiYWZmYzQxODIwN2MiLCJpYXQiOjE3MTQ1MTQ0MjEsIm5iZiI6MTcxNDUxNDQyMSwiZXhwIjoxNzI0ODgyNDIxLCJzdWIiOiIiLCJzY29wZXMiOltdfQ.4g4x58GESxZvfLs4l8-qXIsP3CRiL4RaVk--9S-Ho_ffLdEouDLtBkpUHoCHKbbW7LX_EMgGHuLNoSjcbWwYKN3hiuxhBlMChwf4-m0lJlDLbXMj-jQZIDU-nyBkONM7DSuDVLYCpLUGHO5B6kYWpD5zClFpwUuGc9GZx2PsqHpKf3GkpPHqxdXyy_vqMI0juBExHhr_xN-tmX3qz68Ninw59boTiJhiJQbsVd5tniIpGVYAgstr3nuwq9zsE32fOy0flhpmsxdSuFVjTqPDtaca2GZVvCko5jfFFxzJIgVglm8wk6RYn4O142WYUG5eWDDrQ2hj8FKvC83mBvMZMJ4B3JNDAB1OdBsK_UnRjs8d_QcEPoF9XyMBqeDH0MC6kCLSm9XbN3xGxyHZFy_A3v0-taJprNlb-UqruM91ldG8okvNs0f6L_05GNxd3ldIVTCt1mpgD60dx8SW_AlKkrKx4Mvk1jDqYG8TlLMLNtqCiLyqIMbOoRDv2DeWUH4aeQBsBV-G8wVFoW0qMxAMtKMsIkb5ZjZKuVVJpMAz89lSBiQTq8ve6Sk-axLAQoSgnU3lP9EJGm2405OiXOqnUeSZOQn3pkkuDBy3W-FR7gMA2NM2eMmZ7LUMlqt98LiMCUqiGtlIu6jgp08hLu8_gl5dHA8f_LpOVB84WSNqoPE',
            'content-type': 'application/json',
            'origin': 'https://www.gurufocus.com',
            'priority': 'u=1, i',
            'referer': 'https://www.gurufocus.com/stock-market-news',
            'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'signature': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MTQ1NjExNjcsImNsaWVudF90aW1lIjoxNzE0NTYxMTY3LCJ1cmwiOiIvX2FwaS9sYXRlc3QtZ2xvYmFsLW5ld3MiLCJzZXJ2ZXJfdGltZSI6MTcxNDU2MTE0NSwiZXhwIjoxNzE0NTY0NzY3fQ._zc7gdVf4FiodF8Oix4qssK27ioDSA-u3r-YvpmChns',
        }

    def _get_data_list(self, titles, urls, dates, source):
        data_list = []
        filtered_urls = check_url_sync(collection_name=source, url_list=urls, source=source)
        print('length of filtered urls: {0}'.format(len(filtered_urls)))
        if len(filtered_urls) == 0:
            return '当前没有新的链接'
        # 根据过滤后的URL更新titles和dates
        filtered_titles = [title for title, url in zip(titles, urls) if url in filtered_urls]
        filtered_dates = [date for date, url in zip(dates, urls) if url in filtered_urls]
        contents = [headless_scrape.run_sync(urls=[url])[0] for url in filtered_urls]
        for title, url, date, content in zip(filtered_titles, filtered_urls, filtered_dates, contents):
            data = {
                'title': title,
                'url': url,
                'date': date,
                'content': content
            }
            data_list.append(data)
        return data_list

    def download(self, delay=0.5):
        text = self.request_get_sync(
            'https://www.gurufocus.com/stock-market-news', headers=self.headers
        )
        tree = etree.HTML(text, parser=None)
        
        all_data = []

        try:
            # press_1 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[3]/div[1]/div[1]/div/table/tbody/tr/td[2]/h2/text()')[0]
            titles_1 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[2]/div[1]/div/div/table/tbody/tr/td[2]/a/text()')
            titles_1 = [i.strip() for i in titles_1]
            urls_1 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[1]/div[1]/div/div/table/tbody/tr/td[2]/a/@href')
            dates_1 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[2]/div[1]/div/div/table/tbody/tr/td[1]/text()')
            dates_1 = [convert_date(i.strip()) for i in dates_1]
            data_list = self._get_data_list(titles=titles_1, urls=urls_1, dates=dates_1, source="bloomberg.com")
            self.db_connection.save_data('public', "bloomberg.com", data_list)
            save_urls_sync(collection_name="bloomberg.com", url_list=[data['url'] for data in data_list], source="bloomberg.com")
            all_data.append(data_list)
        except Exception as e:
            print('press_1 error:', e)
        
        try:
            # press_2 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[3]/div[1]/div[2]/div/table/tbody/tr/td[2]/h2/text()')[0]
            titles_2 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[4]/div[1]/div/div/table/tbody/tr[1]/td[2]/a/text()')
            titles_2 = [i.strip() for i in titles_2]
            urls_2 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[1]/div[2]/div/div/table/tbody/tr/td[2]/a/@href')
            dates_2 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[1]/div[2]/div/div/table/tbody/tr/td[1]/text()')
            dates_2 = [convert_date(i.strip()) for i in dates_2]
            data_list = self._get_data_list(titles=titles_2, urls=urls_2, dates=dates_2, source="wsj.com")
            self.db_connection.save_data('public', "wsj.com", data_list)
            save_urls_sync(collection_name="wsj.com", url_list=[data['url'] for data in data_list], source="wsj.com")
            all_data.append(data_list)
        except Exception as e:
            print('press_2 error:', e)
        
        try:
            # press_3 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[3]/div[2]/div[1]/div/table/tbody/tr/td[2]/h2/text()')[0]
            titles_3 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[2]/div[1]/div/div/table/tbody/tr/td[2]/a/text()')
            titles_3 = [i.strip() for i in titles_3]
            urls_3 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[2]/div[1]/div/div/table/tbody/tr/td[2]/a/@href')
            dates_3 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[2]/div[1]/div/div/table/tbody/tr/td[1]/text()')
            dates_3 = [convert_date(i.strip()) for i in dates_3]
            data_list = self._get_data_list(titles=titles_3, urls=urls_3, dates=dates_3, source="reuters.com")
            self.db_connection.save_data('public', "reuters.com", data_list)
            save_urls_sync(collection_name="reuters.com", url_list=[data['url'] for data in data_list], source="reuters.com")
            all_data.append(data_list)
        except Exception as e:
            print('press_3 error:', e)
        
        try:
            # press_4 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[3]/div[2]/div[2]/div/table/tbody/tr/td[2]/h2/text()')[0]
            titles_4 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[2]/div[2]/div/div/table/tbody/tr/td[2]/a/text()')
            titles_4 = [i.strip() for i in titles_4]
            urls_4 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[2]/div[2]/div/div/table/tbody/tr/td[2]/a/@href')
            dates_4 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[2]/div[2]/div/div/table/tbody/tr/td[1]/text()')
            dates_4 = [convert_date(i.strip()) for i in dates_4]
            data_list = self._get_data_list(titles=titles_4, urls=urls_4, dates=dates_4, source="gurufocus.com")
            self.db_connection.save_data('public', "gurufocus.com", data_list)
            save_urls_sync(collection_name="gurufocus.com", url_list=[data['url'] for data in data_list], source="gurufocus.com")
            all_data.append(data_list)
        except Exception as e:
            print('press_4 error:', e)

        try:
            # press_5 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[3]/div[3]/div[2]/div/table/tbody/tr/td[2]/h2/text()')[0]
            titles_5 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[3]/div[2]/div/div/table/tbody/tr/td[2]/a/text()')
            titles_5 = [i.strip() for i in titles_5]
            urls_5 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[3]/div[2]/div/div/table/tbody/tr/td[2]/a/@href')
            dates_5 = tree.xpath('//*[@id="components-root"]/div[1]/div/div[4]/div[3]/div[2]/div/div/table/tbody/tr/td[1]/text()')
            dates_5 = [convert_date(i.strip()) for i in dates_5]
            data_list = self._get_data_list(titles=titles_5, urls=urls_5, dates=dates_5, source="zacks.com")
            self.db_connection.save_data('public', "zacks.com", data_list)
            save_urls_sync(collection_name="zacks.com", url_list=[data['url'] for data in data_list], source="zacks.com")
            all_data.append(data_list)
        except Exception as e:
            print('press_5 error:', e)
        
        return all_data

def main():
    c = Gurufocus_News()
    return c.download()


if __name__ == '__main__':
    print(main())