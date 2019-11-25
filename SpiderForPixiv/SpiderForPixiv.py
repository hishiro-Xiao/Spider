import requests
from pyquery import PyQuery as pq
import json
import os
import sys

class SpiderForPixiv:

    def __init__(self):
        self.cookies = self.get_cookies('PixivCookies.txt')
        self.headers = {
            'User-Agent': 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
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

    def save_comtent(self, filepath: str, content: str):
        '''
            将指定内容保存到文件中
        '''
        f = open(filepath, 'w', 100, 'utf-8')
        f.write(str(content))
        f.close()

    def download_pictures(self, img_url: str, illust_id: str):
        '''
            将图片下载到指定路径
        '''
        img_headers = {
            'referer': 'https://www.pixiv.net/artworks/' + illust_id
        }
        r = requests.get(img_url, headers=img_headers)
        suffix = img_url[-3:]

        if not os.path.exists('Pixiv'):
            os.mkdir('Pixiv')

        with open('Pixiv/' + illust_id + '.' + suffix, 'wb') as f:
            f.write(r.content)
        
        print('Picture ' + illust_id + ' downloaded.')

    def get_pic_url(self, pic: str, illust_id: str):
        '''
            获取单张图片的保存路径
        '''
        r = requests.get(pic, headers=self.headers, cookies=self.cookies)
        html = pq(r.text)
        d = html('meta:last').attr('content')
        j = json.loads(d)['illust'][illust_id]['urls']
        return j

    def get_pic_json(self, pic_num: int):
        '''
            直接根据网站提供的json文件获取图片列表
        '''
        # Pixiv每页有50张图片，所以计算需要的页数
        pages = pic_num // 50 + 1
        if pic_num <= 50:
            pages = 1
        
        for i in range(1, pages + 1):
            url = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=' + str(i) + '&format=json'
            r = requests.get(url, headers=self.headers, cookies=self.cookies)
            html = json.loads(r.text)

            illust_list = []
            for item in html['contents']:
                illust_list.append('https://www.pixiv.net/artworks/' + str(item['illust_id']))
            
            for item in illust_list:
                links = self.get_pic_url(item, item[-8:])
                if links['original'] != '':
                    self.download_pictures(links['original'], item[-8:])
                    pic_num -= 1
                else:
                    print('No original picture.')

                if pic_num <= 0:
                    exit('All Pictures are Downloaded')

if __name__ == '__main__':
    
    spider = SpiderForPixiv()
    img_num = 50
    if len(sys.argv) > 1:
        img_num = sys.argv[1]

    spider.get_pic_json(int(img_num))
    print('All pictures are downloaded.')
