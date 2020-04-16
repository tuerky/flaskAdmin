#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "tuerky"
# Date: 2017/12/4

import random
import time


def co_build():  # 生成随机公司名
    co = "有限公司"
    first = ""
    for i in range(10):
        val = chr(random.randint(0x4e00, 0x9fbf))
        first += val
    return first + co


def rand_str(n=int, return_type=None):  # 返回n位随机中文字符或整数str(默认)
    if type(n) is not int:
        raise TypeError("this type must be int, not '%s'" % type(n))
    else:
        first = ""
        for i in range(n):
            val = chr(random.randint(0x4e00, 0x9fbf)) if return_type else str(base_random(10))
            first += val
        return first


def pop_nm():
    digit = int(random.random() * 10)  # 获取0到9的随机整数
    return digit


def tel_nm():  # 生成随机电话号码
    con = [17, 18, 13, 15]
    tend = int((random.random() * 100) / 25)
    middle = int(random.random() * 1000000000)
    # print(str(con[tend]) + str(middle))
    return str(con[tend]) + str(middle)


def contact_name():  # 生成随机联系人名称
    vat = ""
    for i in range(3):
        head = random.randint(0xb0, 0xf7)
        body = random.randint(0xa1, 0xfe)
        val = f'{head:x}{body:x}'
        vat += bytes.fromhex(val).decode('gb2312')
    # print(vat)
    return vat


def rand_id(count):
    res = ''
    num_set = [chr(i) for i in range(48, 58)]
    # print(num_set)
    char_set = [chr(i) for i in range(65, 91)]
    # print(char_set)
    symbol_set = ['-', '_']
    for i in range(count):
        rand_pick = base_rand(24)
        if 4 < rand_pick < 24:
            if base_random(2) > 0: get_char = char_set[base_random(26)].lower()
            else: get_char = char_set[base_random(26)]
        elif rand_pick > 23:
            get_char = symbol_set[base_random(2)]

        else:
            get_char = num_set[base_random(10)]
        res += get_char
    return res


def base_rand(digt):
    digit = int(random.random() * digt)  # 获取变量范围内的随机整数(1~digt)
    return digit + 1


def base_random(digt):
    digit = int(random.random() * digt)  # 获取变量范围内的随机整数(0~digt-1)
    return digit


class MySnow:

    def __init__(self, dataID):
        self.start = int(time.mktime(time.strptime('2018-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")))
        self.last = int(time.time())
        self.countID = 0
        self.dataID = dataID    # 数据ID，这个自定义或是映射

    def get_id(self):
        # 时间差部分
        now = int(time.time())
        temp = now - self.start
        if len(str(temp)) < 9:  # 时间差不够9位的在前面补0
            length = len(str(temp))
            s = "0" * (9-length)
            temp = s + str(temp)
        if now == self.last:
            self.countID += 1   # 同一时间差，序列号自增
        else:
            self.countID = 0    # 不同时间差，序列号重新置为0
            self.last = now
        # 标识ID部分
        if len(str(self.dataID)) < 2:
            length = len(str(self.dataID))
            s = "0" * (2 - length)
            self.dataID = s + str(self.dataID)
        # 自增序列号部分
        if self.countID == 99999:  # 序列号自增5位满了，睡眠一秒钟
            time.sleep(1)
        countIDdata = str(self.countID)
        if len(countIDdata) < 5:  # 序列号不够5位的在前面补0
            length = len(countIDdata)
            s = "0" * (5 - length)
            countIDdata = s + countIDdata
        id = str(temp) + str(self.dataID) + countIDdata
        return id


def encode_scale(shop_id):
    """
    :type shop_id: int
    """
    code_str = 'xxxxxxx'
    # 默认62位
    init_str = ''

    if shop_id is None: return ""
    else:
        while True:
            reminder = shop_id % 62
            init_str += code_str[int(reminder)]
            shop_id = shop_id / 62
            if shop_id <= 60:
                break
        init_str += code_str[int(shop_id)]
        # 反转字符串
        res_str = init_str[::-1]
    return res_str


def get_upper_int(_str):
    # 向上取整
    # 入参必须为字符串
    # 传入为小数，若为整数，返回自身
    if not isinstance(_str, str):
        raise Exception("error: _str must str type")

    if "." not in _str:
        return _str
    else:
        split_str = _str.split('.')[0]
        if _str[-1] != '0':
            return str(int(split_str) + 1)
        else:
            return split_str


def get_upper_ten_int(_str):
    # 向上取整十
    # 入参必须为字符串
    if not isinstance(_str, str):
        raise Exception("error: _str must str type")
    if "." not in _str:
        if _str[-1] == '0' and _str != '0':
            return _str
        else:
            return str((int(_str)//10 + 1) * 10)
    else:
        split_str = _str.split('.')[0]

        if _str[-1] == '0' and split_str[-1] == '0' and len(split_str) != 1:
            return split_str
        else:
            return str((int(split_str) // 10 + 1) * 10)


if __name__ == '__main__':
    # a=citycode(type='province')
    # __snow = MySnow(dataID='12')
    # print(__snow.get_id())
    # print(rand_id(22))
    # print(contact_name(), co_build())
    # print(encode_scale(653538918274842880))
    # print(get_upper_int("0.01"))
    print(get_upper_ten_int('20.3'))
