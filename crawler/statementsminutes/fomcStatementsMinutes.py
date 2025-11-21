import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从美国联邦公开市场委员会(Federal Open Market Committee, FOMC)下载最新的会议纪要。
    FOMC 大概每个月举行一次会议, 所以不用经常运行。
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from bson.binary import Binary
from lxml import etree
import pdfplumber
import io
import requests

class TranscriptError(Exception):
    pass


class FOMC_Statements_Minutes(Usable_IP):
    def __init__(self, args={}):
        super().__init__(args)
        self.db_connection = MongoConnection('Statements_Minutes')
        self.source = "fomc"
        self.headers = {
            'authority': 'www.federalreserve.gov',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'referer': 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random
        }

    def download(self):
        url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
        text = self.request_get_sync(url=url, headers=self.headers)
        res = etree.HTML(text, parser=None)
        all = res.xpath("(//div[@class='panel panel-default'])")
        for i in all:
            years = i.xpath('./div[1]/h4/a/text()')
            months = i.xpath(
                "./div[position()>1 and position()<last()]/div[1]/strong/text()")
            days = i.xpath(
                "./div[position()>1 and position()<last()]/div[2]/text()")
            statements_pdfs = i.xpath(
                './div[position()>1 and position()<last()]/div[3]/a[contains(text(), "PDF")]/@href')
            press_conference = i.xpath(
                './div[position()>1 and position()<last()]/div[4]/a[1]/@href')

            for z in range(len(statements_pdfs)):
                statements = self.download_pdf(url=statements_pdfs[z], name=years[0].replace(
                    ' ', '_')+'_'+months[z].replace('/', '_')+'_'+days[z].replace('*', '')+'_'+'statements_pdf')
                break
            for c in range(len(press_conference)):
                try:
                    press_conference_transcript = self.download_transcript(url=press_conference[c], name=years[0].replace(
                        ' ', '_')+'_'+months[c].replace('/', '_')+'_'+days[c].replace('*', '')+'_'+'press_conference_transcript')
                    break
                except TranscriptError:
                    print("Transcript not found for this iteration, moving on...")
                    continue
            data = {
                "statement": statements,
                "press_conference_transcript": press_conference_transcript,
            }
            break
        return data

    def download_pdf(self, url, name):
        base_url = 'https://www.federalreserve.gov'
        response = requests.get(url=base_url + url, headers=self.headers)
        try:
            binary_pdf = Binary(response.content)
            pdf_document = {
                "file": binary_pdf
            }
            self.db_connection.save_data(name, self.source, pdf_document)

            with io.BytesIO(response.content) as open_pdf_file:
                with pdfplumber.open(open_pdf_file) as pdf:
                    text = ''
                    for page in pdf.pages:
                        text += page.extract_text() or ''
            return text
        except Exception as e:
            print(f"处理 PDF 失败: {e}")

    def download_transcript(self, url, name):
        base_url = 'https://www.federalreserve.gov'
        if url[0: 4] == 'http':
            base_url = ''
        res = requests.get(url=base_url+url, headers=self.headers)
        res = etree.HTML(res.text)  # type: ignore
        try:
            pdf_url = res.xpath(
                '//a[contains(text(), "Transcript (PDF)")]/@href')[0]
        except IndexError:
            try:
                pdf_url = res.xpath(
                    '//a[contains(text(), "Press Conference Transcript")]/@href')[0]
            except IndexError:
                raise TranscriptError("No transcript found")
        return self.download_pdf(url=pdf_url, name=name)


if __name__ == "__main__":
    from config import config
    c = FOMC_Statements_Minutes(config)
    print(c.download())
