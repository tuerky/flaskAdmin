#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "tuerky"
# Date: 2019-07-10

import os
import sys
import configparser
import requests
import base64
import json
import pymysql.cursors


def get_config(key):
    os.chdir('./')
    cf = configparser.ConfigParser()
    cf.read('config.conf')
    if 'db' in key:
        host = cf.get(key, "db_host")  # 使用configparser模块获取配置参数
        port = cf.getint(key, "db_port")
        user = cf.get(key, "db_user")
        password = cf.get(key, "db_pass")
        db = cf.get(key, "db")
        charset = cf.get(key, "charset")
        curs = cf.get(key, "curs")
        config = [{'host': host, 'port': port, 'user': user, 'password': password, 'db': db, 'charset': charset,
                   'cursorclass': curs}]
        return config[0]
    elif 'url' in key:
        return [cf.get(key, "FrontUrl"), cf.get(key, "BackUrl")]


def execute_sql(db, sql):
    # formdir = os.path.dirname(os.getcwd())
    config_data = get_config(db)
    connection = pymysql.connect(**config_data)  # 数据库的链接
    # cur = connection.cursor()  # 获取一个游标
    try:
        with connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)  # 执行具体数据库操作
            data = cursor.fetchall()  # 将所有查询结果返回为元组,加上了字典游标返回的是字典
        connection.commit()

    finally:
        return data


def get_before_code():
    url = get_config('akc_package_url')[0] + '/verifCode'
    response = requests.get(url=url)
    res = response.text
    img = base64.b64decode(bytes(json.loads(res)['image'], encoding='utf-8'))
    with open('./static/verif_code.jpeg', 'wb') as f:
        f.write(img)

    return json.loads(res)['cookie']


def post_delivery(order_id, rand_code, cookie):
    url = get_config('akc_package_url')[0] + \
          '/deliver?orderId=' + order_id + '&randCode=' + rand_code + '&cookie=' + cookie
    response = requests.post(url=url)
    return response

