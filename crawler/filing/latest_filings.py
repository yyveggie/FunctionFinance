import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.mongodb import AsyncMongoConnection, MongoConnection
from unstructured.partition.html import partition_html
from sec_downloader import Downloader
import asyncio

dl = Downloader("SUFE", "yyveggie@gmail.com")
db_connection = AsyncMongoConnection('SEC_Filings')

async def get_latest_filings(ticker, type):
    # Download the latest 10-Q filing
    html = dl.get_filing_html(ticker=ticker, form=type)
    return html

async def parse_file(html):
    text = html.decode()
    elements = partition_html(text=text)
    content = "\n".join([str(el) for el in elements])
    return content

async def save_file(text, ticker, type):
    data = {'text': text}
    await db_connection.save_data(ticker, type, data)

async def process_ticker(ticker, type):
    html = await get_latest_filings(ticker, type)
    text = await parse_file(html)
    await save_file(text, ticker, type)

async def main(tickers, type):
    tasks = []
    for ticker in tickers:
        task = asyncio.create_task(process_ticker(ticker, type))
        tasks.append(task)
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    tickers = ['AAPL', 'TSLA']
    type = '10-Q'
    asyncio.run(main(tickers, type))