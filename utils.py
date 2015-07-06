# coding:utf-8
__author__ = 'zane'

from settings import *
import MySQLdb
import logging
import os
# import redis
# import pymongo
import traceback
import time
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

def error_log():
    try:
        from settings import ERROR_LOG_PATH
        ch = logging.FileHandler(filename=ERROR_LOG_PATH)
    except:
        if os.path.exists("/tmp/log/"):
            ch = logging.FileHandler(filename='/tmp/log/error.log')
        else:
            ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log = logging.getLogger('ERROR')
    log.propagate = False
    log.addHandler(ch)
    return log

def countTime(func):
    def temp(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logStr =  "%s spend %s" % (func.__name__, end - start)
        logging.error(logStr)
        return result
    return temp