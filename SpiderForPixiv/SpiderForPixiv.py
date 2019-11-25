import requests
from pyquery import PyQuery as pq
import json

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

    def get_pic_json(self, content: str):
        '''
            直接根据网站提供的json文件获取图片列表
        '''
        html = json.loads(content)
        illust_list = []
        for item in html['contents']:
            illust_list.append('https://www.pixiv.net/artworks/' + str(item['illust_id']))
        
        # json_str = json.dumps(illust_list)
        # self.save_comtent('pic_lists.json', json_str)

        for item in illust_list:
            links = self.get_pic_url(item, item[-8:])
            if links['original'] != '':
                self.download_pictures(links['original'], item[-8:])
            else:
                print('No original picture.')


if __name__ == '__main__':
    
    spider = SpiderForPixiv()
    url = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=1&format=json'
    r = requests.get(url, headers=spider.headers, cookies=spider.cookies)
    content = r.text
    
    spider.get_pic_json(content)
