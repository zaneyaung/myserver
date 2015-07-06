# coding:utf-8
__author__ = 'zane'

import sys
import os

file_path = os.path.dirname(__file__)
print file_path
sys.path.insert(0,file_path)
from tornado.web import RequestHandler
class TestHandler(RequestHandler):
    def get(self, *args, **kwargs):
        data = {"data":1,"status":1}
        self.render("test.html",data=data)

