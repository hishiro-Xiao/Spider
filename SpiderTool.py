import requests
from pyquery import PyQuery as pq

class SpiderTool:
    @staticmethod
    def getCookie(filepath):
        '''
            获取文件中的Cookies信息
        '''
        with open(filepath, 'r') as f:
            _cookies = {}
            for row in f.read().split(';'):
                key, value = row.strip().split('=', 1)
                _cookies[key] = value
            return _cookies 

    @staticmethod
    def saveContent(content, filepath):
        '''
            将指定内容保存到指定路径
        '''
        with open(filepath, 'w', 100, 'utf-8') as f:
            f.write(str(content))
            f.close()

    @staticmethod
    def getContent(url, headers=None, cookiePath=None):
        '''
            根据链接获取网页内容
            @parameter:
                header
                cookies
        '''
        try:
            cookies = SpiderTool.getCookie(cookies) if cookiePath is not None else None
            r = requests.get(url, headers=headers)
            r.encoding = 'utf-8'
            html = pq(r.text, parser='html')
            return html
        except:
            print('An error happened')
            return None