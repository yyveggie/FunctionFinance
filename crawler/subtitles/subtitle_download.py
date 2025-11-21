import os
import time
import requests
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

file_path = "./crawler/subtitles/financialURLs.txt"
already_read_file_path = "./crawler/subtitles/id_already_read.txt"

def save(title, content, language):
    os.makedirs(f"./sub/{language}", exist_ok=True)
    with open(f"./sub/{language}/{title}.txt", 'w', encoding='utf-8') as file:
        file.write(content)
        print(f"已保存字幕: ./sub/{language}/{title}.txt")

def read_already_processed_ids():
    try:
        with open(already_read_file_path, 'r') as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def save_processed_id(id):
    with open(already_read_file_path, 'a') as file:
        file.write(id + '\n')

def main(delay=3):
    already_processed_ids = read_already_processed_ids()

    with open(file_path, 'r') as file:
        ids = set(file.read().splitlines()) - already_processed_ids

    print("原始 id 共有 %d 条" % (len(ids)))

    for i, id in enumerate(ids, 1):
        print(f"当前正在爬取第 {i} / {len(ids)} 个 id :", id)

        text_split = []
        try:
            content_cn = YouTubeTranscriptApi.get_transcript(id, languages=['zh-Hans', 'zh-Hant', 'zh-HK'])
            for j in content_cn:
                text_split.append(j["text"])
            text = '，'.join(text_split)
            save(id, text, "cn")
            save_processed_id(id)
        except NoTranscriptFound:
            try:
                content_en = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
                for j in content_en:
                    text_split.append(j["text"])
                text = ', '.join(text_split)
                save(id, text, "en")
                save_processed_id(id)
            except NoTranscriptFound:
                continue
        except TranscriptsDisabled:
            print(f"视频 {id} 的字幕被禁用。")
            save_processed_id(id)
            continue
        except requests.exceptions.SSLError as e:
            print(f"在处理视频 {id} 时遇到 SSL 错误: {e}")
            time.sleep(60)
            continue
        except KeyError:
            continue
        
        time.sleep(delay)

main()