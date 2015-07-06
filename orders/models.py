# coding:utf-8
__author__ = 'zane'
from utils import *
#list all table fileds and data type
table_field = {
    "uid" : int,
    "shop_id ": int,
    "test_id ": str,
    "reserved1":str
}

class ORDER:
    '''
    Comment: This class attend to scape order data from db orders
    '''
    def __init__(self,*args,**kwargs):
        for r in kwargs:
            self.r = kwargs['%s'] %r

    def __getattr__(self, item):
        pass

    def QueryOrderByuid(self):
        pass
