---
title: Python Acunetix Web Vulnerability Scanner 11 批量扫描脚本[AWVS11批量扫描脚本]
categories:
  - 原创工具
date: 2018-10-3 01:04:01
updated: 2018-10-3 03:04:01
comments: true
---

------
{% fold 点击显/隐内容 %}
```python
import json
import queue
import requests
requests.packages.urllib3.disable_warnings()

class AwvsScan(object):
    def __init__(self):
        self.scanner = 'https://127.0.0.1/'
        self.key = '1986ad8c0a5b3df4d7028d5f3c06e286c1003632f31f2423599bfb945100ce3de'
        self.ScanMode = '11111111-1111-1111-1111-111111111111'
        self.headers = {'X-Auth': self.key, 'content-type': 'application/json'}
        self.targets_id = queue.Queue()
        self.scan_id = queue.Queue()
        self.site = queue.Queue()

    def main(self):
        print('='*80)
        print("""1、使用awvs.txt添加扫描任务\n2、删除所有任务""")
        print('='*80)
        choice = input(">")
        if choice == '1':
            self.scans()
        if choice == '2':
            self.del_targets()
        self.main()

    def openfile(self):
        with open('awvs.txt') as cent:
            for web_site in cent:
                web_site = web_site.strip('\n\r')
                self.site.put(web_site)

    def targets(self):
        self.openfile()
        while not self.site.empty():
            website = self.site.get()
            try:
                data = {'address':website,
                        'description':'awvs-auto',
                        'criticality':'10'}
                response = requests.post(self.scanner + '/api/v1/targets', data=json.dumps(data), headers=self.headers, verify=False)
                cent = json.loads(response.content)
                target_id = cent['target_id']
                self.targets_id.put(target_id)
            except Exception as e:
                print('Target is not website! {}'.format(website))

    def scans(self):
        self.targets()
        while not self.targets_id.empty():
            data = {'target_id' : self.targets_id.get(),
                    'profile_id' : self.ScanMode,
                    'schedule' : {'disable': False, 'start_date': None, 'time_sensitive' : False}}

            response = requests.post(self.scanner + '/api/v1/scans', data=json.dumps(data), headers=self.headers, allow_redirects=False, verify=False)
            if response.status_code == 201:
                cent = response.headers['Location'].replace('/api/v1/scans/','')
                print(cent)

    def get_targets_id(self):
        response = requests.get(self.scanner + "/api/v1/targets", headers=self.headers, verify=False)
        content = json.loads(response.content)
        for cent in content['targets']:
            self.targets_id.put([cent['address'],cent['target_id']])

    def del_targets(self):
        self.get_targets_id()
        while not self.targets_id.empty():
            targets_info = self.targets_id.get()
            response = requests.delete(self.scanner + "/api/v1/targets/" + targets_info[1], headers=self.headers, verify=False)
            if response.status_code == 204:
                print('delete targets {}'.format(targets_info[0]))

if __name__ == '__main__':
    Scan = AwvsScan()
    Scan.main()
```
{% endfold %}

------