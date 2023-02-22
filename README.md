# Example Package
#在此文件内，可使用markdown撰写对包的详细介绍和说明，便于别人熟悉和使用，在此不再赘述
This is a simple example package. You can use
[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.
包名称: requestXpath
介绍: 继承requests, 增加xpath功能拓展, 请求携带随机请求头, 请求访问失败默认重试3次间隔1s
使用方式: 
# from requestXpath import requests
# 
# response = requests.get(url='http://www.runoob.com/python3/python3-tutorial.html')
# print(response)  # 返回response对象
# print(response.status_code)  # 返回response状态码
# # print(response.text)  # 返回response源码
# # print(response.json)  # 返回response Json
# item = {}
# TreeItem = response.tree  # 实例化tree
# title = TreeItem.xpath("//div[@id='content']/h1")  # xpath提取(默认.//text() 支持/@href)
# filter_title = TreeItem.xpath("//div[@id='content']/h1|//div[@id='content']/h2", filter="div[@id='content']/h2")  # xpath提取, 过滤器,开头不需要//
# re_title = TreeItem.xpath("//div[@id='content']/h1", rule='Python 3(.*)')  # xpath提取, 支持正则
# titleXpathObj = TreeItem.xxpath("//div[@id='content']/h1/text()")  # 原生xpath提取
# link = TreeItem.xpath("//div[@id='leftcolumn']/a/@href", is_list=True)  # xpath提取(默认.//text() 支持/@href, is_list:True返回列表)
# item['标题'], item['正则标题'], item['链接'], item['titleXpathObj'], item['filter_title'] = title, re_title, link, titleXpathObj, filter_title
# print(item)

