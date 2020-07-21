#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_operating_api.py
@Time: 2020-07-19 15:15:04
@Author: money 
"""
##################################【后台用户管理模块】##################################
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


def get_user_list():
    """用户列表"""
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        group = request.args.get("group") # 全部传default, 一般用户传comm, 认证摄影师传auth

        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not group:
            return response(msg="Bad Request: Miss params: 'group'.", code=1, status=400)
        if group not in ["default", "comm", "auth"]:
            return response(msg="Bad Request: Params 'group' is erroe.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"type": "user", "state": {"$ne": -1}, "group": {"$in": ["comm", "auth"]} if group == "default" else {"$eq": group}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "head_img_url": 1, "nick": 1, "account": 1, "create_time": 1, "group": 1}}
        ]
        cursor = client.client["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        if not data_list:
            raise Exception("No data in the database")
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_filter_list(search_max=16):
    """
    用户列表筛选
    :param search_max: 搜索内容的最大字符数
    """
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        category = request.args.get("category") # 账号传account, 昵称传nick
        group = request.args.get("group") # 全部传default, 一般用户传comm, 认证摄影师传auth
        content = request.args.get("content")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["account", "nick"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if group not in ["default", "comm", "auth"]:
            return response(msg="Bad Request: Params 'group' is erroe.", code=1, status=400)
        if content and len(content) > search_max:
            return response(msg="搜索内容最长16个字符，请重新输入", code=1)
        # 查询
        pipeline = [
            {"$match": {"type": "user", "state": {"$ne": -1}, "group": {"$in": ["comm", "auth"]} if group == "default" else {"$eq": group}, 
                        ("nick" if category == "nick" else "account") if content else "null": {"$regex": content} if content else None}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "head_img_url": 1, "nick": 1, "account": 1, "create_time": 1, "group": 1}}
        ]
        cursor = client.client["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_user_state():
    """冻结、恢复用户"""
    try:
        # 参数
        user_id = request.json.get("user_id") # array
        state = request.json.get("state") # 冻结传0, 恢复传1
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if not state:
            return response(msg="Bad Request: Miss params: 'state'.", code=1, status=400)
        if state and int(state) != -1:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        doc = manager.client["user"].update({"uid": {"$in": user_id}}, {"$set": {"state": int(state)}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_user_group():
    """移动用户组"""
    # TODO
    try:
        pass
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_detail():
    """获取用户详情"""
    try:
         # 参数
        user_id = request.json.get("user_id")
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        # 基本信息查询
        condition = {"_id": 0, "uid": 1, "nick": 1, "head_img_url": 1, "background_url": 1, "account": 1, "label": 1, "state": 1, "sex": 1, "group": 1, "mobile": 1, "balance": 1, "sign": 1, "create_time": 1}
        doc = manager.client["user"].find({"uid": user_id}, condition)
        if not doc:
            return response(msg="Bad Request: Params 'user_id' is error.", code=1, status=400)
        # 作品数量查询
        pipeline = [
            {"$match": {"user_id": "user_id", "state": {"$ne": -1}}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$project": {"type": "$_id.type", "count": 1}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        pic_num = 0
        atlas_num = 0
        video_num = 0
        for doc in cursor:
            if doc.get("type") == "tp":
                pic_num = doc.get("count")
            elif doc.get("type") == "tj":
                atlas_num = doc.get("count")
            elif doc.get("type") == "yj":
                video_num = doc.get("count")
        doc["pic_num"] = pic_num
        doc["atlas_num"] = atlas_num
        doc["video_num"] = video_num
        return response(data=doc)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)  


def put_user_password():
    """重置用户密码"""
    try:
        # 参数
        user_id = request.json.get("user_id")
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        # 密码加密
        password = "123456"
        password_b64 = base64.b64encode(password.encode()).decode()
        # 更新password
        doc = manage.client["user"].update({"uid": user_id}, {"$set": {"password": password}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_user_mobile():
    """修改用户手机"""
    try:
        # 参数
        user_id = request.json.get("user_id")
        mobile = request.json.get("mobile")
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if not mobile:
            return response(msg="请输入手机号码", code=1)
        # 判断手机号长度
        if len(str(mobile)) != 11:
            return response(msg="请输入正确的手机号", code=1)

        # 判断手机格式
        if not re.match(r"1[35678]\d{9}", str(mobile)):
            return response(msg="请输入正确的手机号", code=1)
        # 更新mobile
        doc = manage.client["user"].update({"uid": user_id}, {"$set": {"mobile": mobile}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_user_message():
    """给用户发送消息"""
    try:
        # 参数
        user_id = request.json.get("user_id")
        content = request.json.get("content")
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if not content:
            return response(msg="请输入内容", code=1)
        if len(content) > 32:
            return response(msg="消息文字上限32个字符", code=1)
        manage.client["message"].insert({"uid": uid, "user_id": user_id, "push_people": "系统消息", "desc": content, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_user_balance_operation():
    """用户余额操作接口"""
    try:
         # 参数
        user_id = request.json.get("user_id")
        inc = request.json.get("inc")
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if not inc:
            return response(msg="请输入充值金额", code=1)
        doc = manage.client["user"].update({"uid": user_id}, {"$inc": {"balance": float(inc)}})
        if doc["n"] == 0:
            return response(msg="操作失败", code=1)
        # 记录操作记录
        stamp_time = int(time.time() * 1000)
        random_str = "%02d" % random.randint(0, 100)
        order = random_str + f"{stamp_time}"
        doc = manager.client["user_id"].find_one({"user_id": user_id})
        balance = doc["balance"]
        condition = {"user_id": user_id, "type": "后台充值" if float(inc) >= 0 else "后台扣除", "order": order, "amount": float(inc), "balance": float(inc) + balance, "state": 1, 
                     "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
        }
        manage.client["balance_record"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_balance_records(delta_time=30):
    """
    用户余额记录表
    :param delta_time: 允许查询的最大区间30天
    """
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        user_id = request.json.get("user_id")
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if not start_time:
            return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
        if not end_time:
            return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
        if (int(end_time) - int(start_time)) // 24 * 3600 * 1000 > delta_time:
            return response(msg="最大只能查询一个月之内的记录", code=1)
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1, "$and": [{"$gte": {"create_time": int(start_time)}}, {"$lte": {"create_time": int(end_time)}}]}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "state": 0, "update_time": 0}}
        ]
        cursor = manager.client["balance_record"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_org_list():
    """机构列表"""
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        belong = request.args.get("belong") # 全部传default, 主账号master, 子账号slave

        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if belong not in ["default", "master", "slave"]:
            return response(msg="Bad Request: Params 'belong' is erroe.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"type": "user", "state": {"$ne": -1}, "belong": {"$in": ["master", "slave"]} if belong == "default" else {"$eq": belong}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "org_name": 1, "belong": 1, "head_img_url": 1, "nick": 1, "account": 1, "create_time": 1, "group": 1}}
        ]
        cursor = client.client["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        if not data_list:
            raise Exception("No data in the database")
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_org_filter_list(search_max=16):
    """
    机构列表筛选
    :param search_max: 搜索内容最大字符数
    """
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        category = request.args.get("category") # 机构名称org_name, 昵称传nick
        belong = request.args.get("belong") # 全部传default, 主账号master, 子账号slave
        content = request.args.get("content")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["org_name", "nick"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if belong not in ["default", "master", "slave"]:
            return response(msg="Bad Request: Params 'belong' is error.", code=1, status=400)
        if content and len(content) > search_max:
            return response(msg="搜索内容最长16个字符，请重新输入", code=1)
        # 查询
        pipeline = [
            {"$match": {"type": "user", "state": {"$ne": -1}, "belong": {"$in": ["master", "slave"]} if belong == "default" else {"$eq": belong}, 
                        ("nick" if category == "nick" else "org_name") if content else "null": {"$regex": content} if content else None}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "org_name": 1, "belong": 1, "head_img_url": 1, "nick": 1, "account": 1, "create_time": 1, "group": 1}}
        ]
        cursor = client.client["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_create_org_account():
    """创建机构账号"""
    try:
        # 获取参数
        nick = request.json.get("nick")
        account = request.json.get("account")
        label = request.json.get("label") # array
        sex = request.json.get("sex")
        mobile = request.json.get("mobile")
        sign = request.json.get("sign")
        belong = request.json.get("belong") # 主账号master, 子账号slave
        org_name = request.json.get("org_name")
        group = request.json.get("group") # comm一般用户，auth认证摄影师
        # TODO
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_audit():
    """用户审核列表"""
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"is_auth": False, "state": 1, "type": {"$in": ["org", "user"]}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "head_img_url": 1, "nick": 1, "account": 1, "update_time": 1, "id_card_name": 1, "id_card": 1}}
        ]
        cursor = manager.client["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_audit_filter():
    """用户审核列表搜索"""
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        category = request.args.get("category") # 账号传account, 昵称传nick
        content = request.args.get("content")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["account", "nick"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if not content:
            return response(msg="请输入内容", code=1)
        if content and len(content) > search_max:
            return response(msg="搜索内容最长16个字符，请重新输入", code=1)
        # 查询
        pipeline = [
            {"$match": {"is_auth": False, "state": 1, "type": {"$in": ["org", "user"]}, "nick" if category == "nick" else "account": {"$regex": content}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "head_img_url": 1, "nick": 1, "account": 1, "update_time": 1, "id_card_name": 1, "id_card": 1}}
        ]
        cursor = client.client["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_user_audit_state():
    """用户审核"""
    try:
         # 参数
        user_id = request.json.get("user_id") # array
        is_auth = request.json.get("is_auth") # 通过传true, 驳回传false
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if not is_auth:
            return response(msg="Bad Request: Miss params: 'state'.", code=1, status=400)
        doc = manager.client["user"].update({"uid": {"$in": user_id}}, {"$set": {"is_auth": is_auth}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)
