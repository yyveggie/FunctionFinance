import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

'''
区块链新闻爬虫 - 异步获取各平台区块链新闻
支持多个新闻源的并行爬取，错误处理和日志记录
'''

import json
import logging
from typing import Dict, Type, List, Any, Optional
import aiohttp
import asyncio
from dataclasses import dataclass, field

from crawler.news.blockbeatBlockchainNews import BlockBeats_News
from config import config

# 配置日志
logging.basicConfig(
    filename='blockchain_news_crawler.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BlockchainNewsCrawler")

@dataclass
class NewsSource:
    """新闻源配置类，用于存储和管理新闻源信息"""
    name: str
    crawler_class: Type
    enabled: bool = True
    params: Dict = field(default_factory=dict)


class BlockChainNewsCrawlerFunctions:
    """区块链新闻爬虫核心类"""
    
    def __init__(self, config_obj=None):
        """初始化爬虫，设置配置和新闻源"""
        self.config = config_obj or config
        self.alldata: Dict[str, Any] = {}
        self.sources: List[NewsSource] = self._init_sources()
        
    def _init_sources(self) -> List[NewsSource]:
        """初始化所有新闻源"""
        return [
            NewsSource(name="blockbeat", crawler_class=BlockBeats_News),
            # 在这里添加更多新闻源
        ]
        
    def get_enabled_sources(self) -> List[NewsSource]:
        """获取所有启用的新闻源"""
        return [source for source in self.sources if source.enabled]

    async def fetch_blockchain_news(self, source: NewsSource, session: aiohttp.ClientSession) -> None:
        """从指定新闻源获取新闻数据"""
        try:
            logger.info(f"开始从 {source.name} 获取新闻")
            crawler = source.crawler_class(self.config, session, **source.params)
            data = await crawler.download()
            
            if data is not None and not data.empty:
                self.alldata[source.name] = data.to_json(
                    orient='records', force_ascii=False
                )
                logger.info(f"成功从 {source.name} 获取 {len(data)} 条新闻")
            else:
                logger.warning(f"{source.name} 没有返回任何数据")
                
        except Exception as e:
            logger.error(f"从 {source.name} 获取新闻时出错: {str(e)}", exc_info=True)

    async def run_in_parallel(self, timeout: int = 60) -> None:
        """并行运行所有启用的新闻爬虫"""
        enabled_sources = self.get_enabled_sources()
        if not enabled_sources:
            logger.warning("没有启用的新闻源")
            return
            
        logger.info(f"开始并行爬取 {len(enabled_sources)} 个新闻源")
        
        # 设置超时和自定义连接参数
        conn = aiohttp.TCPConnector(ssl=False, limit=10)
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        
        try:
            async with aiohttp.ClientSession(connector=conn, timeout=timeout_obj) as session:
                tasks = [
                    self.fetch_blockchain_news(source, session)
                    for source in enabled_sources
                ]
                await asyncio.gather(*tasks)
                
        except asyncio.TimeoutError:
            logger.error(f"爬虫任务超时，设置的超时时间为 {timeout} 秒")
        except Exception as e:
            logger.error(f"运行爬虫时发生错误: {str(e)}", exc_info=True)

    def return_data(self) -> str:
        """返回所有爬取的数据的JSON字符串"""
        return json.dumps(self.alldata, ensure_ascii=False)
    
    def get_data_dict(self) -> Dict[str, Any]:
        """返回所有爬取的数据的字典形式"""
        return self.alldata


async def main() -> str:
    """主函数，运行爬虫并返回结果"""
    logger.info("开始区块链新闻爬取任务")
    crawler = BlockChainNewsCrawlerFunctions()
    await crawler.run_in_parallel()
    result = crawler.return_data()
    logger.info("区块链新闻爬取任务完成")
    return result


if __name__ == '__main__':
    data = asyncio.run(main())
    print(f"获取到数据类型: {type(data)}")
    print(data)
