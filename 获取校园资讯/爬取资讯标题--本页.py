import urllib.request
from bs4 import BeautifulSoup
def scrape_page(url):
    # 读取给定 url 的 html 代码
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    # 转换读取到的 html 文档
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
    # 获取表格的内容
    # td = soup.find_all('td', {'class': "list"})
    # lis = td[0].find_all('td', {'class': "tit1"})
    lis = soup.find_all('td', {'class': "tit1"})
    print(f"获取到的数据: {lis}")
    # 遍历获取到的 lis 列表，并从中抓取链接和标题
    for li in lis:
        print(li.find_all('a')[0].get("title"))
# 起始页 URL
start_url = 'https://news.hueb.edu.cn/xywh.htm'
start_num = 1
scrape_page(start_url)