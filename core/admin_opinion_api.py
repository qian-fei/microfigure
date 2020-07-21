#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_opinion_api.py
@Time: 2020-07-19 16:31:50
@Author: money 
"""
##################################【后台舆情监控模块】##################################
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


def get_report_comment_list():
    """举报评论列表"""
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
        pipeline = [
            {"$match": {"state": 0}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "works", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "works_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}, "works_info": {"$arrayElemAt": ["$works_item", 0]}}},
            {"$addFields": {"user_account": "$user_info.account", "works_title": "$works_info.title"}},
            {"$project": {"_id": 0, "uid": 1, "user_account": 1, "works_title": 1, "create_time": 1, "content": 1}}
        ]
        cursor = manage.client["comment"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_report_comment_search(search_max=32):
    """
    举报评论列表搜索
    :param: search_max: 搜索内容上限字符数
    """
    try:
        # 获取参数
        num = request.args.get("num")
        page = request.args.get("page")
        content = request.args.get("content")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not content:
            return response(msg="请输入内容", code=1)
        if len(content) > search_max:
            return response(msg="搜索内容上限32个字符", code=1)
        pipeline = [
            {"$match": {"state": 0, "content": {"$regex": content}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "works", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "works_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}, "works_info": {"$arrayElemAt": ["$works_item", 0]}}},
            {"$addFields": {"user_account": "$user_info.account", "works_title": "$works_info.title"}},
            {"$project": {"_id": 0, "user_account": 1, "works_title": 1, "create_time": 1, "content": 1}}
        ]
        cursor = manage.client["comment"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_report_comment_state(option_max=10):
    """
    审核举报评论
    :param option_max: 最多允许选择的个数
    """
    try:
        # 参数
        comment_list = request.json.get("comment_list") # array
        state = request.json.get("state") # -1删除，1标记正常
        if comment_list:
            return response(msg="Bad Request: Miss params: 'comment_list'.", code=1, status=400)
        if len(comment_list) > option_max:
            return response(msg=f"最多允许选择{option_max}条评论", code=1)
        if state not in ["-1", "1"]:
            return response(msg="Bad Request: Params 'state' is erroe.", code=1, status=400)
        doc = manage.client["comment"].update({"uid": {"$in": comment_list}}, {"$set": {"state": int(state)}})
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)

def get_report_comment_top():
    """评论相关统计"""
    # TODO
    try:
        pass
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)