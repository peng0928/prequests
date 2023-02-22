from requests.exceptions import ProxyError, Timeout, SSLError
import random
from urllib.parse import urljoin
import requests
import logging
import time
import json
import re
from lxml import etree
from requests.models import Response
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

class Xpath(object):
    def __init__(self, response, encoding='utf-8'):
        if isinstance(response, str):
            self.res = etree.HTML(response)
        else:
            response.encoding = encoding
            self.res = etree.HTML(response.text)

    def xpath(self, x=None, filter='style|script', character=True, is_list=False, easy=False, rule=None):
        """
        x: xpath 语法
        filter: 过滤器
        character: join方法带换行
        is_list: 是否为列表 True 列表,
        easy: xpath默认子集关系
        rule: 正则提取
        """
        try:
            if filter != None and len(filter) > 0:
                tree = self.xpath_filter(self.res, filter=filter)
                x = x.split('|')
                if easy:
                    x = [i + '/text()' if '/@' not in i else i for i in x]
                else:
                    x = [i + '//text()' if '/@' not in i else i for i in x]
                x = '|'.join(x)

                obj = tree.xpath(x)
                obj = self.process_text(obj, character, is_list)

            else:
                x = x.split('|')
                if easy:
                    x = [i + '/text()' if '/@' not in i else i for i in x]
                else:
                    x = [i + '//text()' if '/@' not in i else i for i in x]
                x = '|'.join(x)
                obj = self.res.xpath(x)
                obj = self.process_text(obj, character, is_list)

            if rule:
                if obj:
                    if isinstance(obj, list):
                        for i in obj:
                            getrule = re.findall(rule, i)
                            if getrule:
                                obj = getrule[0]
                                break
                            else:
                                obj = None
                    else:
                        getrule = re.findall(rule, obj)
                        obj = getrule[0] if getrule else None
            return obj
        except Exception as e:
            print(e)
            return None

    def xxpath(self, x=None):
        return self.res.xpath(x)

    def dpath(self, x=None, rule=None):
        x = x.split('|')
        x = [i + '//text()' if '/@' not in i else i for i in x]
        x = '|'.join(x)

        obj = self.res.xpath(x)
        obj = ' '.join(obj)
        obj = self.process_date(data=obj, rule=rule)
        return obj

    def fxpath(self, x=None, p='', h='', rule=None):
        le = x.split('|')
        if len(le) > 1:
            x = x.split('|')
            for item in x:
                p += item + '//text()|'
                h += item + '//@href|'
            p = p[:-1]
            h = h[:-1]
        else:
            p = x + '//text()'
            h = x + '//@href'

        filename = self.res.xpath(p) or None
        filelink = self.res.xpath(h) or None
        fn = []
        fk = []
        try:
            if filename is not None and filelink is not None:
                for i in range(len(filelink)):
                    is_file = bool(
                        re.search(r'(\.tar|\.shtml|\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar|\.jpg)',
                                  str(filename[i])))
                    is_link = bool(
                        re.search(r'(\.tar|\.shtml|\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar|\.jpg)',
                                  str(filelink[i])))
                    if is_file or is_link:
                        fn.append(filename[i])
                        fk.append(filelink[i])
                    else:
                        pass
                if fn is not None and fk is not None:
                    filename = '|'.join(fn)
                    filename = self.replace(filename).replace('\n', '')
                    filelink = [urljoin(rule, i) for i in fk]
                    filelink = '|'.join(filelink)

                if len(filelink) == 0 or len(filename) == 0:
                    return None, None
                else:
                    return filename, filelink
            else:
                return None, None
        except:
            return None, None

    def process_date(self, data=None, rule=None):
        if len(data) == 0:
            return None
        if len(data) == 13 and '.' not in data and '-' not in data and '/' not in data:
            localtime = time.localtime(int(data) / 1000)
            date = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            return date

        if len(data) == 10 and '.' not in data and '-' not in data and '/' not in data:
            localtime = time.localtime(int(data))
            date = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            return date

        else:
            if rule != None:
                patten = '%s.*?(\d{1,4}[-|/|.|年]\d{1,2}[-|/|.|月]\d{1,2}[-|/|.|日]*)[\s]*([\d{1,2}]*[:|时]*[\d{1,2}]*[:分]*[\d{1,2}]*[秒]*)' % rule
                result = re.findall(patten, data)
            else:
                patten = r'(\d{1,4}[-|/|.|年]\d{1,2}[-|/|.|月]\d{1,2}[-|/|.|日]*)[\s]*([\d{1,2}]*[:|时]*[\d{1,2}]*[:分]*[\d{1,2}]*[秒]*)'
                result = re.findall(patten, data)

            result = ' '.join(result[0]).replace('.', '-').replace('/', '-').replace('年', '-').replace('月', '-').replace(
                '日', '').strip()
            return result

    def replace(self, str):
        result = re.sub(r'(\\u[a-zA-Z0-9]{4})', lambda x: x.group(
            1).encode("utf-8").decode("unicode-escape"), str)
        result = re.sub(r'(\\r|\\n|\\t|\xa0)', lambda x: '', result)
        return result.strip()

    # etree解析

    def process_text(self, obj, character=True, is_list=False):
        try:
            obj = [self.replace(i) for i in obj]
            obj = [i for i in obj if len(i) > 0]
            if is_list:
                return obj
            character = '\n' if character else ''
            result = character.join(obj)
            return result
        except Exception as e:
            print(e)
            return None

    def xpath_filter(self, response=None, filter=None):
        filter_num = filter.split('|')
        if len(filter_num) > 1:
            filter = filter.split('|')
            filter = '//' + '|//'.join(filter)
        else:
            filter = '//' + filter
        # tree = etree.HTML(response)
        ele = response.xpath(filter)
        for e in ele:
            e.getparent().remove(e)
        return response


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

    def get(self, url, headers=None, retry_time=3, method='get', encoding='utf-8', retry_interval=1, timeout=3, *args, **kwargs):
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

        if headers and isinstance(headers, dict):
            header.update(headers)
        while True:
            try:
                self.response = requests.request(
                    url=url, headers=header, timeout=timeout, method=method,  *args, **kwargs)
                self.response.encoding = encoding
                if self.response.status_code != 200:
                    raise ValueError('requests status:',
                                     self.response.status_code,)
                logging.warning(
                    f'{self.datetime}[Spider]: True [method]: {method} [status]: {self.response.status_code} [url]: {self.response.url}')
                return self
            except ProxyError as e:
                logging.error(e)
                return self
            except Timeout as e:
                logging.error(e)
                return self
            except SSLError as e:
                logging.error(e)
                return self
            except ValueError:
                # self.log.error("requests: %s error: %s" % (url, str(e)))
                logging.error(
                    f'{self.datetime}[ReSpider]: False [method]: {method} [status]: {self.response.status_code} [url]: {self.response.url}')
                retry_time -= 1
                if retry_time <= 0:
                    resp = Response()
                    resp.status_code = 200
                    return self
                # self.log.info("retry %s second after" % retry_interval)
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


def get_ua(uatype: str = 'PC', browser: str = 'random'):
    """
        :param uatype: ua类型， 默认PC端
        :param browser: 浏览器类型，默认random随机, 可选['chrome', 'firefox']
        :return:
    """
    browser_list = ['chrome', 'firefox']
    if browser == 'random':
        browser = random.choice(browser_list)
    ua_lists = {
        'PC': {
            'chrome': [
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
                "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36",
                "Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36",
                "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
                "Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17",
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15",
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14"

            ],
            'firefox': [
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
                "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
                "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0",
                "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0",
                "Mozilla/5.0 (X11; OpenBSD amd64; rv:28.0) Gecko/20100101 Firefox/28.0",
                "Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0",
                "Mozilla/5.0 (Windows NT 6.1; rv:27.3) Gecko/20130101 Firefox/27.3",
                "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:27.0) Gecko/20121011 Firefox/27.0",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0",
                "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0",
                "Mozilla/5.0 (Windows NT 6.2; rv:22.0) Gecko/20130405 Firefox/23.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:23.0) Gecko/20131011 Firefox/23.0",
                "Mozilla/5.0 (Windows NT 6.2; rv:22.0) Gecko/20130405 Firefox/22.0",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0",
                "Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20130405 Firefox/22.0",
                "Mozilla/5.0 (Microsoft Windows NT 6.2.9200.0); rv:22.0) Gecko/20130405 Firefox/22.0",
                "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/21.0.1",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/21.0.1",
                "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:21.0.0) Gecko/20121011 Firefox/21.0.0",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0",
                "Mozilla/5.0 (X11; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20130514 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.2; rv:21.0) Gecko/20130326 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20130401 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20130331 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20130330 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130328 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130401 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130331 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20100101 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 5.0; rv:21.0) Gecko/20100101 Firefox/21.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0",
                "Mozilla/5.0 (Windows NT 6.2; Win64; x64;) Gecko/20100101 Firefox/20.0",
                "Mozilla/5.0 (Windows x86; rv:19.0) Gecko/20100101 Firefox/19.0",
                "Mozilla/5.0 (Windows NT 6.1; rv:6.0) Gecko/20100101 Firefox/19.0",
                "Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/18.0.1",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/20100101 Firefox/17.0.6"
            ]
        }
    }
    ua_list = ua_lists.get(uatype).get(browser)
    ua = random.choice(ua_list)
    return ua


if __name__ == '__main__':
    '请求方式:GET 返回:Json'
    # url = 'http://gxt.nmg.gov.cn/nmsearch/trssearch/searchAll.do?siteId=83&searchTag=all&allKeywords=%E4%B8%93%E7%B2%BE%E7%89%B9%E6%96%B0&fullKeywords=&orKeywords=&notKeywords=&sort=&position=0&organization=&pageNum=2&pageSize=10&zcYear=&isAlways=1&fileTag='
    # response = prequests().get(url=url).json
    # total = response.get('data').get('total')

    '请求方式:POST 返回:Json'
    # url = 'https://gxt.fujian.gov.cn/ssp/search/api/search'
    # data = 'siteType=1&mainSiteId=ff8080816e59baf3016e5e6b08903e8e&siteId=ff8080816e59baf3016e5e6b08903e8e&type=1&page=2&rows=10&historyId=8a289b0a865cc28a01865d037f20211e&sourceType=SSP_ZHSS&isChange=0&fullKey=N&wbServiceType=13&fileType=&fileNo=&pubOrg=&themeType=&searchTime=&startDate=&endDate=&sortFiled=RELEVANCE&searchFiled=&dirUseLevel=&issueYear=&issueMonth=&allKey=&fullWord=&oneKey=&notKey=&totalIssue=&chnlName=&zfgbTitle=&zfgbContent=&zfgbPubOrg=&zwgkPubDate=&zwgkDoctitle=&zwgkDoccontent=&zhPubOrg=1&keyWord=%E5%9B%9B%E5%A4%A7%E7%BB%8F%E6%B5%8E'
    # response = prequests().get(url=url, data=data, method='post', header={
    #     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}).json

    ''
    # item = {}
    # url = 'http://gxt.fujian.gov.cn/zwgk/xw/jxyw/202212/t20221219_6080943.htm'
    # response = prequests().get(url=url, data={1: 1}).tree
    # title = response.xpath(
    #     "//div[@class='article_component']/div[@class='article_title_group']")  # 正常提取, 返回字符串
    # title = response.xpath(
    #     "//div[@class='article_component']/div[@class='article_title_group']", is_list=True)  # 正常提取, 返回列表
    # date = response.dpath(
    #     "//div[@class='trt-row']/div[@class='trt-col-15 trt-col-sm-24']")
    # content = response.xpath(
    #     "//div[@class='TRS_Editor']/div[@class='TRS_Editor']")
    # item['content'] = content
    # item['title'] = title
    # item['date'] = date
    # print(item)
