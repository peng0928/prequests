from urllib.parse import urljoin
import re, time, logging
from lxml import etree


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
                                obj = obj
                    else:
                        getrule = re.findall(rule, obj)
                        obj = getrule[0] if getrule else obj
            return obj
        except Exception as e:
            logging.error(e)
            return None

    def xxpath(self, x=None):
        return self.res.xpath(x)

    def dpath(self, x=None, rule=None):
        x = x.split('|')
        x = [i + '//text()' if '/@' not in i else i for i in x]
        x = '|'.join(x)

        obj = self.res.xpath(x)
        obj = [i.replace('\n', '').strip() for i in obj]
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
            patten = r'(\d{1,4}[-|/|.|年]\d{1,2}[-|/|.|月]\d{1,2}[-|/|.|日]*)[\s]*([\d{1,2}]*[:|时]*[\d{1,2}]*[:分]*[\d{1,2}]*[秒]*)'
            result = re.findall(patten, data)
            if not result:
                if rule != None:
                    patten = '.*?%s.*?(\d{1,4}[-|/|.|年]\d{1,2}[-|/|.|月]\d{1,2}[-|/|.|日]*)[\s]*([\d{1,2}]*[:|时]*[\d{1,2}]*[:分]*[\d{1,2}]*[秒]*)' % rule
                    result = re.findall(patten, data)

            result = ' '.join(result[0]).replace('.', '-').replace('/', '-').replace('年', '-').replace('月',
                                                                                                        '-').replace(
                '日', '').strip()
            result = result if result else None
            return result

    def replace(self, str):
        result = re.sub(r'(\\u[a-zA-Z0-9]{4})', lambda x: x.group(
            1).encode("utf-8").decode("unicode-escape"), str)
        result = re.sub(r'(\\r|\\n|\\t|\xa0)', lambda x: '', result)
        return result.strip()

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
