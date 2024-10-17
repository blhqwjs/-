# 获取单独的一页
# import urllib.request
# from bs4 import BeautifulSoup
#
# # 读取给定 url 的 html 代码
# response = urllib.request.urlopen('https://news.hueb.edu.cn/xywh.htm')
# content = response.read().decode('utf-8')
#
# # 转换读取到的 html 文档
# soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
# # 获取转换后的 html 文档里属性 class=list-main-warp 的 div 标签的内容
# # 必须找到对应的数据的顶部文件所用标签，指定class，
# td = soup.find_all('td', {'class': "list"})
# # 从已获取的 div 标签的内容里获取 li 标签的内容
# # lis = divs[0].find_all('td')
# # 遍历获取到的 lis 列表，并从中抓取链接和标题
# lis = td[0].find_all('td',{'class': "tit1"})
# # 遍历获取到的 lis 列表，并从中抓取链接和标题
# for li in lis:
#     print(li.find_all('a')[0].get("href"))
#     print(li.find_all('a')[0].get("title"))
#
#
import re
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
        print("", li.find_all('a')[0].get("href"))
        # 首页是：info/1014/15340.htm样式，
        # 部分内容存在：../info/1014/15340.htm样式的
        print(li.find_all('a')[0].get("title"))

        link = li.find_all('a')[0].get("href")
        link = re.sub(r"^\.\./", r"", link)
        # 正则表达式 r"^\.\./", "/" 将路径前面出现的 "../" 替换为""，即全消除
        full_link = 'https://news.hueb.edu.cn/' + link  # 完整链接
        print(f"Scraping details from: {full_link}")
        scrape_details(full_link)  # 访问具体页面并抓取详细内容

    # 查找下一页的链接
    next_page = soup.find('a', text='下页')  # 假设下一页的按钮文字是 "下一页"
    if next_page:
        next_page_url = next_page.get('href')
        if next_page_url:
            return next_page_url
    return None


# """抓取具体页面内的详细信息"""
def scrape_details(detail_url):
    # """抓取具体页面内的详细信息"""
    global images
    response = urllib.request.urlopen(detail_url)
    content = response.read().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

    # 假设具体页面的标题和正文在如下标签中
    # title = soup.find('h1').get_text()  # 页面标题（根据具体页面结构调整）
    # content_paragraphs = soup.find_all('p')  # 具体页面的内容
    content_paragraphs = soup.find_all('div', {'class': "v_news_content"})

    # 输出详细内容
    # print(f"Title: {title}")
    # print("Content:未格式化",content_paragraphs) 对数据进行格式化
    print("=========================获取到的格式化数据:=========================")
    for paragraph in content_paragraphs:
        images = paragraph.find_all('img')
        print(paragraph.get_text())
        # print(images)
    print("=========================获取到的格式化数据，完结==============================")

    print("=========================获取到的格式化图片url集合:")
    for img in images:
        # print(img)
        # img_url = img.get('orisrc')  # 获取图片的 URL，河北经贸大学用的orisrc或src标识符，有两个
        img_url = img.get('src')  # 获取图片的 URL，河北经贸大学用的orisrc或src标识符，有两个
        # 如果 img_url 是相对路径，则拼接域名
        if not img_url.startswith('http'):
            img_url = 'https://news.hueb.edu.cn' + img_url
        print("图片格式化地址：", img_url)


print("=========================获取到的格式化图片url，完结==============================")


# 起始页 URL，对应的url替换，递归实现查询
def scrape_all_pages(start_url, start_num):
    next_url = start_url

    while next_url:
        nextUrl = scrape_page(next_url)
        if start_num == 1:
            # 首页时获取到的下一页标识：带有：xywh标识，后续页没有
            next_url = 'https://news.hueb.edu.cn/' + nextUrl
        else:
            next_url = 'https://news.hueb.edu.cn/xywh/' + nextUrl

        start_num += 1

        print("=========================下一页单纯地址不带url：", next_url, "=========================")


# 起始页 URL
start_url = 'https://news.hueb.edu.cn/xywh.htm'
start_num = 1
scrape_all_pages(start_url, start_num)
