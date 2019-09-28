---
title: 代码审计-Axublog建站系统
date: 2019-1-28 09:41:29
updated: 2019-1-28 09:41:29
comments: true
categories: 
 - 代码审计
---

### 0x00 序言

昨天刚学的代码审计，代码读起来非常的吃力，视频也很"水"，没有讲到精髓，看视频到后边直接想放弃了，蛋疼、蛋疼、蛋疼，但还是下了一个简单的博客源码来看看，上源码之家看了看，压缩包都很大，最后选了一个1M大小的压缩包。

### 0x01 SQL注入漏洞

初次发现了一个SQL注入漏洞，确实挺激动的。

* 源码版本：Axublog v1.1.1
* 漏洞位置：login.php
* 下载地址：http://pic.axublog.com/axublog1.1.1install.rar
* 修复状态：未修复

##### 分析

默认安装之后后台地址是：http://localhost/ad/login.php
但是查看ad/login.php文件又找不到任何执行SQL语句的地方，只看到了几个变量。
```code
@$user=$_POST["user"];
@$psw=$_POST["psw"];
@$loginlong=$_POST["loginlong"];
```

搜索@$user发现几个文件包含这个变量，凭感觉，c_login.php才是控制登录的文件。

![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-axublog01.png)

打开这个文件之后发现果然是包含了login.php，那么这里就有个小技巧可以发现哪个是登陆文件了，直接通过搜索login.php文件，看看哪些文件包含了login.php，就能大概猜到是哪个文件了。

通过用户名变量往上查找，发现了这个程序有SQL注入过滤，过滤函数是sqlguolv()：

```code
function jsloginpost(){
global $tabhead;
global $txtchk;
@$user=$_POST["user"];
@$psw=$_POST["psw"];$psw = authcode(@$psw, 'ENCODE', 'key',0); 
@$loginlong=$_POST["loginlong"];
$chk=sqlguolv();
if($chk==1){
$json_arr = array("jieguo"=>"<div id=redmsg>登录失败：发现非法字符！</div>");
$json_obj = json_encode($json_arr);
echo $json_obj;die();
}
```

过滤函数内容如下，刚开始觉得奇怪，这个函数为什么不用传参就能执行和判断，原来是'SERVER'这个变量：
```code
Function sqlguolv() {
@header("Content-type:text/html; charset=utf-8");
$a='/%3C|\<|%27|%22|\>|%3E|\||\\\|\;|select|insert|\"|\'|\\*|\*|union|into/i';
if(preg_match($a,$_SERVER['QUERY_STRING'])==11 or preg_match($a,file_get_contents("php://input"))==11 ){return "1";}
}
```

既然过滤了这么多内容，就想看看过滤之后都有什么提示：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-axublog02.png)

嗯！！！竟然没有提示非法字符！往上看了遍代码，竟然没有包含过滤函数的文件，那还过滤个屁啊，把过滤函数的文件包含上去试试。
说好的过滤呢？
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-axublog03.png)

嗯！！！还是一样，不应该是提示非法字符吗？

SQLmap跑了一下，竟然没跑出来，那到底是过滤还是没过滤了啊，看看查询语句吧，目测是过滤失效了。
```code
select * from axublog_adusers where adnaa='select|insertunion|into' and adpss='yYxvHseLMURYWjNE6YGqRjrqVDZUd38v7C+k/uhYgmw'
```
那就根据查询语句试试绕过登录：
```code
select * from axublog_adusers where adnaa='' or true #' and adpss='yYxvHseLMURYWjNE6YGqRjrqVDZUd38v7C+k/uhYgmw'
```
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-axublog04.gif)

### 结束
来看看为什么过滤会失效：
```code
Function sqlguolv() {
@header("Content-type:text/html; charset=utf-8");
$a='/%3C|\<|%27|%22|\>|%3E|\||\\\|\;|select|insert|\"|\'|\\*|\*|union|into/i';
if(preg_match($a,$_SERVER['QUERY_STRING'])==11 or preg_match($a,file_get_contents("php://input"))==11 ){return "1";}
}
```

* preg_match() 函数用于进行正则表达式匹配，成功返回 1 ，否则返回 0 。
* 这里的过滤做了判断，匹配过滤的字符，条件等于11，这里就有问题。
* SERVER['QUERY_STRING'] 这个语句是获取GET请求?后边的内容，所以这里获取的值为空，也就匹配不出来了。