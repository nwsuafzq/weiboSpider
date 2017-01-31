#-*-coding:utf8-*-
#-------------------------------------
#       张琼 西北农林科技大学 计算机141
#         2017年1月31日 20:09:08
# ------------------------------------
import re
import string
import sys
import os
import urllib
import urllib2
from bs4 import BeautifulSoup
import requests
import shutil
import time
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf-8')
# if(len(sys.argv)>=2):
#        user_id = (int)(sys.argv[1])
# else:
#        user_id = (int)(raw_input(u"please_input_id: "))
user_id = 3805842931  #微博用户ID
cookie = {"Cookie": "_T_WM=6a0975bd8ce171d2c8b31e48d27993b7; ALF=1488452559; SCF=Aphq2I26dyB0N2ikBftYqeJKmR_jZE3ZQPpZ78yMq5h81f2xcKuQaFOIrBttHnTRrdjH3AFD9iDcHs6SKBQDyRQ.; SUB=_2A251lB6GDeRxGeNM4lQZ-S_Jzz6IHXVXdqLOrDV6PUJbktBeLXTTkW2fnHFXxkcPdpyC7aArA3VvccZDXg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWug7UMvAm9Pg91a_h6o8Ye5JpX5o2p5NHD95Qfeo.c1h.pSKBEWs4DqcjZBXxCPXSQqg4rB7tt; SUHB=05i62K5ms4yYQ4; SSOLoginState=1485860566"}
url = 'http://weibo.cn/u/%d?filter=1&page=1'%user_id
html = requests.get(url, cookies = cookie).content
print u'user_id和cookie读入成功'
selector = etree.HTML(html)
pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])



result = ""
urllist_set = set()
word_count = 1
image_count = 1

print u'ready'
print pageNum
sys.stdout.flush()

times = 5
one_step = pageNum/times
for step in range(times):
    if step < times - 1:
        i = step * one_step + 1
        j =(step + 1) * one_step + 1
    else:
        i = step * one_step + 1
        j =pageNum + 1
    for page in range(i, j):
        #获取lxml页面
        try:
            url = 'http://weibo.cn/u/%d?filter=1&page=%d'%(user_id,page)
            lxml = requests.get(url, cookies = cookie).content
            #文字爬取
            selector = etree.HTML(lxml)
            content = selector.xpath('//span[@class="ctt"]')
            for each in content:
                text = each.xpath('string(.)')
                if word_count >= 3:
                    text = "%d: "%(word_count - 2) +text+"\n"
                else :
                    text = text+"\n\n"
                result = result + text
                word_count += 1
            print page,'word ok'
            sys.stdout.flush()
            soup = BeautifulSoup(lxml, "lxml")
            urllist = soup.find_all('a',href=re.compile(r'^http://weibo.cn/mblog/oripic',re.I))
            urllist1 = soup.find_all('a',href=re.compile(r'^http://weibo.cn/mblog/picAll',re.I))
            for imgurl in urllist:
                imgurl['href'] = re.sub(r"amp;", '', imgurl['href'])
        #       print imgurl['href']
                urllist_set.add(requests.get(imgurl['href'], cookies = cookie).url)
                image_count +=1
            for imgurl_all in urllist1:
                html_content = requests.get(imgurl_all['href'], cookies = cookie).content
                soup = BeautifulSoup(html_content, "lxml")
                urllist2 = soup.find_all('a',href=re.compile(r'^/mblog/oripic',re.I))
                for imgurl in urllist2:
                    imgurl['href'] = 'http://weibo.cn' + re.sub(r"amp;", '', imgurl['href'])
                    urllist_set.add(requests.get(imgurl['href'], cookies = cookie).url)
                    image_count +=1
                image_count -= 1
            print page,'picurl ok'
        except:
            print page,'error'
        # print page, 'sleep'
        sys.stdout.flush()
        #time.sleep(60)
    # print u'正在进行第', step + 1, u'次停顿，防止访问次数过多'
    #time.sleep(300)

try:
    isExists=os.path.exists(os.getcwd()+"/%s"%user_id)
    if not isExists:
        os.mkdir(os.getcwd()+"/%s"%user_id)
        # userpath=os.getcwd()+"/%s"%user_id
    else:
        print "目录存在"
    userpath=os.getcwd()+"/%s"%user_id
    fo = open(userpath+"/%s"% user_id, "wb")
    fo.write(result)
    # word_path=os.getcwd()+'/%s'% user_id

    print u'文字微博爬取完毕'
    link = ""
    fo2 = open(userpath+"/%s_imageurls"% user_id, "wb")
    for eachlink in urllist_set:
        link = link + eachlink +"\n"
    fo2.write(link)
    print u'图片链接爬取完毕'
except:
    print u'存放数据地址有误'
sys.stdout.flush()

if not urllist_set:
    print u'该用户原创微博中不存在图片'
else:
    #下载图片,保存在当前目录的pythonimg文件夹下
    image_path=userpath+'/weibo_image'
    if os.path.exists(image_path) is False:
        os.mkdir(image_path)
    x = 1
    for imgurl in urllist_set:
        temp= image_path + '/%s.jpg' % x
        print u'正在下载第%s张图片' % x
        try:
        # urllib.urlretrieve(urllib2.urlopen(imgurl).geturl(),temp)
            r = requests.get(imgurl, stream=True)
            if r.status_code == 200:
                with open(temp, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
        except:
            print u"该图片下载失败:%s"%imgurl
        x += 1
print u'原创微博爬取完毕，共%d条，保存路径%s'%(word_count - 3,userpath)
print u'微博图片爬取完毕，共%d张，保存路径%s'%(image_count - 1,image_path)
