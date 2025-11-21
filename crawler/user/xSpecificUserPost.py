import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    使用 Nitter 从 X 下载指定用户的推文。
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from tenacity import retry, wait_fixed, stop_after_attempt
from ntscraper import Nitter
import pandas as pd


class X_Specific_User_Post(Usable_IP):
    def __init__(self, args={}):
        super().__init__(args)
        self.users = args['user']
        self.dataframe = pd.DataFrame()
        self.db_connection = MongoConnection('User')
        self.source = 'x'
        self.no = 5

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(5))
    def download(self):
        alldata = {}
        self.scarper = Nitter()
        for user in self.users:
            xs = self.scarper.get_tweets(
                terms=user, mode='user', number=self.no)
            final_data = []
            for x in xs['tweets']:
                data = [x['text'], x['date'], x['stats']['likes']]
                final_data.append(data)
            dataframe = pd.DataFrame(final_data, columns=[
                                     'text', 'date', 'No_of_Likes'])
            dict_data = dataframe.to_dict(orient='split')
            self.db_connection.save_data(user, self.source, dict_data)
            alldata[user] = dict_data
        return alldata


if __name__ == "__main__":
    from config import config
    c = X_Specific_User_Post(config)
    print(c.download())
