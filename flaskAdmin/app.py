#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "tuerky"
# Date: 2019-05-22

import os
import platform
from flask import Flask, g, session, Blueprint, url_for, request, render_template, redirect, send_from_directory, \
    send_file, make_response
from function import get_config, get_before_code, post_delivery, post_aftersale, Secret, execute_sql, send_mail, \
    post_set_tag, post_refund, get_banner, post_set_banner, post_modify_inventory, post_update_display, GetExcel, \
    create_xmind, delete_user_tag, refresh_skins_redis, create_virtual_wx_account, distributor_register, trash_member_redis
import json, time, xmind
from datetime import timedelta

auth_bp = Flask(__name__, template_folder='templates')

# admin.init_app(app)

# flask中的session会用到的密钥字符串
auth_bp.config['SECRET_KEY'] = os.urandom(24)
# 默认session过期时间为30天，下面代码设置为5小时过期
auth_bp.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
# 配置分页url集合
task_url = ['tasks', 'task_banner/test']
activity_url = ['activity', 'activity_bak']


@auth_bp.route('/index/', methods=['get', 'post'])
def index():
    if session == {}:
        return render_template("login.html")
    else:
        user_name = '@' + session['name']
        return render_template("index.html", userName=user_name)


@auth_bp.route('/register', methods=['get', 'post'])
def register():
    # 枚举
    json_msg = [
        {
            "msg_code": 0,
            "message": "注册成功,请重新登录"
        }, {
            "msg_code": 201,
            "message": "该用户已存在,请直接登录"
        }, {
            "msg_code": 301,
            "message": "注册失败"
        }, {
            "msg_code": 401,
            "message": "任意项不能为空"
        }
    ]
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    if (name is None or not name != '') or (password is None or not '' != password) or (
            email is None or not '' != email):
        return json.dumps(json_msg[3])
    else:
        pick_sql = "select " \
                   "     `password` " \
                   "from " \
                   "     `flask_user` " \
                   "where " \
                   "     `is_delete` = '0' and" \
                   "     `name` = '%s'" % name
        data = execute_sql(db="db_local_mac", sql=pick_sql)
        if data:
            return json.dumps(json_msg[1])
        else:
            try:
                insert_sql = "insert into " \
                             "      `flask_user` " \
                             "values " \
                             "      ('0','%s','%s','%s',NOW(),NOW(),'0', NULL, NULL);" % (
                                 name, Secret.tosecret(password), email
                             )
                execute_sql(db="db_local_mac", sql=insert_sql)
                return json.dumps(json_msg[0])
            except Exception as err:
                print(err)
                return json.dumps(json_msg[2])


@auth_bp.route('/login', methods=['get', 'post'])
def login():
    # 枚举
    json_msg = [
        {
            "msg_code": 200,
            "message": "登录成功"
        }, {
            "msg_code": 201,
            "message": "用户名或密码错误"
        }, {
            "msg_code": 301,
            "message": "用户不存在请注册"
        }, {
            "msg_code": 302,
            "message": "用户名、密码不能为空"
        }]
    name = request.values.get('name')
    password = request.values.get('password')
    if name == 'admin' and password == '123456':
        session['name'] = name
        session['password'] = Secret.tosecret(password)
        print(session)
        return json.dumps(json_msg[0])
    else:

        if (name is None or not name != '') or (password is None or not '' != password):
            return json.dumps(json_msg[3])
        else:
            pick_sql = "select " \
                       "     `password` " \
                       "from " \
                       "     `flask_user` " \
                       "where " \
                       "     `is_delete` = '0' and" \
                       "     `name` = '%s'" % name
            data = execute_sql(db="db_local_mac", sql=pick_sql)
            if not data:
                return json.dumps(json_msg[2])
            elif password == Secret.exsecret(data[0]['password']):
                session['name'] = name
                session['password'] = Secret.tosecret(password)
                print(session)
                return json.dumps(json_msg[0])
            else:
                return json.dumps(json_msg[1])


@auth_bp.route('/logout', methods=['get', 'post'])
def logout():
    session = {}
    return render_template("login.html")


@auth_bp.route('/forgot', methods=['get', 'post'])
def forgot():
    json_msg = [
        {
            "msg_code": 201,
            "message": "请至邮箱查收密码信息,重新登录"
        }, {
            "msg_code": 301,
            "message": "用户名不可为空"
        }, {
            "msg_code": 401,
            "message": "该用户不存在"
        }

    ]
    name = request.form.get('name')
    if name is None or name == '':
        return json.dumps(json_msg[1])
    else:
        pick_sql = "select " \
                   "     `password`, " \
                   "     `email` " \
                   "from " \
                   "     `flask_user` " \
                   "where " \
                   "     `is_delete` = '0' and" \
                   "     `name` = '%s'" % name
        data = execute_sql(db="db_local_mac", sql=pick_sql)
        if not data:
            return json.dumps(json_msg[2])
        else:
            password = data[0]['password']
            email = data[0]['email']
            send_mail(name=name, mail=email, password=Secret.exsecret(password))
            return json.dumps(json_msg[0])


@auth_bp.route('/profile', methods=['get', 'post'])
def profile():
    try:
        name = session['name']
        user_name = '@' + session['name']
        pick_sql = "select " \
                   "     `email`, " \
                   "     `phone`, " \
                   "     `description` " \
                   "from " \
                   "     `flask_user` " \
                   "where " \
                   "     `is_delete` = '0' and" \
                   "     `name` = '%s'" % name
        data = execute_sql(db="db_local_mac", sql=pick_sql)
        email = data[0]['email']
        phone = data[0]['phone']
        description = data[0]['description']
        return render_template("profile.html", userName=user_name, name=name, email=email, phone=phone,
                               description=description)
    except:
        return render_template("login.html")


@auth_bp.route('/saveProfile', methods=['get', 'post'])
def save_profile():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    description = request.form.get('description')
    if not name:
        return redirect(url_for("profile"))
    else:
        save_sql = "update \n" \
                   "    `flask_user` \n" \
                   "set `email` = '%s', \n" \
                   "    `phone` = '%s', \n" \
                   "    `description` = '%s' \n" \
                   "WHERE \n" \
                   "    `name` = '%s';" % (email, phone, description, name)
        # print(save_sql)
        execute_sql(db="db_local_mac", sql=save_sql)
        return render_template("profile.html", name=name, email=email, phone=phone, description=description)


# 流程工具
@auth_bp.route('/activity', methods=['get', 'post'])
def activity():
    if session == {}:
        return render_template('login.html')
    else:
        user_name = '@' + session['name']
        cookie = get_before_code()
        return render_template('activity.html', userName=user_name, cookie=cookie, args=1, url_list=activity_url)


@auth_bp.route('/activity_bak', methods=['get', 'post'])
def activity_bak():
    if session == {}:
        return render_template('login.html')
    else:
        user_name = '@' + session['name']
        # 歌词数据
        sql = 'select `title`,`pic_url`,`singer`,`lyric` from `music_newest`'
        data_list = execute_sql(db='db_local_mac', sql=sql)
        return render_template('activity_bak.html', userName=user_name, args=2, url_list=activity_url,
                               content_arr=data_list)


# 配置工具
@auth_bp.route('/tasks', methods=['get', 'post'])
def tasks():
    if session == {}:
        return render_template('login.html')
    else:
        user_name = '@' + session['name']
        return render_template('tasks.html', userName=user_name, args=1, url_list=task_url)


# 退款工具
@auth_bp.route('/projects', methods=['get', 'post'])
def projects():
    if session == {}:
        return render_template('login.html')
    else:
        user_name = '@' + session['name']
        return render_template('projects.html', userName=user_name)


# 配置分类修改
@auth_bp.route('/setTag', methods=['get', 'post'])
def set_tag():
    if request.method == 'POST':
        json_data = request.get_data()
        data = json.loads(json_data)
        env = str(request.values.get('env')) if request.values.get('env') else ''
        res = post_set_tag(env=env, data=data)
        json_data = json.loads(res.text)
        return json.dumps(json_data)


# 配置banner
@auth_bp.route('/task_banner/<env>', methods=['get', 'post'])
def task_banner(env=None):
    if session == {}:
        return render_template('login.html')
    else:
        user_name = '@' + session['name']
        # 初始化banner接口数据
        res = get_banner('test' if not env else env)
        json_data = json.loads(res.text)
        banner_list = json_data['data']
        return render_template('task_banner.html', userName=user_name, args=2, url_list=task_url,
                               env='test' if not env else env,
                               banner_list=banner_list)


# set banner
@auth_bp.route('/setBanner', methods=['get', 'post'])
def set_banner():
    if request.method == 'POST':
        json_data = request.get_data()
        data = json.loads(json_data)
        env = str(request.values.get('env')) if request.values.get('env') else ''
        res = post_set_banner(env=env, data=data)
        json_data = json.loads(res.text)
        return json.dumps(json_data)


# 点击获取验证码
@auth_bp.route('/verify_code', methods=['get', 'post'])
def get_verify_code():
    cookie = get_before_code()
    res = {"cookie": cookie}
    return json.dumps(res)


@auth_bp.route('/delivery_order', methods=['get', 'post'])
def order_delivery():
    order_id = str(request.form.get('orderId')) if request.form.get('orderId') else ''
    rand_code = str(request.form.get('randCode')) if request.form.get('orderId') else ''
    cookie = request.form.get('cookie')
    res = post_delivery(order_id, rand_code, cookie)
    json_data = json.loads(res.text)
    return json.dumps(json_data)


@auth_bp.route('/afterSale', methods=['get', 'post'])
def order_aftersale():
    service_id = str(request.form.get('serviceId')) if request.form.get('serviceId') else ''
    execute_method = str(request.form.get('executeMethod')) if request.form.get('executeMethod') else ''
    res = post_aftersale(service_id, execute_method)
    json_data = json.loads(res.text)
    return json.dumps(json_data)


@auth_bp.route('/modifyInventory', methods=['get', 'post'])
def modify_inventory():
    if request.method == 'POST':
        json_data = request.get_data()
        data = json.loads(json_data)
        res = post_modify_inventory(data=data)
        json_data = json.loads(res.text)
        return json.dumps(json_data)


@auth_bp.route('/updateDisplay', methods=['get', 'post'])
def update_display():
    if request.method == 'POST':
        json_data = request.get_data()
        data = json.loads(json_data)
        res = post_update_display(data=data)
        json_data = json.loads(res.text)
        return json.dumps(json_data)


@auth_bp.route('/refund', methods=['get', 'post'])
def order_refund():
    order_line_id = str(request.form.get('orderLineId')) if request.form.get('orderLineId') else ''
    res = post_refund(order_line_id)
    json_data = json.loads(res.text)
    return json.dumps(json_data)


@auth_bp.route('/upload', methods=['get', 'post'])
def post_upload():
    json_msg = [
        {
            "code": 200,
            "message": "上传成功，生成转化文件"
        }, {
            "code": 301,
            "message": "上传异常"
        }

    ]
    if request.method == 'POST':
        try:
            file_name = request.form.get('file_name')
            print(file_name)
            file = request.files.get('file')
            file.save(file_name)
            __excel = GetExcel(file=file_name)
            create_xmind(__excel.get_slice(), file=file_name)
            os.remove(file_name)
            return json.dumps(json_msg[0])
        except Exception as err:
            print(err)
            return json.dumps(json_msg[1])


@auth_bp.route('/download', methods=['get', 'post'])
def post_download():
    if request.method == 'GET':
        file_name = str(request.values.get('file')) if request.values.get('file') else ''
        file_new_name = file_name if '.xlsx' not in file_name else file_name.split('.xlsx')[0] + '.xmind'
        res = make_response(send_from_directory(directory=auth_bp.root_path, filename=file_new_name))
        os.remove(file_new_name)
        return res


@auth_bp.route('/freshUserTag', methods=['get', 'post'])
def fresh_user_tag():
    json_msg = [
        {
            "code": 200,
            "message": "刷新缓存成功"
        }, {
            "code": 301,
            "message": "刷新异常"
        }

    ]
    if request.method == 'POST':
        shop_id = str(request.args['shop_id']) if request.args['shop_id'] else ''
        user_id = str(request.args['user_id']) if request.args['user_id'] else ''
        user_type = str(request.args['type']) if request.args['type'] else ''
        try:
            delete_user_tag(shop_id=shop_id, user_id=user_id, user_type=user_type)
            return json.dumps(json_msg[0])
        except Exception as err:
            json_msg[1]['message'] = str(err)
            return json.dumps(json_msg[1])


@auth_bp.route('/freshSkinRedis', methods=['get', 'post'])
def fresh_skin_redis():
    json_msg = [
        {
            "code": 200,
            "message": "刷新缓存成功"
        }, {
            "code": 301,
            "message": "刷新异常"
        }

    ]
    if request.method == 'POST':
        shop_id = str(request.args['shop_id']) if request.args['shop_id'] else ''
        try:
            refresh_skins_redis(shop_id)
            return json.dumps(json_msg[0])
        except Exception as err:
            json_msg[1]['message'] = str(err)
            return json.dumps(json_msg[1])


@auth_bp.route('/trashMemberInfo', methods=['get', 'post'])
def trash_member_info():
    json_msg = [
        {
            "code": 200,
            "message": "xx成功"
        }, {
            "code": 301,
            "message": "xx失败"
        }

    ]
    if request.method == 'POST':
        open_id = str(request.args['open_id']) if request.args['open_id'] else ''
        try:
            trash_member_redis(open_id=open_id)
            return json.dumps(json_msg[0], ensure_ascii=False)
        except Exception as err:
            json_msg[1]['message'] = str(err)
            return json.dumps(json_msg[1], ensure_ascii=False)


@auth_bp.route('/createVirtualDistributor', methods=['get', 'post'])
def create_virtual_distributor():
    json_msg = [
        {
            "code": 200,
            "message": "xx成功"
        }, {
            "code": 301,
            "message": "xx失败"
        }

    ]
    if request.method == 'POST':
        shop_id = str(request.args['shop_id']) if request.args['shop_id'] else ''
        open_id = str(request.args['open_id']) if request.args['open_id'] else ''
        ms_token = str(request.args['ms_token']) if request.args['ms_token'] else ''
        try:
            create_virtual_wx_account(open_id)
            distributor_register(shop_id=shop_id, open_id=open_id, ms_token=ms_token)
            return json.dumps(json_msg[0], ensure_ascii=False)
        except Exception as err:
            json_msg[1]['message'] = str(err)
            return json.dumps(json_msg[1], ensure_ascii=False)


if __name__ == '__main__':
    auth_bp.run(
        "0.0.0.0",
        5000,
        debug=True
    )
