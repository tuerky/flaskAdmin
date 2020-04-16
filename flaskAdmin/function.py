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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis
import xlrd
import xmind
import time
# import datetime
from datetime import datetime, timedelta
from createRand import rand_id, MySnow, contact_name, base_random, tel_nm, encode_scale


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
    elif 'redis' in key:
        host = cf.get(key, "redis_host")
        port = cf.getint(key, "redis_port")
        password = cf.get(key, "redis_pass")
        db = cf.get(key, 'redis_db')
        max_connections = cf.getint(key, "redis_max_connections")
        config = [{'host': host, 'port': port, 'password': password, 'db': db, 'max_connections': max_connections}]
        return config[0]


def to_unix_time(interval):
    stat_date = datetime.strftime(datetime.now() + timedelta(days=interval), '%Y-%m-%d %H:%M:%S')
    unix_time = time.mktime(time.strptime(stat_date, '%Y-%m-%d %H:%M:%S'))
    return round(unix_time) * 1000


def get_change_time(date, interval):
    """
    :param date:
    :param interval: int
    :return: **2019-01-01 12:12:12
    """
    if date and date in "minutes":
        stat_date = datetime.strftime(datetime.now() + timedelta(minutes=interval), '%Y-%m-%d %H:%M:%S')
    elif date in "hours":
        stat_date = datetime.strftime(datetime.now() + timedelta(hours=interval), '%Y-%m-%d %H:%M:%S')
    elif date in "days":
        stat_date = datetime.strftime(datetime.now() + timedelta(days=interval), '%Y-%m-%d %H:%M:%S')
    else:
        raise TypeError("no support type %s !" % date)
    return stat_date


def time_interval(time):  # time 格式为2017-08-12 或2017-9-9 为str格式
    """
    :param time: 格式为2017-08-12 或2017-9-9 为str格式
    :return:  距离当前日期天数
    """
    year = int(time.split('-')[0])
    mon = time.split('-')[1]
    month = int(mon.lstrip('0'))
    d = time.split('-')[2]
    day = int(d.lstrip('0'))
    dic = dict(year=year, month=month, day=day)
    inter_day = (datetime.now() - datetime(dic['year'], dic['month'], dic['day'])).days
    return inter_day


class Secret:
    @staticmethod
    def tosecret(key):
        # print(((str(base64.b64encode(bytes(str(key), 'utf-8')))))[2:-1])
        return str(base64.b64encode(bytes(str(key), 'utf-8')))[2:-1]

    @staticmethod
    def exsecret(key):
        # print((base64.b64decode(key)).decode('utf-8'))
        return base64.b64decode(key).decode('utf-8')


def execute_sql(db, sql):
    # formdir = os.path.dirname(os.getcwd())
    config_data = get_config(db)
    connection = pymysql.connect(**config_data)  # 数据库的链接
    # cur = connection.cursor()  # 获取一个游标
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql)  # 执行具体数据库操作
        connection.commit()
        data = cursor.fetchall()  # 将所有查询结果返回为元组,加上了字典游标返回的是字典
    except Exception as e:
        print(e)
        connection.rollback()
    connection.close()
    return data


def redis_pool(redis_name):
    pool = redis.ConnectionPool(**get_config(redis_name))
    conn = redis.Redis(connection_pool=pool)
    return conn


def send_mail(name, mail, password):
    pass


class GetExcel:
    """
    :returns: iterable get all excel data && set first rows' values as key
    """

    def __init__(self, file):
        # 判断文件后缀名.xlsx
        if ".xlsx" in file:
            xlsx = xlrd.open_workbook(file)
            self.sheet_name_list = xlsx.sheet_names()
            self.sheet_list = xlsx.sheets()
            self.aim_dict = []
        else:
            raise TypeError("文件格式不对")

    def get_slice(self):
        for self.sheet in list(zip(self.sheet_list, self.sheet_name_list)):
            self.aim_dict.append(GetExcel.get_excel(self.sheet))
        return self.aim_dict

    @staticmethod
    def get_excel(data):
        try:
            n_rows = data[0].nrows
            n_cols = data[0].ncols
            content_list = []
            key_list = [data[1]]
            for x in range(n_rows):
                if x == 0:
                    for i in range(n_cols):
                        key_list.append(data[0].cell_value(0, i))
                else:
                    content_dict = {}
                    for y in range(n_cols):
                        if key_list[y + 1] == '':
                            pass
                        else:
                            data_list = data[0].cell_value(x, y).split('【')[1:] if isinstance(data[0].cell_value(x, y),
                                                                                              str) else None
                            if not data_list:
                                content_dict[key_list[y + 1]] = str(data[0].cell_value(x, y))
                            else:
                                new_list = []
                                for item in data_list:
                                    item = '【' + str(item)
                                    new_list.append(item)
                                content_dict[key_list[y + 1]] = new_list
                    content_list.append(content_dict)
            return [content_list, key_list]
        except Exception as err:
            print(err)


def create_xmind(dict_data, file):
    try:
        file_name = file if '.xlsx' not in file else file.split('.xlsx')[0]
        w = xmind.load(file_name + '.xmind')
        for i in range(len(dict_data)):
            s = w.getPrimarySheet() if i == 0 else w.createSheet()
            s.setTitle(dict_data[i][1][0])  # set its title
            global r  # 初始使用变量，需要在下面的方法中查找，提供全局
            r = s.getRootTopic()  # get the root topic of this sheet
            r.setTitle(dict_data[i][1][0])  # 设置主分支标题，同sheet都相同
            # 设置循环标签 不超过26位
            topic_list = list(map(chr, range(ord('a'), ord('z') + 1)))
            topic_list.pop(17)
            topic_list.pop(18)
            for item in enumerate(dict_data[i][0]):
                preview_ct = 1
                for dict_ct in range(len(item[1])):
                    if dict_ct == 0:
                        current_topic = item[1][dict_data[i][1][dict_ct + 1]]
                        key = dict_data[i][1][dict_ct + 1]
                        topic_name = topic_list[dict_ct]
                        prev_topic_name = 'r'
                        preview_ct = sort_liter(preview_ct, current_topic, key, topic_name, prev_topic_name)
                    else:
                        current_topic = item[1][dict_data[i][1][dict_ct + 1]]
                        key = dict_data[i][1][dict_ct + 1]
                        topic_name = topic_list[dict_ct]
                        prev_topic_name = topic_list[dict_ct - 1]
                        preview_ct = sort_liter(preview_ct, current_topic, key, topic_name, prev_topic_name)

        xmind.save(w, file_name + '.xmind')
    except Exception as err:
        print(err)


def sort_liter(preview_ct, current_topic, key, topic_name, prev_topic_name):
    names = globals()
    current_ct = 1
    if preview_ct > 1 and isinstance(current_topic, list):
        for ct in range(len(current_topic)):
            names[topic_name + str(ct)] = names[prev_topic_name + str(ct)].addSubTopic()
            names[topic_name + str(ct)].setTitle(key + ':' + current_topic[ct])
            current_ct += 1
        return current_ct
    if preview_ct > 1 and not isinstance(current_topic, list):
        for ct in range(0, preview_ct - 1):
            names[topic_name + str(ct)] = names[prev_topic_name + str(ct)].addSubTopic()
            names[topic_name + str(ct)].setTitle(key + ':' + current_topic)
            current_ct += 1
        return current_ct

    if preview_ct <= 1 and isinstance(current_topic, list):
        for ct in range(len(current_topic)):
            names[topic_name + str(ct)] = names[prev_topic_name].addSubTopic()
            names[topic_name + str(ct)].setTitle(key + ':' + current_topic[ct])
            current_ct += 1
        return current_ct
    if preview_ct <= 1 and not isinstance(current_topic, list):
        names[topic_name] = names[prev_topic_name].addSubTopic()
        names[topic_name].setTitle(key + ':' + current_topic)
        return current_ct


def post_operate_redis_key(func, key, value=None):
    """
    :param func: redis 操作方式
    :param key: key值
    :param value: 若有需要set的值，则为新值
    :return: get返回值，set返回旧值，delete、append返回1为成功
    """
    conn = redis_pool('redis_h5_member')
    if func == 'get':
        res = conn.get(key)
        print(res)
    elif func == 'set':
        res = conn.getset(key, value)
        print(res)
    elif func == 'delete':
        res = conn.delete(key)
        return res
    elif func == 'append':
        res = conn.append(key, value)
        return res


if __name__ == "__main__":
    pass