#!/usr/bin/python
# -*- coding: utf-8 -*-

#1、统计文本有多少行
# f = open("weibo.txt","r")
# content = f.read()
# f.close()
# print content.count("\n")

# f = open("weibo.txt","r")
# content = f.readlines()    #使用readlines内置方法，每一行作为一个列表分割，保存在大列表里边
# f.close()
# print len(content)         #len统计内容里边有多少项数据

#2、该微博中一共有多少个不重复的用户名：
raw_data = ("user_id","user_name","poster_url","post_num","post_id","post_time","content")

# l = []                                         #创建空的列表
# for item in raw_data:                          #迭代出raw_data
# 	l.append((item,raw_data.index(item)))      #添加到一个列表
# d = dict(l)                                    #转换成字典
# print d["user_name"]                           #通过字典的键，查找他所对应的值

#列表推倒式：
data_item = dict([(item,raw_data.index(item)) for item in raw_data])
# print data_item["user_name"] 

f = open("weibo.txt","r")
content = f.readlines()    #使用readlines内置方法，每一行作为一个列表分割，保存在大列表里边
f.close()
# print len(content)         #len统计内容里边有多少项数据
# l = []                       #新建空的列表
# for line in content:         #迭代
# 	l.append(line[1:-1].split('","')) #取第一位到最后一位，并使用","符号进行分割
# print l[1][1]

#列表推倒式：
lines = [line[1:-1].split('","') for line in content]
# print lines[1][1]

# l = []
# for line in lines:
# 	l.append(line[data_item["user_name"]])
# print len(set(l))

#列表推倒式：
# uname = set(line[data_item["user_name"]] for line in lines)
# print len(uname)

#3、依次输出这些用户名：
# for anyname in uname:
# 	print anyname

#4、该微博有多少条是在41959时间断种发布的：
# time = [line for line in lines if line[data_item["post_time"]].startswith("41959")]
# print len(time)

#计数器：
# x = 0
# for line in lines:
# 	time = line[data_item["post_time"]]
# 	if time.startswith("41959"):
# 		x += 1
# print x

# print sorted(set(line[data_item["post_time"]][0:7] for line in lines))

# print len(set(line[data_item["post_time"]].split(".")[0] for line in lines))

#该微博数据中，每个小时的发布量各是多少：
d = {}
for line in lines:
	hour = line[data_item["post_time"]].split(".")[1][0:2]
	if hour in d:
		d[hour] += 1
	else:
		d[hour] = 1
# print d["22"]

#8、该微博数据中，那个小时的发布量最大：
hours = d.items()   #使用items内置方法，转换成列表，列表里边包含元祖
hours.sort(key=lambda x:x[1])
print "Max hour:%s,number:%s" % hours[-1]
