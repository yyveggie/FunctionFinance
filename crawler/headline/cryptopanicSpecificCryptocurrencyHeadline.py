import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从 cryptopanic 的 API 下载指定加密货币相关的最新新闻的标题(包括摘要)和媒体:
https://cryptopanic.com/developers/api/
免费的 API 可以无限制使用
注意:
1. 免费的 API 一次最多请求200条新闻, 每次返回20条, 因此一共有10页
2. 这是 "kind": "news" 的爬取, 要获取关于 media 的数据, 见 media_cryptopanic_streaming.py
'''
import os
import time
import json
import asyncio
import logging
from crawler.utils import check_url, save_urls
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from lxml import etree

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CryptoPanicHeadline")

class Cryptopanic_Specific_Cryptocurrency_Headline(Usable_IP):
    def __init__(self, cryptocurrency, args={}):
        super().__init__(args)
        self.cryptocurrency = cryptocurrency
        self.token :str = os.environ.get('Cryptopanic_TOKEN')  # type: ignore
        self.db_connection = AsyncMongoConnection('Headline')
        self.source = "cryptopanic.com"
        self.rounds = 1

    async def download(self, delay=0.1):
        base_url = 'https://cryptopanic.com/api/v1/posts/?auth_token='
        data_list = []
        for i in range(self.rounds):
            params = {
                # You can use any of UI filters using filter=(rising|hot|bullish|bearish|important|saved|lol)
                "filter": "rising",
                # Filter by currencies using currencies=CURRENCY_CODE1,CURRENCY_CODE2 (max 50)
                "currencies": self.cryptocurrency,
                # Available regions: en (English), de (Deutsch), nl (Dutch), es (Español), fr (Français), it (Italiano), pt (Português), ru (Русский), tr (Türkçe), ar (عربي), cn (中國人), jp (日本), ko (한국인)
                "regions": "en,cn",
                # Filter by kind using kind=news. Default: all. Available values: news or media
                "kind": "news",
                "page": i+1
            }
            headers = {'user-agent': UserAgent().random}
            
            # 添加错误处理逻辑
            try:
                text = await self.request_get(
                    url=base_url+self.token,
                    headers=headers,
                    params=params
                )
                
                # 检查text是否为None
                if text is None:
                    logger.error(f"请求返回了None，可能是网络问题或API限制，跳过当前页 {i+1}")
                    continue
                
                res = json.loads(text)
                
                if "results" not in res:
                    logger.warning(f"API响应中没有results字段: {res}")
                    continue
                    
                results = res["results"]
                
                if not results:
                    logger.info(f"第 {i+1} 页没有结果")
                    continue
                    
                urls = [item["url"] for item in results]
                logger.info(f'获取到 {len(urls)} 个URL')
                
                filtered_urls = await check_url(collection_name=self.source, url_list=urls, source='')
                logger.info(f'过滤后剩余 {len(filtered_urls)} 个URL')
                
                if len(filtered_urls) == 0:
                    logger.info('当前没有新的链接')
                    continue
                    
                for j in results:
                    if j["url"] not in filtered_urls:
                        continue
                    one_sample = {}
                    one_sample["domain"] = j["domain"]
                    one_sample["title"] = j["title"]
                    one_sample["published_date"] = j["published_at"]
                    one_sample["url"] = j["url"]
                    
                    try:
                        one_sample["summary"] = await self.summary_download(j["url"])
                    except Exception as e:
                        logger.error(f"获取摘要时出错: {e}, URL: {j['url']}")
                        one_sample["summary"] = ""
                        
                    one_sample["votes"] = j["votes"]
                    data_list.append(one_sample)
                    
                time.sleep(delay)
                
            except json.JSONDecodeError as e:
                logger.error(f"解析JSON时出错: {e}, text: {text[:100]}...")
                continue
            except Exception as e:
                logger.error(f"处理第 {i+1} 页时发生错误: {e}")
                continue
        
        if not data_list:
            logger.warning("没有获取到任何数据")
            return "没有获取到任何数据"
            
        successful_urls = [item["url"] for item in data_list]
        await save_urls(collection_name=self.source, url_list=successful_urls, source='')
        await self.db_connection.save_data(self.cryptocurrency, self.source, data_list)
        logger.info(f"成功获取 {len(data_list)} 条数据")
        return data_list

    async def summary_download(self, url):
        headers = {'user-agent': UserAgent().random}
        try:
            text = await self.request_get(url=url, headers=headers)
            
            if text is None:
                logger.warning(f"获取摘要时请求返回None: {url}")
                return ""
                
            res = etree.HTML(text, parser=None)
            
            # 添加安全检查
            meta_desc = res.xpath("//meta[@name='description']/@content")
            if not meta_desc:
                logger.warning(f"找不到摘要信息: {url}")
                return ""
                
            return meta_desc[0]
            
        except Exception as e:
            logger.error(f"下载摘要时出错: {e}, URL: {url}")
            return ""


async def main():
    from config import config
    c = Cryptopanic_Specific_Cryptocurrency_Headline('BTC', args=config)
    return await c.download()

if __name__ == "__main__":
    print(asyncio.run(main()))