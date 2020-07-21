#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File: test.py
@Time: 2020-06-30 16:26:41
@Author: money 
'''
import random
import sys
import string
import os
import base64
import time
import datetime
import pymongo
t = base64.b64encode(os.urandom(64)).decode()

import sys,os
print(os.path.abspath(__file__))
print(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)

# dict = {
#     'name':'hah',
#     'sex': '男'
# }
# dict.update({'age':87})
# print(dict)

# print(string.ascii_letters)

# last_time_str = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
# timeArray = time.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
# last_time_timestamp = int(time.mktime(timeArray)) * 1000
# print(last_time_timestamp)

# #获取当前时间
# dtime = datetime.datetime.now()
# print(dtime)
# t = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)

# timeArray = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
# print(timeArray)
# timestamp = int(time.mktime(timeArray.timetuple()) * 1000)
# print(timestamp)
# un_time = int(time.mktime((timeArray - datetime.timedelta(days=7)).timetuple())) * 1000
# print(un_time)

# set = {1,2,3,2}
# set.add(6)
# print(set)

# client = pymongo.MongoClient('127.0.0.1', 27017)

# cursor = client["student"]["visit"].aggregate([
#     {"$match": {"test": {"$in": [5, 9]}}}
# ])
# doc = [doc for doc in cursor]
# print(doc)

# uuid = base64.b64encode(os.urandom(8)).decode().lower()
# print(uuid + "111111111111111111111111111")

# list = [1,3,4]
# list.insert(1, 9)
# print(list)

# dict = {"$match": {}}
# dict["$match"].update({"name": "前"})
# print(dict)


# def test(a):
#     try:
#         if a >2:
#             raise Exception("错误")
#     except Exception as e:
#         print(e, "是的")
# test(4)

# print(os.getcwd())

# date = datetime.datetime.now()
# print(f"{date.year}{date.month}{date.day}")

# path = os.getcwd() + "/file/"

# if not os.path.exists(path):
#     os.makedirs(path)

# t = 1593532800000 - 1593619200000
# tt = 24 * 3600 * 1000
# print(t, tt)


# test_dict = {"user": 111, "mobile": 333}
# t = test_dict.get("sex")
# print(t)
# if t:
#     print("存在")
# uuid = base64.b64encode(os.urandom(32)).decode()
# print(uuid)   

# import manage

# state = manage.client["test"].insert([{"user": 3, "name": 3}, {"user": 2, "name": 2}])
# print(state)
# list = [doc for doc in state]

# cursor = manage.client["test"].find({"_id": {"$in": list}})
# for doc in cursor:
#     print(doc)
# import datetime
# import time
# today = datetime.date.month
# today_time = int(time.mktime(today.timetuple())*1000)
# print(today)

# random_str = "%02d" % random.randint(0, 100)
# print(random_str)

# size = os.path.getsize() // 1024

# str = "http://101.136.132.180/20200713103921.png"
# str = str.replace("http", "")
# print(str)
# # print(size)
# import re
# test = "825076979qq.com"
# re = re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',test)
# if not re:
#     print('11111111')
t = 232423234 // 1024
print(t)