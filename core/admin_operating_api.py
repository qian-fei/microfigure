#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_operating_api.py
@Time: 2020-07-19 15:15:04
@Author: money 
"""
##################################【后台运营管理模块】##################################
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



def works_list_api(is_recommend):
    """
    作品列表调用接口
    :param is_recommend: 是否推荐 true推荐 false不推荐
    """
    try:
        # 参数
        num = request.args.get("num")
        page = request.args.get("page")
        type = request.args.get("type") # 发现传default, 微图传pic, 影集传video
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if type not in ["default", "pick", "video"]:
            return response(msg="Bad Request: Params 'type' is erroe.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"type" if type != "default" else "null": ({"$in": ["tp", "tj"]} if type == "pic" else "yj") if type != "default" else None, "state": 2, "is_recommend": is_recommend}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"author": "$user_info.nick"}},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "type": 1, "author": 1, "browse_num": 1, "create_time": 1}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        return cursor
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_platform_pricing():
    """平台定价"""
    try:
        s_price = request.json.get("s_price")
        m_price = request.json.get("m_price")
        l_price = request.json.get("l_price")
        k_price = request.json.get("k_price")
        fees = request.json.get("fees")
        if not s_price or float(s_price) < 0:
            return response(msg="Bad Request: Params 's_price' is error.", code=1, status=400)
        if not m_price or float(m_price) < 0:
            return response(msg="Bad Request: Params 'm_price' is error.", code=1, status=400)
        if not l_price or float(l_price) < 0:
            return response(msg="Bad Request: Params 'l_price' is error.", code=1, status=400)
        if not k_price or float(k_price) < 0:
            return response(msg="Bad Request: Params 'k_price' is error.", code=1, status=400)
        if not fees or float(fees) < 0:
            return response(msg="Bad Request: Params 'fees' is error.", code=1, status=400)
        doc = manage.client["price"].update({"format": "S"}, {"$set": {"price": float(s_price)}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        doc = manage.client["price"].update({"format": "M"}, {"$set": {"price": float(m_price)}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        doc = manage.client["price"].update({"format": "L"}, {"$set": {"price": float(l_price)}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        doc = manage.client["price"].update({"format": "扩大授权"}, {"$set": {"price": float(fees)}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_recomm_works_list():
    """推荐作品列表"""
    try:
        cursor = works_list_api(True)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_recomm_state():
    """删除推荐作品"""
    try:
        # 参数
        works_id = request.json.get("works_id")
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        # 更新
        doc = manage.client["works"].update({"uid": works_id}, {"$set": {"is_recommend": False}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_option_works_list():
    """作品选择列表"""
    try:
        cursor = works_list_api(False)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_option_works_list_search(delta_time=30):
    """
    作品选择列表搜索
    :param delta_time: 允许查询的最大区间30天
    """
    try:
        # 参数
        content = request.args.get("content")
        category = request.args.get("category") # 标题传title, 作者传author
        type = request.args.get("type") # 发现传default, 微图传pic, 影集传video
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        num = request.args.get("num")
        page = request.args.get("page")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if content and category not in ["title", "author"]:
            return response(msg="Bad Request: Params 'category' is erroe.", code=1, status=400)
        if type not in ["default", "pick", "video"]:
            return response(msg="Bad Request: Params 'type' is erroe.", code=1, status=400)
        if not start_time:
            return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
        if not end_time:
            return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
        if (int(end_time) - int(start_time)) // 24 * 3600 * 1000 > delta_time:
            return response(msg="只能选择一个月以内的作品", code=1)
        pipeline [
            {"$match": {"type" if type != "default" else "null": ({"$in": ["tp", "tj"]} if type == "pic" else "yj") if type != "default" else None, "state": 2, "is_recommend": False, 
             ("title" if category == "title" else "nick") if content else "null": {"$regex": content} if content else None, "$and": [{"$gte": {"create_time": int(start_time)}}, {"$lte": {"create_time": int(end_time)}}]}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"author": "$user_info.nick"}},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "type": 1, "author": 1, "browse_num": 1, "create_time": 1}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_add_recomm_works(upload_max=10):
    """
    添加推荐作品
    :param upload_max: 允许同时上传作品的上限值
    """
    try:
        # 获取参数
        works_list = request.json.get("works_list")
        if not works_list:
            return response(msg="Bad Request: Miss params: 'works_list'.", code=1, status=400)
        # 最大上传10个
        if len(works_list) > upload_max:
            return response(msg=f"最多允许选择{upload_max}个作品", code=1)
        doc = manage.client["price"].update({"uid": {"$in": works_list}}, {"$set": {"is_recommend": True}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)