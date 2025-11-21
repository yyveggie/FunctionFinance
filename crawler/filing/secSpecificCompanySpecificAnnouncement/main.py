import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 SEC 下载指定公司，指定数量的Filings。
    目前经常会出现这个错误，暂时搁置：ValueError: Input object is not an XML element: lxml.etree._ProcessingInstruction
'''
import datetime
import time
import json
from proxy_pool.usable_ip import Usable_IP
from data_connection.mongodb import MongoConnection
from collections import defaultdict
from crawler.filing.secSpecificCompanySpecificAnnouncement.sec_filings import SECExtractor
import concurrent.futures


class SECFilingsLoader(Usable_IP):
    def __init__(self, args={}):
        self.tickers = [item[0] for item in args["ticker"]]
        self.amount = args["sec_filings_amount"]
        self.filing_type = args["filing_type"]
        self.num_workers = args["num_workers"]
        self.include_amends = False
        assert self.filing_type in [
            "10-K",
            "10-Q",
        ], "The supported document types are 10-K and 10-Q"
        self.db_connection = MongoConnection('Filing')
        self.collection = "sec"
        self.se = SECExtractor(
            tickers=self.tickers,
            amount=self.amount,
            filing_type=self.filing_type,
            include_amends=self.include_amends
        )

    def multiprocess_run(self, tic):
        tic_dict = self.se.get_accession_numbers(tic)
        text_dict = defaultdict(list)
        for tic, fields in tic_dict.items():
            print(f"Started for {tic}")
            field_urls = [field["url"] for field in fields]
            years = [field["year"] for field in fields]
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=self.num_workers
            ) as executor:
                results = executor.map(self.se.get_text_from_url, field_urls)
            for idx, res in enumerate(results):
                all_text, filing_type = res
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                text_dict[tic].append(
                    {
                        "fetch_time": timestamp,
                        "source": "SEC",
                        "year": years[idx],
                        "ticker": tic,
                        "all_texts": all_text,
                        "filing_type": filing_type,
                    }
                )
        return text_dict

    def load_data(self):
        all_data = []
        start = time.time()
        thread_workers = min(len(self.tickers), self.num_workers)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=thread_workers
        ) as executor:
            results = executor.map(self.multiprocess_run, self.tickers)
        for res in results:
            all_data.extend(res.values())
            curr_tic = list(res.keys())[0]
            for data in res[curr_tic]:
                curr_year = data["year"]
                curr_filing_type = data["filing_type"]
                if curr_filing_type in ["10-K/A", "10-Q/A"]:
                    curr_filing_type = curr_filing_type.replace("/", "")
                self.collection.insert_one(data)
                print(
                    f"Done for {curr_tic} for document {curr_filing_type} and year"
                    f" {curr_year}"
                )
        print(f"It took {round(time.time()-start,2)} seconds")
        return json.dumps(all_data, default=str, indent=4)


if __name__ == '__main__':
    from config import config
    c = SECFilingsLoader(config)
    print(c.load_data())
