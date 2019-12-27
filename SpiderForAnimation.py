from SpiderTool import SpiderTool
import requests
from bs4 import BeautifulSoup
import json

class SpiderForAnimation:
    def __init__(self):
        self.headers = {
            'User-Agent': 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }

    def getAniList(self, url):
        html = SpiderTool.getContent(url, self.headers)

        # 获取某季度。所有的视频页链接
        animList = {}
        content = html('div.anime_list dd h3 a')
        
        # 如果没有获取到，直接返回
        if content is None:
            return None
        for a in content.items():
            title = str(a.text())
            animList[title] = 'http://www.dilidili.one' + a.attr('href')
        
        # 获取各个番剧的下载链接
        downloadList = {}
        for item in animList.items():
            title, link = item
            html = SpiderTool.getContent(link, self.headers)
            
            dlink = html('div.time_pic div.time_con:nth-child(2) a:first-child').attr('href') if html is not None else ''
            code = html('div.time_pic div.time_con:nth-child(2) a:first-child').text()[-4:] if html is not None else ''
            if len(code) != 4:
                code = ''
            downloadList[title] = {'下载链接':dlink, '提取码':   code}

            print(title + ' get')

        season = url[30:-1]
        SpiderTool.saveContent(json.dumps(downloadList), season + '.json')
        print('---------' + season[0:4] + '年' + season[4:] + '月番剧 get ---------')
        print()
        
        return downloadList


    def getAllAniList(self):
        links = []
        for i in range(2019, 2010, -1):
            links.append('http://www.dilidili.one/anime/' + str(i) + '10/')
            links.append('http://www.dilidili.one/anime/' + str(i) + '07/')
            links.append('http://www.dilidili.one/anime/' + str(i) + '04/')
            links.append('http://www.dilidili.one/anime/' + str(i) + '01/')
        
        links.append('http://www.dilidili.one/anime/2010xq/')
        links.append('http://www.dilidili.one/anime/2000xqq/')

        allLinks = {}
        try:
            for link in links:
                dLinks = self.getAniList(link)
                allLinks.update(dLinks)
        except:
            print('An error happened')
            SpiderTool.saveContent(json.dumps(allLinks), 'Animations.json')
            exit()
        

if __name__ == '__main__':
    
    s = SpiderForAnimation()
    s.getAllAniList()
    # print(s.getAniList())
