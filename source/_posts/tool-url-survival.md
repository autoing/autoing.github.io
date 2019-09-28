---
title: Python 资产发现小脚本
categories:
  - 原创工具
date: 2019-9-24 23:24:36
updated: 2019-9-24 23:24:36
comments: true
---

脚本会将URL分割，仅适用于资产发现探测，不适用链接存活检测。

```code
#WEB探测专用，不适用于存活探测
import re
import sys
import time
import queue
import requests
import threading
import telnetlib
from urllib.parse import urlparse
requests.packages.urllib3.disable_warnings()


class GetUrl(object):
    def __init__(self):
        super(GetUrl, self).__init__()
        self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0'}

    def geturl(self,url):
        try:
            response = requests.get(url, verify=False, headers=self.headers, allow_redirects=False,timeout = 15)
            if response.status_code == 301 or response.status_code == 302:
                self.host = urlparse(url)
                self.scheme = self.host.scheme
                self.netloc = self.host.netloc
                location = response.headers['Location']
                if self.netloc.split(':')[0] in location or location[0:4].lower() == 'http':
                    get_url = location
                else:
                    if location[0] != '/' or location[0:4].lower() != 'http':
                        get_url = '{}://{}/{}'.format(self.scheme,self.netloc,location)
                response = requests.get(get_url, verify=False, headers=self.headers, allow_redirects=False,timeout = 15)
                get_url = response.url
            else:
                get_url = response.url

            return [get_url,response.text,response.status_code]
        except Exception as e:
            pass

class Waittask(threading.Thread):
    def run(self):
        self.telnet = telnetlib.Telnet()
        while True:
            if asset.qsize() < 500:
                for i in range(500):
                    host = urlparse(waittask.get())
                    self.scheme = host.scheme
                    self.netloc = host.netloc
                    try:
                        if ':' in self.netloc:
                            Host = self.netloc.split(':')
                            self.telnet.open(Host[0],Host[1],timeout = 3)
                            asset.put('{}://{}:{}'.format(self.scheme,Host[0],Host[1]))
                        elif self.scheme == 'https':
                            self.telnet.open(self.netloc,443,timeout = 3)
                            asset.put('{}://{}'.format(self.scheme,self.netloc))
                        else:
                            self.telnet.open(self.netloc,80,timeout = 3)
                            asset.put('{}://{}'.format(self.scheme,self.netloc))
                    except Exception as e:
                        pass
            time.sleep(1)

class Asset(threading.Thread):
    def run(self):
        while True:
            while not asset.empty():
                url = asset.get()
                # return [get_url,response.text,response.status_code]
                info = GetUrl().geturl(url)
                self.get_url = info[0]
                self.content = info[1]
                self.status_code = info[2]
                if self.status_code == 301 or self.status_code == 302:
                    while True:
                        info = GetUrl().geturl(self.get_url)
                        if info:
                            if info[2] != 301 or info[2] != 302:
                                self.get_url = info[0]
                                self.content = info[1]
                                self.status_code = info[2]
                                break
                            else:
                                self.get_url = info[0]
                    self.url_title = get_title(self.content)
                else:
                    self.url_title = get_title(self.content)

                print(self.status_code,self.get_url,self.url_title)
                get.put([url,self.status_code,self.get_url,self.url_title])
            time.sleep(1)

class Check(threading.Thread):
    def run(self):
        while True:
            time.sleep(10)
            print('进度：{:.2%} 当前还有{}个端口开放检测，{}个WEB探测任务未完成！'.format(1-waittask.qsize()/sums,waittask.qsize(),asset.qsize()))
            while not get.empty():
                assets = get.get()
                with open('survival.txt','a',encoding='gb18030') as cent:
                    cent.write('{}|{}|{}|{}\n'.format(assets[0],assets[1],assets[2],assets[3]))

def get_title(text):
    try:
        title = re.findall('<title>(.*?)</title>',text.encode('iso-8859-1').decode('utf-8').lower())[0].strip()
    except Exception as e:
        try:
            title = re.findall('<title>(.*?)</title>',text.encode('iso-8859-1').decode('gbk').lower())[0].strip()
        except Exception as e:
            try:
                title = re.findall('<title>(.*?)</title>',text.lower())[0].strip()
            except Exception as e:
                title = '获取标题失败'
    return title

if __name__ == '__main__':
    file = sys.argv[1]
    waittask = queue.Queue()
    asset = queue.Queue()
    get = queue.Queue()

    with open(file) as content:
        for cent in content:
            waittask.put(cent.strip())
    sums = int(waittask.qsize())

    for i in range(100):
        Waittask_ = Waittask()
        Waittask_.start()

    for i in range(100):
        Asset_ = Asset()
        Asset_.start()

    check = Check()
    check.start()
```