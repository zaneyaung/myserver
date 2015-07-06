# coding:utf-8
__author__ = 'zane'

import tornado.ioloop
import tornado.template
import tornado.httpserver
import tornado.wsgi
from settings import *

import sys
import os
import traceback
import logging
import time

def main(port):

    dirs = os.listdir(".")
    urls = []
    for d in dirs:
        if os.path.exists("%s/urls.py" % d):
            exec("from %s.urls import urls as temp_urls" % d)
            urls.extend(temp_urls)
    from settings import settings
    application = tornado.web.Application(urls, **settings)
    global server
    server = tornado.httpserver.HTTPServer(application,xheaders=True)
    server.listen(port,address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main(int(sys.argv[1]))