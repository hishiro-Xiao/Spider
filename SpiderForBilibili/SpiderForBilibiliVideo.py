import requests
from pyquery import PyQuery as pq
import json
import sys

class SpiderForBilibili:

    def __init__(self):
        self.cookies = self.get_cookies('BilibiliCookies.txt')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }

    def get_cookies(self, path: str):
        '''
            获取文件中的Cookies信息
        '''
        with open(path, 'r') as f:
            _cookies = {}
            for row in f.read().split(';'):
                key, value = row.strip().split('=', 1)
                _cookies[key] = value
            return _cookies

    def save_content(self, filepath: str, content: str):
        '''
            将指定内容保存到文件中
        '''
        f = open(filepath, 'w', 100, 'utf-8')
        f.write(str(content))
        f.close()

    # 根据视频的链接，获取视频的cid，cid是获取视频弹幕的唯一标志
    def get_cid(self, url: str):
        r = requests.get(url, headers=self.headers, cookies=self.cookies)
        html = pq(r.text, parser='html')
        self.title = html('title').text()       # 视频标题

        # 视频信息会初始化加载在网页的script标签中（实际保存在window.__INITIAL_STATE__对象中）
        for script in html('script').items():
            if script.text()[0:24] == 'window.__INITIAL_STATE__':
                
                info = script.text()[25: script.text().index(';')]     # 因为是script标签，所有需要过滤掉js脚本（js脚本使用分号分割）
                info_json = json.loads(info)                             
                
                # 如果是番剧类视频，cid会保存在epInfo中，其他视频的，都保存在videoData中
                if 'videoData' in info_json:
                    cid = info_json['videoData']['cid']
                else:
                    cid = info_json['epInfo']['cid']
                return cid

    def get_vedio(self,url):
        cid = self.get_cid(url)

        href = 'https://api.bilibili.com/pgc/player/web/playurl?cid='+ str(cid) +'&qn=80'
        self.headers['referer'] = href

        r = requests.get(href, headers=self.headers, cookies=self.cookies)
        json_obj = json.loads(r.text)

        urls = []
        for item in json_obj['result']['durl']:
            urls.append(item['url'])

        self.save_content('urls.json', json.dumps(urls))
        
        r = requests.get(urls[0], headers=self.headers, cookies=self.cookies, stream=True)
        chunk_size = 1024
        content_size = int(r.headers['content-length'])
        print('下载开始')
        with open(self.title + '.flv', "wb") as f:
            n = 1
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                f.flush()
                loaded = n*1024.0/content_size
                print('已下载{0:%}'.format(loaded))
                n += 1

if __name__ == '__main__':
    spider = SpiderForBilibili()
    
    url = sys.argv[1]

    spider.get_vedio(url)
    
