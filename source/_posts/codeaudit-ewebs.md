---
title: 代码审计-极通EWEBS应用虚拟化系统
date: 2019-3-16 13:58:07
updated: 2019-3-16 13:58:12
comments: true
categories: 
 - 代码审计
---

### 0x00 漏洞描述

极通EWEBS应用虚拟化系统<=7.02版本存在SQL注入漏洞，远程攻击者可利用该漏洞写入webshell，获得服务器权限。

### 0x01 漏洞分析与利用

极通EWEBS应用虚拟化系统安装完成后，站点根目录下存在测试文件testweb.php,文件包含物理路径等敏感信息。
站点对SQL语句过滤不严，存在SQL注入漏洞，攻击者可以利用泄露的物理路径加上SQL注入漏洞写入webshell，获得服务器权限。

#### 存在漏洞点

1、用户名输入框存在SQL注入：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-ewebs01.gif)

如上图，点击用户名输入框后，随便点击网页上的任何一个地方，就会向服务器发送一个用户名验证，这里没有做SQL语句过滤。

2、站点目录下存在测试文件，有站点的各种信息,安装路径、web路径等等：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-ewebs02.png)

#### 漏洞利用

SQL注入为root权限，加上泄露的物理路径就可以写入webshell：

1、 必须要先访问首页链接，生成PHPSESSID

2、 把发往服务器的数据长度删除

3、 利用SQL注入写入webshell

手动验证方式：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-ewebs03.gif)

脚本利用方式：
```code
python3 ewebs.py http://192.168.123.112:8088
```

脚本下载链接：[ewebs.py](../do/code/ewebs.py)

![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-ewebs04.gif)


### 修复
* 删除测试页面，自定义错误页面
* 过滤SQL语句