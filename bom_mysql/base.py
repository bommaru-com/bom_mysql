#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
# import re
import sys
import atexit
import pymysql

from sshtunnel import SSHTunnelForwarder
from loguru import logger
from dotenv import load_dotenv


"""
bom_mysql base module.

This is the principal module of the bom_mysql project.
here you put your main classes and objects.

Be creative! do whatever you want!

If you want to replace this with a Flask application run:

    $ make init

and then choose `flask` as template.
"""


'''
class BaseClass:
    def base_method(self) -> str:
        """
        Base method.
        """
        return "hello from BaseClass"

    def __call__(self) -> str:
        return self.base_method()


def base_function() -> str:
    """
    Base function.
    """
    return "hello from base function"
'''


class MysqlConnect(object):

    def __init__(self, conf):
        """
        mysql 연결

        맥의 경우만 tunnel처리후 mysql 커넥션 처리

        Property
        --------
        tunnel: obj
            ssh tunnel object
        conn: obj
            mysql connection
        cursor: obj
            mysql cursor
        """

        logger.debug(conf)
        self.tunnel = None
        self.conn = None
        self.cursor = None

        if sys.platform == "darwin" or conf["tunnel"]:
            sshconf = {
                "ssh_username": conf["ssh_username"],
                "ssh_pkey": conf["ssh_pkey"],
                "remote_bind_address": (conf["host"], conf["port"])
            }
            self.tunnel = SSHTunnelForwarder((conf["ssh_host"], conf["ssh_port"]), **sshconf)
            self.tunnel.start()
            conf["host"] = '127.0.0.1'
            conf["port"] = self.tunnel.local_bind_port
            logger.debug("tunneling start")

        mysqlconf = {
            "host": conf["host"],
            "user": conf["user"],
            "passwd": conf["passwd"],
            "db": conf["db"],
            "port": conf["port"]
        }
        self.conn = pymysql.connect(**mysqlconf)
        self.cursor = self.conn.cursor()
        logger.debug("mysql connection open")

        atexit.register(self.cleanup)

    def __call__(self):
        return self.__init__()

    def cleanup(self):
        """db close, tunnel stop"""
        logger.debug("mysql connection close")
        self.cursor.close()
        self.conn.close()

        if self.tunnel:
            logger.debug("tunneling stop")
            self.tunnel.stop()

    def loadenv(self):
        load_dotenv(verbose=True)  # verbose .env 파일 누락 등의 경고 메시지를 출력할 것인지에 대한 옵션
        return {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USERNAME"),
            "passwd": os.getenv("DB_PASSWORD"),
            "db": os.getenv("DB_DEFAULT"),
            "port": int(os.getenv("DB_PORT")),
            "ssh_host": os.getenv("SSH_HOST"),
            "ssh_username": os.getenv("SSH_USERNAME"),
            "ssh_pkey": os.getenv("SSH_PRIVATE_KEY"),
            "ssh_port": int(os.getenv("SSH_PORT")),
            "tunnel": int(os.getenv("TUNNEL"))
        }
