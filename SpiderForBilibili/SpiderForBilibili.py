import requests
from pyquery import PyQuery as pq
import json
from bs4 import BeautifulSoup
import time
import random
import sys

class SpiderForBilibili:

    def __init__(self):
        self.cookies = self.get_cookies('BilibiliCookies.txt')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        self.script_info = {
            'Title': '',
            'Original Script': 'hishiro-Xiao SpiderForBilibili',
            'Synch Point': '0',
            'ScriptType': 'v4.00+',
            'Collisions': 'Normal',
            'PlayResX': '1280',
            'PlayResY': '720',
            'Timer': '100.0000'
        }
        self.styles = {
            'Format': 'Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
             'Style': 'Default,Wenquanyi Micro Hei,18,&H00FFFFFF,&HF0000000,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,1.5,1,8,30,30,10,134'
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

        self.script_info['Title'] = html('title').text()

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

    # 根据视频的cid获取弹幕库
    def get_danmuku(self, cid: int):
        danmuku_url = 'http://comment.bilibili.com/'+ str(cid) +'.xml'
        r = requests.get(danmuku_url)
        r.encoding = 'utf-8'

        danmuku = []
        soup = BeautifulSoup(r.text, 'lxml')
        for item in soup.find_all('d'):
            
            danmu_attr = item['p'].split(',')
            
            # 根据秒数计算弹幕开始时间和结束时间
            m, s = divmod(float(danmu_attr[0]), 60)
            h, m = divmod(m, 60)
            start =  "%02d:%02d:%02d" % (h, m, s) + '.00'

            m, s = divmod(float(danmu_attr[0]) + 60.0, 60)
            h, m = divmod(m, 60)
            end =  "%01d:%02d:%02d" % (h, m, s) + '.00'
            
            danmu_info = {
                'start': start ,
                'end': end,
                'type': danmu_attr[1],
                'font-size': danmu_attr[2],
                'font-color': danmu_attr[3],
                'content': item.get_text(),
                'y': str(random.randint(0, 350))
            }

            danmuku.append(danmu_info)

        # self.save_content('danmuku.json', json.dumps(danmuku))

        self.xml_to_ass(danmuku)

    def xml_to_ass(self, danmuku):

        def sec_to_time(second: float):
            hour = (second) // 60 // 60
            minute = int(second - hour*60*60) // 60
            sec = second - hour*60*60 - minute*60

            return str(hour) + ':' + str(minute) + ':' + str(sec)

        filepath = self.script_info['Title'] + '.ass'
        with open(filepath, 'w', 100, 'utf-8') as f:
            f.write('[Script Info]\n')
            for key in self.script_info.keys():
                f.write(key + ': ' + self.script_info[key] + '\n')

            f.write('\n[V4+ Styles]\n')
            for key in self.styles.keys():
                f.write(key + ': ' + self.styles[key] + '\n')

            f.write('\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\nComment: 0,0:00:00.00,0:00:00.00,*Default,NTP,0000,0000,0000,,(avant)\n')

            for danmu in danmuku:
                f.write('Dialogue: 0,')
                f.write(danmu['start'] + ',')
                f.write(danmu['end'] + ',')
                f.write('*Default,NTP,0000,0000,0000,,{\move(2000,'+ danmu['y'] +',-2000,'+ danmu['y'] +' [,0,40000])}')
                f.write(danmu['content'])
                f.write('\n')


if __name__ == '__main__':
    spider = SpiderForBilibili()
    
    url = sys.argv[1]

    cid = spider.get_cid(url)
    spider.get_danmuku(cid)
