#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: works.py
@Time: 2020-06-30 16:27:15
@Author: money 
"""
##################################【app作品创建模块】##################################
import sys
import os
# 将根目录添加到sys路径中
BASE_DIR1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR1)
sys.path.append(BASE_DIR2)

import time
import random
import datetime
import manage
import jieba
from bson.son import SON
from flask import request, g
from constant import constant
from utils.util import response, UploadSmallFile, genrate_file_number


def pic_upload_api(user_id):
    """
    图片上传调用接口
    :param user_id: 用户id
    """
    data_list = []
    try:
        # 参数
        pic_list = request.files.getlist("pic_list[]")
        if not pic_list:
            return response(msg="Bad Request: Miss param: 'pic_list'.", code=1, status=400)
        file = util.UploadSmallFile(manage.app, ALLOWED_EXTENSIONS, 48 * 1024 * 1024, manage.log)
        context = file.upload_file("pic_list[]", "files", user_id)
        if context["code"] == 0:
            return response(msg=context["msg"], code=1, status=400)
        data_list = context["data"]
        return data_list
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_material_upload_common():
    """单个素材上传通用接口"""
    data = {}
    try:
        # 参数
        pic_list = request.files.getlist("pic_list[]")
        if not pic_list:
            return response(msg="Bad Request: Miss param: 'pic_list'.", code=1, status=400)
        file = util.UploadSmallFile(manage.app, ALLOWED_EXTENSIONS, 48 * 1024 * 1024, manage.log)
        context = file.upload_file("pic_list[]", "files", user_id)
        if context["code"] == 0:
            return response(msg=context["msg"], code=1, status=400)
        obj = context["data"][0]
        dada["file_path"] = obj["file_path"]
        data["size"] = obj["size"]
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_pic_material_upload(domain=constant.DOMAIN):
    """
    素材上传接口
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        data_list = pic_upload_api(user_id)
        # 入库
        temp_list = []
        for obj in data_list:
            uid = base64.b64encode(os.urandom(32)).decode()
            condition = {"uid": uid, "user_id": user_id, "pic_url": obj["file_path"], "big_pic_url": obj["file_path"], "thumb_url": obj["file_path"], "size": obj["size"],
                         "state": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
            }
            temp_list.append(condition)
        cursor = manage.client["pic_material"].insert(temp_list)
        id_list = [doc for doc in cursor]
        pipeline = [
            {"$match": {"_id": {"$in": id_list}}},
            {"$project": {"_id": 0, "uid": 1, "pic_url": {"$concat": [domain, "$pic_url"]}}}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        if not data_list:
            raise Exception("Failed to get data.")
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return reponse(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_material(domain=constant.DOMAIN):
    """
    获取图片素材库
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$project": {"_id": 0, "uid": 1, "pic_url": {"$concat": [domain, "$pic_url"]}, "label": 1, "title": 1, "format": 1}}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_history_label(label_max=20):
    """
    用户历史标签
    :param label_max: 标签个数上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$project": {"_id": 0}},
            {"$sort": SON(["create_time", -1])},
            {"$limit": label_max}
        ]
        cursor = manage.client["history_label"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def get_search_label():
    """标签接口"""
    keyword_list = []
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        keyword = request.args.get("keyword")
        # 校验
        if not keyword:
            return response(msg="请输入关键词", code=1)

        # 模糊查询
        cursor = manage.client["label"].find({"label": {"$regex": f"{keyword}"}}, {"_id": 0, "label": 1})
        keyword_list.append(keyword)
        for doc in cursor:
            keyword_list += doc["related"]
        if keyword in keyword_list:
            keyword_list = list(set(keyword_list))
            keyword_list.remove(keyword)
            keyword_list.insert(0, keyword)
        return response(data=keyword_list)
    except Exception as e:
        lgo.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_create_pic_works(pic_list, user_id, label_max=9, title_max=32):
    """
    创作图片
    :param pic_list: 图片列表
    :param user_id: 用户id
    :param length_max: 最多允许标签的上限
    :param title_max: 标题字符上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        pic_list = request.json.get("pic_list")
        if not pic_list:
            return response(msg="Bad Request: Miss param 'pic_list'.", code=1, status=400)
        for i in pic_list:
            title = i["title"]
            label = i["label"]
            pic_uid = i["pic_uid"]
            format = i["format"]
            if not title:
                return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
            if len(title) > title_max:
                return response(msg=f"标题上限{title_max}个字符", code=1)
            if not label:
                return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
            if not pic_uid:
                return response(msg="Bad Request: Miss param 'pic_uid'.", code=1, status=400)
            if not format:
                return response(msg="Bad Request: Miss param 'format'.", code=1, status=400)
            if len(label) > label_max:
                return response(msg=f"最多允许选择{label_max}", code=1)
            # 分词
            keyword = list(jieba.cut(title))
            # 更新素材库
            doc = manage.client["pic_material"].update({"uid": i["pic_uid"], "user_id": user_id}, {"$set": {"title": title, "label": label, "keyword": keyword}})
            if doc["n"] == 0:
                return response(msg="Update failed", code=1, status=400)
        # 只有一张时制作图集
        if len(pic_list) == 1:
            # 制作图片作品
            title = pic_list[0]["title"]
            label = pic_list[0]["label"]
            pic_uid = pic_list[0]["pic_uid"]
            format = pic_list[0]["format"]
            title = pic_list[0]["title"]
            uid = base64.b64encode(os.urandom(32)).decode()
            number = genrate_file_number()
            keyword = list(jieba.cut(title))
            condition = {"uid": uid, "user_id": user_id, "pic_id": pic_uid, "type": "tp", "number": number, "format": format.upper(), "title": title, "keyword": keyword, 
                        "label": label, "state": 0, "is_recommend": False, "is_portrait": False, "is_products": False, "pic_num": 1, "like_num": 0, "comment_num": 0, 
                        "share_num": 0, "browse_num": 0, "sale_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
            }
            manage.client["works"].insert(condition)
            # 更新标签表中works_num
            doc = manage.client["label"].update({"uid": {"$in": label}}, {"$inc": {"works_num": 1}})
            if doc["n"] == 0:
                return response(msg="Update failed.", code=1, status=400)
            doc = manage.client["pic_material"].update({"user_id": user_id, "uid": pic_uid}, {"$set": {"works_id": uid, "works_status": 0}})
            if doc["n"] == 0:
                return response(msg="Update failed.", code=1, status=400)
            # 统计
            # 当前day天
            dtime = datetime.datetime.now()
            time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
            timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            today_stamp = int(time.mktime(timeArray.timetuple()) * 1000)
            doc = manage.client["user_statistical"].find_one({"user_id": user_id, "date": today_stamp})
            if doc:
                manage.client["user_statistical"].update({"user_id": user_id, "date": today_stamp}, {"$inc": {"works_num": 1}, "$set": {"update_time": int(time.time() * 1000)}})
                if doc["n"] == 0:
                    return response(msg="Update failed.", code=1, status=400)
            else:
                condition = {"user_id": user_id, "date": today_stamp, "works_num": 1, "date": today_stamp, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
                manage.client["user_statistical"].insert(condition)
            return response(data=uid)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_pic_collect_works(label_max=9, title_max=32,pic_id_max=20, domain=constant.DOMAIN):
    """
    图集创作
    :param length_max: 最多允许标签的上限
    :param title_max: 标题字符上限
    :param pic_id_max: 允许选择图片的上限
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        cover_url = request.json.get("cover_url")
        title = request.json.get("title")
        label = request.json.get("label")
        pic_id_list = request.json.get("pic_id_list") # array
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if len(title) > title_max:
            return response(msg=f"标题上限{title_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > length_max:
            return response(msg=f"最多允许选择{length_max}", code=1)
        if not pic_id_list:
            return response(msg="Bad Request: Miss param 'pic_id_list'.", code=1, status=400)
        if len(pic_id_list) > pic_id_max:
            return response(msg=f"最多允许选择{pic_id_max}张图片", code=1)
        # 制作图片作品
        cover_url = cover_url.replace(domain, "")
        uid = base64.b64encode(os.urandom(32)).decode()
        number = genrate_file_number()
        keyword = list(jieba.cut(title))
        condition = {"uid": uid, "user_id": user_id, "pic_id": pic_id_list, "type": "tj", "number": number, "title": title, "keyword": keyword, "cover_url": cover_url, 
                     "label": label, "state": 0, "is_recommend": False, "is_portrait": False, "is_products": False, "pic_num": len(pic_id_list), "like_num": 0, "comment_num": 0, 
                     "share_num": 0, "browse_num": 0, "sale_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
        }
        manage.client["works"].insert(condition)
        # 更新标签表中works_num
        doc = manage.client["label"].update({"uid": {"$in": label}}, {"$inc": {"works_num": 1}})
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        # 统计
        # 当前day天
        dtime = datetime.datetime.now()
        time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
        timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        today_stamp = int(time.mktime(timeArray.timetuple()) * 1000)
        doc = manage.client["user_statistical"].find_one({"user_id": user_id, "date": today_stamp})
        if doc:
            manage.client["user_statistical"].update({"user_id": user_id, "date": today_stamp}, {"$inc": {"works_num": 1}, "$set": {"update_time": int(time.time() * 1000)}})
            if doc["n"] == 0:
                return response(msg="Update failed.", code=1, status=400)
        else:
            condition = {"user_id": user_id, "date": today_stamp, "works_num": 1, "date": today_stamp, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["user_statistical"].insert(condition)
        return response(data=uid)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_create_article_works(domain=constant.DOMAIN):
    """
    创作图文
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        title = request.json.get("title")
        content = request.json.get("content")
        cover_url = request.json.get("cover_url")
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if not content:
            return response(msg="Bad Request: Miss param 'content'.", code=1, status=400)
        if not cover_url:
            return response(msg="Bad Request: Miss param 'cover_url'.", code=1, status=400)
        # 入库
        uid = base64.b64encode(os.urandom(32)).decode()
        cover_url = cover_url.replace(domain, "")
        condition = {"uid": uid, "user_id": user_id, "cover_url": cover_url, "content": content, "title": title, "state": 1, "type": "tw", "is_recommend": False, "like_num": 0, 
                     "comment_num": 0, "share_num": 0, "browse_num": 0, "create_time": int(time.time() * 1000), "updated_time": int(time.time() * 1000)
        }
        manage.client["works"].insert(condition)
        # 统计
        # 当前day天
        dtime = datetime.datetime.now()
        time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
        timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        today_stamp = int(time.mktime(timeArray.timetuple()) * 1000)
        doc = manage.client["user_statistical"].find_one({"user_id": user_id, "date": today_stamp})
        if doc:
            manage.client["user_statistical"].update({"user_id": user_id, "date": today_stamp}, {"$inc": {"works_num": 1}, "$set": {"update_time": int(time.time() * 1000)}})
            if doc["n"] == 0:
                return response(msg="Update failed.", code=1, status=400)
        else:
            condition = {"user_id": user_id, "date": today_stamp, "works_num": 1, "date": today_stamp, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["user_statistical"].insert(condition)
        return response(data=uid)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)
