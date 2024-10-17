import urllib.request

from bs4 import BeautifulSoup


def scrape_page(url):
    # 读取给定 url 的 html 代码
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')

    # 转换读取到的 html 文档
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

    # 获取表格的内容
    td = soup.find_all('td', {'class': "list"})
    lis = td[0].find_all('td', {'class': "tit1"})

    # 遍历获取到的 lis 列表，并从中抓取链接和标题
    for li in lis:
        print(li.find_all('a')[0].get("href"))
        print(li.find_all('a')[0].get("title"))

    # 查找下一页的链接
    next_page = soup.find('a', text='下页')  # 假设下一页的按钮文字是 "下一页"
    if next_page:
        next_page_url = next_page.get('href')
        if next_page_url:
            return next_page_url
    return None


# 起始页 URL，对应的url替换，递归实现查询
def scrape_all_pages(start_url, start_num):
    next_url = start_url

    while next_url:
        nextUrl = scrape_page(next_url)
        if start_num == 1:
            # 首页时获取到的下一页标识：
            next_url = 'https://news.hueb.edu.cn/' + nextUrl
        else:
            next_url = 'https://news.hueb.edu.cn/xywh/' + nextUrl

        start_num += 1

        print(next_url)


# 起始页 URL
start_url = 'https://news.hueb.edu.cn/xywh.htm'
start_num = 1
scrape_all_pages(start_url, start_num)