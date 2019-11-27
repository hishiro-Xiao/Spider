# Spider
 python spider tools

- PixivForPixiv
 
  下载Pixiv的“今日排行榜的”图片，保存到当前路径下的Pixiv文件夹下

  使用方式：
  
    `
    python  SpiderForPixiv.py [num] | num为图片数量，默认为50
    ` 
    
    注：Pixiv每日排行榜只包含500张图片，所以num最大值为500

- PixivForBilibili
  
    下载指定url视频的弹幕

    使用方式：
  
    `
    python  SpiderForBilibili.py https://www.bilibili.com/bangumi/play/ep289520?theme=movie
    ` 

    弹幕会以.ass形式的外挂字幕文件保存在当前文件夹

    需要改进的地方：

      1. 弹幕会有重叠现象出现
      2. 不支持部分播放器
      3. 弹幕加载有时会很卡