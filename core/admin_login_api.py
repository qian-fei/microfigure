#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_login_api.py
@Time: 2020-07-19 15:20:23
@Author: money 
"""
##################################【后台登录退出模块】##################################
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


def post_admin_login():
    """管理员登录接口"""
    data = {}
    try:
        # 获取参数
        account = request.json.get("account", None)
        password = request.json.get("password", None)
        # 校验
        if not account:
            return response(msg="请输入账号", code=1)
        if not password:
            return response(msg="请输入密码", code=1)
        condition = {"_id": 0, "uid": 1, "type":1, "role_id": 1, "token": 1, "nick": 1, "sex": 1, "sign": 1, "mobile": 1, "login_time": 1}
        doc = manage.client["user"].find_one({"account": account, "password": password}, condition)
        if not doc:
            return response(msg="账户名或密码错误", code=1)
        if doc.get("state") == 0:
            return response(msg="您的账号已被冻结，请联系超级管理员", code=1)
        if doc.get("type") not in ["super", "admin"]:
            return response(msg="您没有权限，请联系超级管理员", code=1)
        # 角色权限
        pipeline = [
            {"$match": {"uid": doc.get("role_id"), "state": 1}},
            {"$lookup": {"from": "module", "let": {"module_id": "$module_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$module_id"]}}}], "as": "module_item"}},
            {"$lookup": {"from": "permission", "let": {"permission_id": "$permission"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$permission_id"]}}}], "as": "permission_item"}},
            {"$addFields": {"module_info": {"$arrayElemAt": ["$module_item", 0]}, "permission_info": {"$arrayElemAt": ["$permission", 0]}}},
            {"$addFields": {"module_name": "$module_info.name", "permission_name": "$permission_info.name"}},
            {"$group": {"_id": 0}}
        ]
        cursor = manage.client["role"].aggregate(pipeline)
        role_info = {}
        module_list = []
        permission_list = []
        c = 0
        for doc in cursor:
            module_dict = {}
            permission_dict = {}
            if c == 0:
                role_info["uid"] = doc.get("uid")
                role_info["nick"] = doc.get("nick")
                role_info["desc"] = doc.get("desc")
            module_dict["module_id"] = doc.get("module_id")
            module_dict["module_name"] = doc.get("module_name")
            permission_dict["module_id"] = doc.get("module_id")
            permission_dict["permission_id"] = doc.get("permission_id")
            permission_dict["permission_name"] = doc.get("permission_name")
            module_list.append(module_dict)
            permission_list.append(permission_dict)
        role_info["module_list"] = module_list
        role_info["permission_list"] = permission_list
        data["role_info"] = role_info

        # 校验token有效期
        token = doc["token"]

        sign = check_token(doc)
        if sign: token = sign
        data["user_info"] = doc
        # 记录登录时间
        manage.client["user"].update_one({"uid": doc["uid"]}, {"$set": {"login_time": int(time.time() * 1000)}})
        resp = response(data=data)
        resp.headers["token"] = token
        
        return resp
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s" % str(e), code=1, status=500)