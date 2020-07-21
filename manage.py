#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: manage.py
@Time: 2020-06-30 16:26:29
@Author: money 
"""
import os
import sys
import functools
import pymongo
from flask_cors import CORS
from core import app_login_api, app_list_api, app_user_api, app_order_api, app_works_api
from core import admin_login_api, admin_index_api, admin_front_api, admin_user_api, admin_opinion_api, admin_operating_api, admin_system_api
from utils import util
from flask import Flask, jsonify, request, g
from constant.constant import DOMAIN
# 将根目录添加到sys路径中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# 创建应用
app = Flask(__name__)
# 允许跨域
CORS(app, supports_credentials=True)
# 允许输出中文
app.config["JSON_AS_ASCII"] = False
# 生成密钥 base64.b64encode(os.urandom(64)).decode()
SECRET_KEY = "p7nHRvtLdwW07sQBoh/p9EBmHXv9DAcutk2vlj4MdSPNgFeTobUVJ3Ss2Wwl3T3tuv/ctTpPw+nQKMafU3MRJQ=="
app.secret_key = SECRET_KEY
# 允许上传的文件类型
ALLOWED_EXTENSIONS = ["txt", "pdf", "png", "jpg", "jpeg", "gif", "mp3", "svg", "avi", "mov", "rmvb", "rm", "flv", "mp4", "3gp", "asf", "asx"]

# 创建日志
log = util.Logger("log_debug")
# 输出日志信息
log.info("The application has started.")
# 连接mongoDB
mongo = util.MongoDB(log)
# 连接数据库
client = mongo.client["local_writer"]["microfigure"]
# 云数据库链接
# CONN_ADDR1 = "dds-uf6c62f85a588a641741-pub.mongodb.rds.aliyuncs.com:3717" 
# CONN_ADDR2 = "dds-uf6c62f85a588a642965-pub.mongodb.rds.aliyuncs.com:3717"
# REPLICAT_SET = "mgset-32825379"
# username = "root"
# password = "Rd123!@#"
# # 获取mongoclient
# client = pymongo.MongoClient([CONN_ADDR1, CONN_ADDR2], replicaSet=REPLICAT_SET)
# # 管理员授权
# client.admin.authenticate(username, password)
# client = client["microfigure"]
# 路径
url = "/api/v1"


def auth_user_login(f):
    """用户状态判断"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            user_data = {
                "user_id": None,
                "user_info": None
            }
            token = request.headers.get("token")
            if token:
                pipeline = [
                    {"$match": {"token": token}},
                    {"$project": {"_id": 0, "uid": 1, "nick": 1, "sex": 1, "head_img_url": {"$concat": [DOMAIN, "$head_img_url"]}, "sign": 1, "mobile": 1, "backgroud": 1, "works_num": 1, 
                                  "label": 1, "login_time": 1, "group": 1, "create_time": 1, "update_time": 1}
                    }
                ]
                cursor = client["user"].aggregate(pipeline)
                data_list = [doc for doc in cursor]
                if not data_list:
                    raise Exception("Bad Request: Parameter 'token' is error.")
                doc = data_list[0]
                if doc: 
                    uid = doc.get("uid")
                    user_data = {
                    "user_id": uid,
                    "user_info": doc
                    }
        except Exception as e:
            log.error(e)
        finally:
            g.user_data = user_data
        return f(*args, **kwargs)

    return wrapper


def auth_admin_login(f):
    """管理员登录校验"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # 验证token
            token = request.headers.get("token")
            from utils.util import response
            if not token:
                return response(msg="Bad Request: Miss params 'token'.", code=1, status=400)
            doc = client["user"].find_one({"token": token, "type": {"$in": ["super","admin"]}}, {"_id": 0, "uid": 1, "type": 1, "nick": 1, "sex": 1, "sign": 1, "mobile": 1, "role_id": 1})
            if not doc:
                return response(msg="Bad Request: The user doesn't exist.", code=1, status=400)   
            if doc["type"] not in ["super", "admin"]:
                return response(msg="Bad Request: You don't have permission", code=1, status=400)
            uid = doc.get("uid")
            user_data = {
                "user_id": uid,
                "user_info": doc
            }
            g.user_data = user_data
        except Exception as e:
            log.error(e)
            return
        return f(*args, **kwargs)

    return wrapper


def auth_amdin_role(f):
    """管理员角色权限校验"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # 验证token
            module_id = request.headers.get("module_id")
            permission_id = request.headers.get("permission_id")
            from utils.util import response
            if not module_id:
                return response(msg="Bad Request: Miss params 'module_id'.", code=1, status=400)
            if not permission_id:
                return response(msg="Bad Request: Miss params 'permission_id'.", code=1, status=400)
            user_id = g.user_data["user_id"]
            doc = client["role"].find_one({"user_id": user_id, "module_id": module_id, "permission_id": permission_id})
            if not doc:
                return response(msg="您没有操作权限，请联系超级管理员", code=1)
        except Exception as e:
            log.error(e)
            return
        return f(*args, **kwargs)

    return wrapper


@app.after_request
def response_headers(response):
    """处理跨域问题"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Content-Struct-Type"] = "HotAppServerApi"
    response.headers["Access-Control-Expose-Headers"] = "*"
    return response


@app.route(f"{url}/banner", methods=["GET"])
def get_banner():
    """轮播图接口"""
    return app_list_api.get_banner()


@app.route(f"{url}/total", methods=["GET"])
@auth_user_login
def total_list():
    """发现页列表接口"""
    return app_list_api.get_total_list()


@app.route(f"{url}/pic", methods=["GET"])
@auth_user_login
def pic_list():
    """图集页列表接口"""
    return app_list_api.get_pic_list()


@app.route(f"{url}/video", methods=["GET"])
@auth_user_login
def video_list():
    """影集页列表接口"""
    return app_list_api.get_video_list()


@app.route(f"{url}/article", methods=["GET"])
@auth_user_login
def article_list():
    """图文页列表接口"""
    return app_list_api.get_article_list()


@app.route(f"{url}/atlas/detail", methods=["GET"])
@auth_user_login
def pic_detail():
    """图集详情页列表接口"""
    return app_list_api.get_pic_detail()


@app.route(f"{url}/video/detail", methods=["GET"])
@auth_user_login
def video_detail():
    """影集详情页列表接口"""
    return app_list_api.get_video_detail()


@app.route(f"{url}/article/detail", methods=["GET"])
@auth_user_login
def article_detail():
    """图文详情页列表接口"""
    return app_list_api.get_article_detail()


@app.route(f"{url}/article/hot", methods=["GET"])
@auth_user_login
def hot_article_list():
    """图文热点文章列表接口"""
    return app_list_api.get_hot_article_list()


@app.route(f"{url}/video/top", methods=["GET"])
def video_top_list():
    """影集置顶列表接口"""
    return app_list_api.get_video_top_list()


@app.route(f"{url}/label_kw", methods=["GET"])
@auth_user_login
def hot_kw_label():
    """标签、热搜词接口"""
    return app_list_api.get_label_kw()


@app.route(f"{url}/browse", methods=["POST"])
@auth_user_login
def browse_records():
    """浏览记录接口"""
    return app_list_api.post_browse_records()


@app.route(f"{url}/hot/keyword", methods=["GET"])
def hot_keyword():
    """热搜词接口"""
    return app_list_api.get_hot_keyword()


@app.route(f"{url}/search/keyword", methods=["GET"])
def search_keyword():
    """搜索关键词接口"""
    return app_list_api.get_search_keyword()


@app.route(f"{url}/search/works", methods=["GET"])
@auth_user_login
def search_works():
    """搜索作品接口"""
    return app_list_api.get_search_works()


@app.route(f"{url}/captcha", methods=["GET"])
def pic_captcha():
    """图片验证码接口"""
    return app_login_api.get_captcha()


@app.route(f"{url}/sms", methods=["POST"])
def sms_code():
    """短信验证码接口"""
    return app_login_api.post_sms_code()


@app.route(f"{url}/sms/verify", methods=["POST"])
def sms_code_verify():
    """短信验证码校验接口"""
    return app_login_api.post_sms_verify()


@app.route(f"{url}/register", methods=["POST"])
def user_register():
    """用户注册接口"""
    return app_login_api.post_register()


@app.route(f"{url}/login/account", methods=["POST"])
def login_account():
    """账户登录接口"""
    return app_login_api.post_account_login()


@app.route(f"{url}/login/mobile", methods=["POST"])
def login_mobile():
    """手机登录接口"""
    return app_login_api.post_mobile_login()


@app.route(f"{url}/oauth/bind", methods=["POST"])
def oauth_bind():
    """第三方绑定接口"""
    return app_login_api.post_oauth_bind()


@app.route(f"{url}/oauth/login", methods=["POST"])
def oauth_login():
    """第三方登录接口"""
    return app_login_api.post_oauth_login()


@app.route(f"{url}/logout", methods=["GET"])
@auth_user_login
def user_logout():
    """退出接口"""
    return app_login_api.get_user_logout()


@app.route(f"{url}/user/message", methods=["GET"])
def user_message():
    """我的消息"""
    return app_user_api.get_user_message()


@app.route(f"{url}/user/message/alter", methods=["PUT"])
def user_message_alter():
    """删除我的消息"""
    return app_user_api.put_user_message_alter()


# @app.route(f"{url}/user/follow/list", methods=["GET"])
# def user_follow():
#     """我的关注"""
#     return app_user_api.get_user_follow()


@app.route(f"{url}/user/follow/search", methods=["GET"])
def user_follow_search():
    """我的关注搜索"""
    return app_user_api.get_user_follow_search()


@app.route(f"{url}/user/follow/cancel", methods=["PUT"])
def user_follow_cancel():
    """我的关注取消"""
    return app_user_api.put_user_follow_state()


@app.route(f"{url}/user/follow/news", methods=["PUT"])
def user_follow_news():
    """我的关注作品最新动态"""
    return app_user_api.get_user_follow_works()


@app.route(f"{url}/user/info", methods=["GET"])
@auth_user_login
def user_info():
    """用户基本信息接口"""
    return app_user_api.get_userinfo()


@app.route(f"{url}/user/info/alter", methods=["PUT"])
@auth_user_login
def user_info_alter():
    """修改基本信息接口"""
    return app_user_api.put_alter_userinfo()


@app.route(f"{url}/works/like", methods=["POST"])
@auth_user_login
def works_like():
    """作品点赞接口"""
    return app_list_api.post_works_like()


@app.route(f"{url}/comment/list", methods=["GET"])
def comment_list():
    """评论列表页接口"""
    return app_list_api.get_comment_list()


@app.route(f"{url}/works/comment", methods=["POST"])
@auth_user_login
def works_comment():
    """作品评论记录接口"""
    return app_list_api.post_comment_records()


@app.route(f"{url}/comment/like", methods=["POST"])
@auth_user_login
def works_comment_like():
    """作品评论点赞接口"""
    return app_list_api.post_comment_like()


@app.route(f"{url}/comment/delete", methods=["PUT"])
@auth_user_login
def works_comment_delete():
    """作品评论删除接口"""
    return app_list_api.put_delete_comment()


@app.route(f"{url}/comment/report", methods=["POST"])
@auth_user_login
def works_comment_report():
    """作品评论举报接口"""
    return app_list_api.post_comment_report()


@app.route(f"{url}/author/follow", methods=["POST"])
@auth_user_login
def author_follow():
    """作者关注接口"""
    return app_list_api.post_author_follow()


@app.route(f"{url}/custom/label/option", methods=["GET"])
def custom_label_option():
    """自定义供选标签接口"""
    return app_list_api.get_option_label()


@app.route(f"{url}/custom/label", methods=["POST"])
@auth_user_login
def custom_label():
    """自定义标签接口"""
    return app_list_api.post_custom_label()


@app.route(f"{url}/user/sales/record", methods=["GET"])
@auth_user_login
def user_sales_record():
    """用户销售记录接口"""
    return app_user_api.get_user_sales_records()


@app.route(f"{url}/user/data/statistic", methods=["GET"])
@auth_user_login
def user_data_statistic():
    """用户商品概况接口"""
    return app_user_api.get_user_data_statistic()



@app.route(f"{url}/user/paymethod", methods=["GET"])
@auth_user_login
def user_paymethod_show():
    """用户支付方式展示接口"""
    return app_user_api.get_user_paymethod_show()


@app.route(f"{url}/user/balance", methods=["GET"])
@auth_user_login
def user_balance():
    """用户账户余额接口"""
    return app_user_api.get_user_balance()


@app.route(f"{url}/user/home/page", methods=["GET"])
@auth_user_login
def user_home_page():
    """用户主页接口"""
    return app_user_api.get_user_home_page()


@app.route(f"{url}/user/follow/list", methods=["GET"])
def user_follow_list():
    """用户的关注列表"""
    return app_user_api.get_user_follow_list()


@app.route(f"{url}/user/fans/list", methods=["GET"])
def user_fans_list():
    """用户的粉丝列表"""
    return app_user_api.get_user_fans_list()


@app.route(f"{url}/user/works/manage", methods=["GET"])
@auth_user_login
def user_works_manage():
    """我的作品管理"""
    return app_user_api.get_works_manage()


@app.route(f"{url}/user/history/comment", methods=["GET"])
@auth_user_login
def user_history_comment():
    """我的历史评论记录"""
    return app_user_api.get_user_comment_history()


@app.route(f"{url}/user/upload/common", methods=["POST"])
@auth_user_login
def user_material_upload():
    """素材上传通用接口"""
    return app_works_api.post_material_upload_common()



















@app.route(f"{url}/admin/login", methods=["POST"])
def admin_login():
    """后台登录"""
    return admin_login_api.post_admin_login()


@app.route(f"{url}/admin/index/collect", methods=["GET"])
@auth_admin_login
def admin_index_top_collect():
    """后台首页顶部统计接口"""
    return admin_index_api.get_top_statistics()


@app.route(f"{url}/admin/index/trend", methods=["GET"])
@auth_admin_login
def admin_index_trend_collect():
    """后台首页趋势统计接口"""
    return admin_index_api.get_data_statistics()


@app.route(f"{url}/admin/banner/list", methods=["GET"])
@auth_admin_login
def admin_front_banner():
    """后台前台banner接口"""
    return admin_front_api.get_banner()


@app.route(f"{url}/admin/banner/link", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_banner_link():
    """后台前台banner修改链接接口"""
    return admin_front_api.put_banner_link()


@app.route(f"{url}/admin/banner/order", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_banner_order():
    """后台前台banner修改序号接口"""
    return admin_front_api.put_banner_order()


@app.route(f"{url}/admin/banner/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_banner_state():
    """后台前台banner删除接口"""
    return admin_front_api.put_banner_state()


@app.route(f"{url}/admin/hot/keyword", methods=["GET"])
@auth_admin_login
def admin_front_hot_keyword():
    """后台前台热搜词列表接口"""
    return admin_front_api.get_hot_keyword_list()


@app.route(f"{url}/admin/keyword/add", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_front_hot_keyword_add():
    """后台前台添加热搜词接口"""
    return admin_front_api.post_add_keyword()


@app.route(f"{url}/admin/keyword/delete", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_hot_keyword_delete():
    """后台前台删除热搜词接口"""
    return admin_front_api.put_delete_keyword()


@app.route(f"{url}/admin/label/list", methods=["GET"])
@auth_admin_login
def admin_front_label_list():
    """后台前台可选标签列表接口"""
    return admin_front_api.get_label_list()


@app.route(f"{url}/admin/label/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_label_state():
    """后台前台可选标签列表接口"""
    return admin_front_api.put_show_label()


@app.route(f"{url}/admin/user/list", methods=["GET"])
@auth_admin_login
def admin_user_list():
    """后台用户列表接口"""
    return admin_user_api.get_user_list()


@app.route(f"{url}/admin/user/filter", methods=["GET"])
@auth_admin_login
def admin_user_filter():
    """后台用户列表筛选接口"""
    return admin_user_api.get_user_filter_list()


@app.route(f"{url}/admin/user/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_state():
    """后台用户冻结恢复接口"""
    return admin_user_api.put_user_state()


@app.route(f"{url}/admin/user/detail", methods=["GET"])
@auth_admin_login
def admin_user_detail():
    """后台用户详情接口"""
    return admin_user_api.get_user_detail()


@app.route(f"{url}/admin/user/reset/password", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_reset_password():
    """后台用户重置密码接口"""
    return admin_user_api.put_user_password()


@app.route(f"{url}/admin/user/alter/mobile", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_alter_mobile():
    """后台用户更改手机接口"""
    return admin_user_api.put_user_mobile()


@app.route(f"{url}/admin/user/send/message", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_user_send_message():
    """后台给用户发送消息接口"""
    return admin_user_api.post_user_message()


@app.route(f"{url}/admin/user/balance/operation", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_balance_operatin():
    """后台用户余额操作接口"""
    return admin_user_api.put_user_balance_operation()


@app.route(f"{url}/admin/user/balance/record", methods=["GET"])
@auth_admin_login
@auth_amdin_role
def admin_user_balance_record():
    """后台用户余额记录接口"""
    return admin_user_api.put_user_balance_record()


@app.route(f"{url}/admin/org/list", methods=["GET"])
@auth_admin_login
def admin_org_list():
    """后台机构用户列表接口"""
    return admin_user_api.get_org_list()


@app.route(f"{url}/admin/user/audit", methods=["GET"])
@auth_admin_login
def admin_user_audit():
    """后台用户待审核列表接口"""
    return admin_user_api.get_user_audit()


@app.route(f"{url}/admin/user/audit/filter", methods=["GET"])
@auth_admin_login
def admin_user_audit_filter():
    """后台用户待审核列表搜索接口"""
    return admin_user_api.get_user_audit_filter()


@app.route(f"{url}/admin/comment/list", methods=["GET"])
@auth_admin_login
def admin_comment_list():
    """后台评论列表接口"""
    return admin_opinion_api.get_report_comment_list()


@app.route(f"{url}/admin/comment/search", methods=["GET"])
@auth_admin_login
def admin_comment_list_search():
    """后台评论列表搜索接口"""
    return admin_opinion_api.get_report_comment_search()


@app.route(f"{url}/admin/comment/audit", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_comment_audit():
    """后台评论审核接口"""
    return admin_opinion_api.put_report_comment_state()


@app.route(f"{url}/admin/price", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_platform_price():
    """后台平台定价接口"""
    return admin_operating_api.post_platform_pricing()


@app.route(f"{url}/admin/recomm/list", methods=["GET"])
@auth_admin_login
def admin_recomm_list():
    """后台推荐作品列表接口"""
    return admin_operating_api.get_recomm_works_list()


@app.route(f"{url}/admin/recomm/delete", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_recomm_delete():
    """后台推荐作品删除接口"""
    return admin_operating_api.put_recomm_state()


@app.route(f"{url}/admin/recomm/option", methods=["GET"])
@auth_admin_login
def admin_recomm_option():
    """后台推荐作品选择接口"""
    return admin_operating_api.get_option_works_list()


@app.route(f"{url}/admin/recomm/option/search", methods=["GET"])
@auth_admin_login
def admin_recomm_option_search():
    """后台推荐作品选择搜索接口"""
    return admin_operating_api.get_option_works_list_search()


@app.route(f"{url}/admin/recomm/add", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_recomm_add():
    """后台添加推荐作品接口"""
    return admin_operating_api.post_add_recomm_works()


@app.route(f"{url}/admin/manage/list", methods=["GET"])
@auth_admin_login
def admin_manage_list():
    """后台管理员列表接口"""
    return admin_system_api.get_admin_account_list()


@app.route(f"{url}/admin/manage/search", methods=["GET"])
@auth_admin_login
def admin_manage_search():
    """后台管理员列表接口"""
    return admin_system_api.get_admin_account_search()


@app.route(f"{url}/admin/manage/search", methods=["GET"])
@auth_admin_login
def admin_manage_search():
    """后台管理员列表接口"""
    return admin_system_api.get_admin_account_search()








@app.route(f"{url}/test", methods=["POST"])
def test():
    filetest = util.UploadSmallFile(app, ALLOWED_EXTENSIONS, 16 * 1024 * 1024, log)
    context = filetest.upload_file("file", "files", "qianfei")
    print(context)
    # if not context["code"]:
        # return util.response(msg=context["msg"], status=1)
    resp = util.response()
    print(context["file_path"])
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp










if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)