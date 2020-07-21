#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_system_api.py
@Time: 2020-07-19 17:05:31
@Author: money 
"""
##################################【后台系统管理模块】##################################
import sys
import os
# 将根目录添加到sys路径中
BASE_DIR1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR1)
sys.path.append(BASE_DIR2)

import base64
import string
import time
import random
import datetime
import manage
from bson.son import SON
from flask import request, g
from utils.util import response
from constant import constant
from app_login_api import check_token


def get_admin_account_list():
    """管理员账号列表"""
    try:
        # 获取参数
        num = request.args.get("num")
        page = request.args.get("page")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"state": {"$ne": -1}, "type": {"$in": ["super", "admin"]}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "role", "let": {"role_id": "$role_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$role_id"]}}}], "as": "role_item"}},
            {"$addFields": {"role_info": {"$arrayElemAt": ["$role_item", 0]}}},
            {"$addFields": {"role": "$role_info.nick"}},
            {"$project": {"_id": 0, "uid": 1, "nick": 1, "account": 1, "mobile": 1, "sole": 1, "create_time": 1}}
        ]
        cursor = manage.cient["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_admin_account_search(search_max=32):
    """
    管理员账号列表搜索
    :param: search_max: 搜索内容上限字符数
    """
    try:
        # 获取参数
        num = request.args.get("num")
        page = request.args.get("page")
        content = request.args.get("content")
        type = request.args.get("type") # 账号account 昵称nick 联系电话mobile
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if type not in ["account", "nick", "mobile"]:
            return response(msg="Bad Request: Params 'type' is erroe.", code=1, status=400)
        if not content:
            return response(msg="请输入内容", code=1)
        if len(content) > search_max:
            return response(msg="搜索内容上限32个字符", code=1)
        # 查询
        pipeline = [
            {"$match": {"state": {"$ne": -1}, "type": {"$in": ["super", "admin"]}, f"{type}": {"$regex": content}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "role", "let": {"role_id": "$role_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$role_id"]}}}], "as": "role_item"}},
            {"$addFields": {"role_info": {"$arrayElemAt": ["$role_item", 0]}}},
            {"$addFields": {"role": "$role_info.nick"}},
            {"$project": {"_id": 0, "uid": 1, "nick": 1, "account": 1, "mobile": 1, "sole": 1, "create_time": 1}}
        ]
        cursor = manage.cient["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_admin_account_state():
    """管理员列表页删除操作"""
    try:
        # 参数
        user_id = request.json.get("user_id")
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        doc = manage.client["user"].update({"uid": user_id}, {"$set": {"state": -1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)
