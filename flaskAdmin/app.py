#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "tuerky"
# Date: 2019-05-22

from flask import Flask, url_for, request, render_template
from flask.ext.admin import Admin, BaseView, expose, AdminIndexView
from function import get_config, get_before_code, post_delivery
import json


class DeliveryView(BaseView):

    @expose('/')
    def index(self):
        # Get URL for the test view method
        # url = url_for('.aftersale')
        cookie = get_before_code()
        return self.render('delivery.html', cookie=cookie)

    @expose('/delivery/')
    def delivery(self):
        # url = url_for('aftersale.index')
        return self.render('delivery.html')


class AftersaleView(BaseView):
    
    @expose('/')
    def index(self):
        # Get URL for the test view method
        # url = url_for('.aftersale')
        return self.render('aftersale.html')

    @expose('/aftersale/')
    def aftersale(self):
        # url = url_for('delivery')
        return '<a>aftersale</a>'


class ActivityView(BaseView):
    
    @expose('/')
    def index(self):
        # Get URL for the test view method
        # url = url_for('.aftersale')
        return self.render('index.html')
    
    @expose('/create_activity/')
    def create_activity(self):
        # url = url_for('create_activity.index')
        return self.render('delivery.html')
    
    
class AutoView(BaseView):
    
    @expose('/')
    def index(self):
        # Get URL for the test view method
        # url = url_for('.aftersale')
        return self.render('index.html')

    @expose('/openapi/')
    def create_activity(self):
        # url = url_for('create_activity.index')
        return self.render('delivery.html')


class H5View(BaseView):

    @expose('/')
    def index(self):
        # Get URL for the test view method
        # url = url_for('.aftersale')
        return self.render('index.html')

    @expose('/h5/')
    def create_activity(self):
        # url = url_for('create_activity.index')
        return self.render('delivery.html')


app = Flask(__name__, template_folder='templates')
# set optional bootswatch theme

admin = Admin(
    app,
    index_view=AdminIndexView(
        name='质量工具平台',
        template='login.html',
        url='/admin'
    )
)


admin.add_view(DeliveryView(name='截单发货', endpoint='delivery', category='工具化'))
admin.add_view(AftersaleView(name='售后流程', endpoint='aftersale', category='工具化'))
admin.add_view(ActivityView(name='创建活动', endpoint='create_activity', category='工具化'))
admin.add_view(AutoView(name='openapi接口自动化', endpoint='openapi', category='接口自动化'))
admin.add_view(H5View(name='h5商城接口自动化', endpoint='h5', category='接口自动化'))
# admin.init_app(app)


@app.route('/delivery/order', methods=['get', 'post'])
def order_delivery():
    order_id = request.form.get('orderId')
    rand_code = request.form.get('randCode')
    cookie = request.form.get('cookie')
    res = post_delivery(order_id, rand_code, cookie)
    json_data = json.loads(res.text)
    return render_template("finish_delivery.html", msgCode=json_data['msg_code'])


if __name__ == '__main__':
    app.run(
        "0.0.0.0",
        5000,
        debug=True
    )

