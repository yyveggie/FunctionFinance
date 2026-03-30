from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
import pandas as pd
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from mongodb import MongoAPI
from parser import PostParser
from parser import CommentParser


class PostCrawler(object):

    def __init__(self, stock_symbol: str):
        self.browser = None
        self.symbol = stock_symbol
        self.start = time.time()  # calculate the time cost

    def create_webdriver(self):
        options = webdriver.ChromeOptions()  # configure the webdriver
        options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             'like Gecko) Chrome/111.0.0.0 Safari/537.36"')
        self.browser = webdriver.Chrome(options=options)

        current_dir = os.path.dirname(os.path.abspath(__file__))  # hide the features of crawler/selenium
        js_file_path = os.path.join(current_dir, 'stealth.min.js')
        with open(js_file_path) as f:
            js = f.read()
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })

    def get_page_num(self):
        try:
            self.browser.get(f'http://guba.eastmoney.com/list,{self.symbol},f_1.html')
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.paging > li:nth-child(7) > a > span'))
            )
            page_element = self.browser.find_element(By.CSS_SELECTOR, 'ul.paging > li:nth-child(7) > a > span')
            return int(page_element.text)
        except Exception as e:
            print(f'{self.symbol}: 获取最大页数失败，受反爬或网速影响，默认读取100页。错误：{e}')
            return 100

    def crawl_post_info(self, page1: int, page2: int):
        self.create_webdriver()
        max_page = self.get_page_num()  # confirm the maximum page number to crawl
        current_page = page1  # start page
        stop_page = min(page2, max_page)  # avoid out of the index

        parser = PostParser()  # must be created out of the 'while', as it contains the function about date
        postdb = MongoAPI('post_info', f'post_{self.symbol}')  # connect the collection
        commentdb = MongoAPI('comment_info', f'comment_{self.symbol}')
        comment_parser = CommentParser()

        retry_count = 0
        while current_page <= stop_page:  # use 'while' instead of 'for' is crucial for exception handling
            time.sleep(abs(random.normalvariate(0.05, 0.02)))  # 适当放缓，减轻被封禁概率
            url = f'http://guba.eastmoney.com/list,{self.symbol},f_{current_page}.html'

            try:
                self.browser.get(url)  # many times our crawler is restricted access (especially after 664 pages)
                dic_list = []
                # 加大超时时间，并捕获获取页面的异常
                try:
                    WebDriverWait(self.browser, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.listitem'))
                    )
                except TimeoutException:
                    pass # 若某页空数据或加载很慢也继续往下跑，防止强制报错
                
                list_item = self.browser.find_elements(By.CSS_SELECTOR, '.listitem')  # includes all posts on one page
                if current_page == 1:
                    list_item = list_item[1:]  # 剔除首页的置顶帖（开户广告hhh）
                for li in list_item:  # get each post respectively
                    dic = parser.parse_post_info(li)
                    if 'guba.eastmoney.com/news' in dic['post_url']:  # other website is different!
                        dic_list.append(dic)
                
                if dic_list:  # 避免因列表为空导致 insert_many 报错
                    postdb.insert_many(dic_list)
                    
                    # --- 改进：紧接着爬取这些帖子的评论 ---
                    for dic in dic_list:
                        # 过滤掉没有评论的帖子
                        if dic.get('comment_num', 0) > 0:
                            post_url = dic['post_url']
                            post_id = dic['_id']
                            
                            # 【新增跳过判断】查询评论库里是否已有当前帖子的评论
                            existing_comment = commentdb.find_one({'post_id': post_id}, {'_id': 1})
                            if existing_comment:
                                continue  # 如果已经存在该帖子的评论，则跳过爬取
                            
                            self._crawl_comments_for_post(post_url, post_id, commentdb, comment_parser)
                    # --------------------------------------

                print(f'{self.symbol}: 已经成功爬取第 {current_page} 页帖子基本信息及评论，'
                      f'进度 {(current_page - page1 + 1)*100/(stop_page - page1 + 1):.2f}%')
                current_page += 1
                retry_count = 0  # 成功后恢复重试计数

            except Exception as e:
                print(f'{self.symbol}: 第 {current_page} 页出现了错误 {e}')
                retry_count += 1
                if retry_count >= 3:
                    print(f'{self.symbol}: 第 {current_page} 页重试超过 3 次，跳开。')
                    current_page += 1
                    retry_count = 0
                    
                time.sleep(1)
                try:
                    self.browser.delete_all_cookies()
                    self.browser.quit()  # 安全退出
                except:
                    pass
                
                # 对浏览器重启加上重试和异常保护
                for _ in range(3):
                    try:
                        self.create_webdriver()  # restart it again!
                        break
                    except Exception as launch_e:
                        print(f"[{self.symbol}] 重新生成 WebDriver 失败, 5秒后重试: {launch_e}")
                        time.sleep(5)
                else:
                    print(f"[{self.symbol}] 致命错误：该挂起无法重新启动浏览器。")
                    break

        end = time.time()
        time_cost = end - self.start  # calculate the time cost
        row_count = postdb.count_documents()
        
        # 增加数据库为空的判断，避免空库读取报错
        if row_count > 0:
            first_doc = postdb.find_first()
            last_doc = postdb.find_last()
            start_date = last_doc['post_date'] if last_doc else '未知'
            end_date = first_doc['post_date'] if first_doc else '未知'
        else:
            start_date, end_date = '未知', '未知'
            
        try:
            self.browser.quit()
        except:
            pass

        print(f'成功爬取 {self.symbol}股吧共 {stop_page - page1 + 1} 页帖子，总计 {row_count} 条，花费 {time_cost/60:.2f} 分钟')
        print(f'帖子的时间范围从 {start_date} 到 {end_date}')

    def _crawl_comments_for_post(self, url, post_id, commentdb, parser):
        # 内部方法：复用原有评论提取逻辑
        try:
            time.sleep(abs(random.normalvariate(0.05, 0.02)))  # 随机延迟增加冗余

            try:
                self.browser.get(url)
                # 等待评论项加载，或者等待出现"暂无评论"标识，避免无限死等抛出错误
                WebDriverWait(self.browser, 1.5, poll_frequency=0.2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.reply_item.cl, div.no_reply'))
                )
            except TimeoutException:
                try:
                    self.browser.refresh()
                    WebDriverWait(self.browser, 1.5, poll_frequency=0.2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.reply_item.cl, div.no_reply'))
                    )
                except TimeoutException:
                    pass # 再次超时就直接放弃本条帖子（可能无评论或死链）
                    
            try:
                reply_items = self.browser.find_elements(By.CSS_SELECTOR, 'div.allReplyList > div.replylist_content > div.reply_item.cl')
            except Exception:
                reply_items = []

            dic_list = []
            for item in reply_items:
                dic = parser.parse_comment_info(item, post_id)
                dic_list.append(dic)

                if parser.judge_sub_comment(item):
                    sub_reply_items = item.find_elements(By.CSS_SELECTOR, 'li.reply_item_l2')
                    for subitem in sub_reply_items:
                        dic = parser.parse_comment_info(subitem, post_id, True)
                        dic_list.append(dic)

            if dic_list:
                commentdb.insert_many(dic_list)

        except TypeError as e:
            pass  # 此类由于帖子违规被屏蔽导致的 TypeError 安全忽略
        except Exception as e:
            # 单各帖子评论出错不阻断总流程，跳过即可
            pass


class CommentCrawler(object):

    def __init__(self, stock_symbol: str):
        self.browser = None
        self.symbol = stock_symbol
        self.start = time.time()
        self.post_df = None  # dataframe about the post_url and post_id
        self.current_num = 0

    def create_webdriver(self):
        options = webdriver.ChromeOptions()  # configure the webdriver
        options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             'like Gecko) Chrome/111.0.0.0 Safari/537.36"')
        options.add_argument('--headless=new')  # 使用新版的无头模式，不会弹出实体窗口
        options.add_argument('--window-size=1920,1080') # 为无头模式设置固定分辨率避免渲染异常
        
        self.browser = webdriver.Chrome(options=options)
        # self.browser.set_page_load_timeout(2)  # set the timeout restrict

        current_dir = os.path.dirname(os.path.abspath(__file__))  # hide the features of crawler/selenium
        js_file_path = os.path.join(current_dir, 'stealth.min.js')
        with open(js_file_path) as f:
            js = f.read()
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })

    def find_by_date(self, start_date, end_date):
        # get comment urls through date (used for the first crawl)
        """
        :param start_date: '2003-07-21' 字符串格式 ≥
        :param end_date: '2024-07-21' 字符串格式 ≤
        """
        postdb = MongoAPI('post_info', f'post_{self.symbol}')
        time_query = {
            'post_date': {'$gte': start_date, '$lte': end_date},
            'comment_num': {'$ne': 0}  # avoid fetching urls with no comment
        }
        post_info = postdb.find(time_query, {'_id': 1, 'post_url': 1})  # , 'post_date': 1
        self.post_df = pd.DataFrame(post_info)

    def find_by_id(self, start_id: int, end_id: int):
        # get comment urls through post_id (used when crawler is paused accidentally) crawl in batches
        """
        :param start_id: 721 整数 ≥
        :param end_id: 2003 整数 ≤
        """
        postdb = MongoAPI('post_info', f'post_{self.symbol}')
        id_query = {
            '_id': {'$gte': start_id, '$lte': end_id},
            'comment_num': {'$ne': 0}  # avoid fetching urls with no comment
        }
        post_info = postdb.find(id_query, {'_id': 1, 'post_url': 1})  # , 'post_date': 1
        self.post_df = pd.DataFrame(post_info)

    def crawl_comment_info(self):
        url_df = self.post_df['post_url']
        id_df = self.post_df['_id']
        total_num = self.post_df.shape[0]

        self.create_webdriver()
        parser = CommentParser()
        commentdb = MongoAPI('comment_info', f'comment_{self.symbol}')

        for url in url_df:
            try:
                time.sleep(abs(random.normalvariate(0.03, 0.01)))  # random sleep time

                try:  # sometimes the website needs to be refreshed (situation comment is loaded unsuccessfully)
                    self.browser.get(url)  # this function may also get timeout exception
                    WebDriverWait(self.browser, 0.2, poll_frequency=0.1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.reply_item.cl')))
                except TimeoutException:  # timeout situation
                    self.browser.refresh()
                    print('------------ refresh ------------')
                finally:
                    reply_items = self.browser.find_elements(By.CSS_SELECTOR, 'div.allReplyList > div.replylist_content > div.reply_item.cl')  # some have hot reply list avoid fetching twice

                dic_list = []  # as batch insert is more efficient than insert one
                for item in reply_items:
                    dic = parser.parse_comment_info(item, id_df.iloc[self.current_num].item())
                    # save the related post_id
                    dic_list.append(dic)

                    if parser.judge_sub_comment(item):  # means it has sub-comments
                        sub_reply_items = item.find_elements(By.CSS_SELECTOR, 'li.reply_item_l2')

                        for subitem in sub_reply_items:
                            dic = parser.parse_comment_info(subitem, id_df.iloc[self.current_num].item(), True)
                            # as it has sub-comments
                            dic_list.append(dic)

                commentdb.insert_many(dic_list)
                self.current_num += 1
                print(f'{self.symbol}: 已成功爬取 {self.current_num} 页评论信息，进度 {self.current_num*100/total_num:.3f}%')

            except Exception as e:  # some comment is not allowed to display, just skip it
                self.current_num += 1
                print(f'{self.symbol}: 第 {self.current_num} 页出现了错误 {e} （{url}）')  # maybe the invisible comments
                try:
                    print(f'应爬取的id范围是 {id_df.iloc[0]} 到 {id_df.iloc[-1]}, id {id_df.iloc[self.current_num - 1]} 出现了错误')
                except:
                    pass
                try:
                    self.browser.delete_all_cookies()
                    self.browser.quit()  # restart webdriver if crawler is restricted
                except:
                    pass
                self.create_webdriver()

        end = time.time()
        time_cost = end - self.start
        row_count = commentdb.count_documents()
        self.browser.quit()
        print(f'成功爬取 {self.symbol}股吧 {self.current_num} 页评论，共 {row_count} 条，花费 {time_cost/60:.2f}分钟')
