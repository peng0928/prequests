from requests.exceptions import SSLError
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
logging.basicConfig(format='%(message)s', level=logging.INFO)


class prequest(Xpath):
    def __init__(self):
        self.response = Response()
        self.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.amount = 0
        self.samount = 0
        self.famount = 0

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
        :param retry_interval: retry interval default: 1
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
                self.amount += 1
                self.response.encoding = encoding
                if self.response.status_code == 200:
                    self.samount += 1
                    logging.info(
                        f'{self.datetime} [Spider] True [Method] {method} [Num] {self.amount} [Status] {self.response.status_code} [Url]: {self.response.url}')
                    return self
                else:
                    self.famount += 1
                    logging.error(
                        f'{self.datetime} [Spider] False [Method] {self.method} [Num] {self.amount} [Status] {self.response.status_code} [Url]: {self.response.url}')
                    raise TypeError(f'Respider {self.retry_interval}s')
            except SSLError as e:
                logging.error(e)
                return self
            except TypeError as e:
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
    def content(self):
        return self.response.content

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
    def get_len(self):
        return len(self.response.text)

    @property
    def tree(self):
        return Xpath(self.response.text)

    def __del__(self):
        msg = """
Requests: %s
Success Requests: %s
False Requests: %s
        """ % (self.amount, self.samount, self.famount)
        logging.info(msg)
