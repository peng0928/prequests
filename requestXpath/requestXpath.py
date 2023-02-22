from requests.exceptions import  SSLError
import requests
import logging
import time
import json
from requests.models import Response
from .useragent import get_ua
from .pxpath import Xpath
import datetime

"""
-------------------------------------------------
   File Name:     prequest
   Description :   Network Requests Class
   Author :        penr
   date:          2023/02/16
-------------------------------------------------
   Change Activity:
                   2023/02/16:
-------------------------------------------------
"""
__author__ = 'penr'
__version__ = 0.1


class prequests(Xpath):
    def __init__(self):
        self.response = Response()
        self.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @property
    def user_agent(self):
        """
        :return: an User-Agent at random
        """
        return get_ua()

    @property
    def header(self):
        """
        :return: basic header
        """
        return {'user-agent': self.user_agent}

    def get(self, url, headers=None, retry_time=3, method='get', encoding='utf-8', retry_interval=1, timeout=3, *args,
            **kwargs):
        """
        get method
        :param url: target url
        :param header: headers default:
        :param retry_time: retry time default: 3
        :param retry_interval: retry interval default: 0
        :param timeout: network timeout default: 3
        :return:
        """
        header = self.header
        self.method = method
        self.retry_time = retry_time
        self.retry_interval = retry_interval
        if headers and isinstance(headers, dict):
            header.update(headers)
        while True:
            try:
                self.response = requests.request(
                    url=url, headers=header, timeout=timeout, method=method, *args, **kwargs)
                self.response.encoding = encoding
                if self.response.status_code == 200:
                    logging.warning(
                        f'{self.datetime}[Spider]: True [method]: {method} [status]: {self.response.status_code} [url]: {self.response.url}')
                    return self
                else:
                    logging.error(
                        f'{self.datetime}[ReSpider]: False [method]: {self.method} [status]: {self.response.status_code} [url]: {self.response.url}')
                    raise Exception('请求失败')
            except SSLError as e:
                logging.error(e)
                return self
            except Exception as e:
                logging.error(e)
                retry_time -= 1
                if retry_time <= 0:
                    resp = Response()
                    resp.status_code = 200
                    return self
                time.sleep(retry_interval)

    @property
    def text(self):
        return self.response.text

    @property
    def url(self):
        return self.response.url

    @property
    def history(self):
        return self.response.history

    @property
    def json(self):
        return json.loads(self.response.text)

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def headers(self):
        return self.response.headers

    @property
    def tree(self):
        return Xpath(self.response.text)
