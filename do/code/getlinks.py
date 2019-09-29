# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib2
import re
import sys


url = sys.argv[1]

def get_link(url):
    html = urllib2.urlopen(url)
    content = html.read()
    html.close()
    links = re.findall(r'(\w*\:\/\/[a-zA-Z0-9\.\-\_\/]+)', content)
    for link in links:
      print link

if __name__ == '__main__':
    get_link(url)
