import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import requests
import re
import time
from fake_useragent import UserAgent

lis = [
    "行为金融",
]

def find_with_length_condition(pattern, text, max_length=100):
    matches = re.finditer(pattern, text, re.S)
    filtered_matches = [match.group(1) for match in matches if len(
        match.group(1)) <= max_length]
    return filtered_matches


for i in lis:

    params = {"search_query": i}

    url = "https://www.youtube.com/results"

    headers = {
        'authority': 'www.youtube.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        # 'cache-control': 'max-age=0',
        # 'cookie': 'VISITOR_INFO1_LIVE=Jh5b0BA7IKI; LOGIN_INFO=AFmmF2swRgIhAIk8N2Ys-JD8lKHTyd04yoGdC0KS4HUtZYaG9B7rJkCwAiEA-K75FBMSZzD0Po41SVlj4fbiszZ1aVD3snbEpwv8atA:QUQ3MjNmeU5lRWVxaDhYVVp4SVdBQU00TzVITmgxT0dGMHphTUo1TGx1cWhYUERYem9BdFcyNWJyWXg4aEp4N2hZVnZ6cHdnYnZsSW0tS0ZGcmtlYzJkRjB6NGNNSWkyUzBURHV6STRqS3FKZFNmVDBRZk1mYnhWSktEbFVpcEVGMXdKazI0YkJySjh4R3NhVzZKVTRINURLQ2t6SllwNm9n; HSID=A09qMwNaGu0ETJrzH; SSID=A4NHS3TLMsfX2GJ8y; APISID=l8vlNB5of__ASqa9/ASK-XUFzyxHGpWCtV; SAPISID=NyfvTkHVeVd0KJYp/A2O4or7w-JNdpWhos; __Secure-1PAPISID=NyfvTkHVeVd0KJYp/A2O4or7w-JNdpWhos; __Secure-3PAPISID=NyfvTkHVeVd0KJYp/A2O4or7w-JNdpWhos; VISITOR_PRIVACY_METADATA=CgJVUxIEGgAgHw%3D%3D; SID=eAhnvMJRKovevafkx6SkcGTIt5oVjd-Ss3H3D7JfRs7QhReR4GgqI21OrkqMu906L_SR3Q.; __Secure-1PSID=eAhnvMJRKovevafkx6SkcGTIt5oVjd-Ss3H3D7JfRs7QhReRa2_OtQXEvMiKvneIpJXofQ.; __Secure-3PSID=eAhnvMJRKovevafkx6SkcGTIt5oVjd-Ss3H3D7JfRs7QhReRkabf_tjg8Zoz9GZIkR3gBQ.; YSC=LsIYJ8J5PcU; wide=1; NID=511=NjyynT12c23GjgUK9lXM_-I2FV0JvZzdJXORMF_MZQ2PzpNR6cMphJiB8vb2AiEryDfdydC8PletjtrJeloMekaWw6Ag5AUGVczHtIycMG53QOJ1eTLev7hso9ZCB3wy6DZVnMhZVp8doOtZ8dcjQp9Ns4M10WFbZxNUd3YgRNY5eYBE-_nhRGl-qTebNxrrK4q3Agf_2dT3; PREF=tz=Asia.Shanghai&f7=100&gl=US&f5=30000&f4=4000000; __Secure-1PSIDTS=sidts-CjEBPVxjSoJ5AhzrfY7GN58w-6g-Hf4ilmg2v15sZ0AHC8aeXxphiNDADzU_3Gt3wlQEEAA; __Secure-3PSIDTS=sidts-CjEBPVxjSoJ5AhzrfY7GN58w-6g-Hf4ilmg2v15sZ0AHC8aeXxphiNDADzU_3Gt3wlQEEAA; SIDCC=ABTWhQHkkm94ZG9WN6OzEIrDeLUfMKoSBc39ZZLX6ioBM8AOIMkJt0iF9v1OwtPd79utN-OrE8o; __Secure-1PSIDCC=ABTWhQHYTsI2d1nMEXEJxy34B18umkg9CSKrAEz01uHdzMmdRi_VMNGElHqiyMqTrwpY0iUJeeY; __Secure-3PSIDCC=ABTWhQFP6lRKKptC0tg6A2iLTuGDG-zf0rGrPirVIwYOfQfaWCUK-Vrw1v09ntr8RoE2fNkED3iL',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"120.0.6099.71"',
        'sec-ch-ua-full-version-list': '"Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.71", "Google Chrome";v="120.0.6099.71"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"10.0.0"',
        'sec-ch-ua-wow64': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'service-worker-navigation-preload': 'true',
        'upgrade-insecure-requests': '1',
        'user-agent': UserAgent().random
    }

    response = requests.get(url=url, headers=headers, params=params)
    if response.status_code == 200:
        text = response.text
    else:
        exit()
    pattern = r'{"webCommandMetadata":{"url":"/watch\?v=(.*?)\\'

    matched_strings = find_with_length_condition(pattern, text)

    print("搜索: %s, 一共查询到 %d 条 url" %
          (params["search_query"], len(matched_strings)))

    file_path = "./crawler/subtitles/financialURLs.txt"

    with open(file_path, 'a') as file:
        for string in matched_strings:
            file.write(string + '\n')

    time.sleep(5)
