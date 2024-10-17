import re
import urllib.request
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup

# 存储抓取的数据
data = {
    'title': [],  # 存储页面标题
    'schoolUrl': [],  # 存储页面的完整链接
    'content': [],  # 存储页面的完整链接
    'publishTime': [],  # 存储页面的完整链接
    'filePath': [],  # 存储图片链接
    'type': []  # 存储资讯类型 如果文字里出现活动，会进行分类==》要不要加识别判断
}


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
        print(li.find_all('a')[0].get("title"))
        # 存储获得的数据
        link = li.find_all('a')[0].get("href")
        title = li.find_all('a')[0].get("title")
        # 首页是：info/1014/15340.htm样式，
        # 部分内容存在：../info/1014/15340.htm样式的
        link = re.sub(r"^\.\./", r"", link)
        # 正则表达式 r"^\.\./", "/" 将路径前面出现的 "../" 替换为""，即全消除
        full_link = 'https://news.hueb.edu.cn/' + link  # 完整链接
        print(f"Scraping details from: {full_link}")
        scrape_details(full_link, title)  # 访问具体页面并抓取详细内容

    # 查找下一页的链接
    next_page = soup.find('a', text='下页')  # 假设下一页的按钮文字是 "下一页"
    if next_page:
        next_page_url = next_page.get('href')
        if next_page_url:
            return next_page_url
    return None


# """抓取具体页面内的详细信息"""
# def scrape_details(detail_url, title):
#     # """抓取具体页面内的详细信息"""
#     global images, fullText, imgUrls
#     fullText = ''
#     imgUrls = ''
#     response = urllib.request.urlopen(detail_url)
#     content = response.read().decode('utf-8')
#     soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
#
#     # 假设具体页面的标题和正文在如下标签中
#     # title = soup.find('h1').get_text()  # 页面标题（根据具体页面结构调整）
#     # content_paragraphs = soup.find_all('p')  # 具体页面的内容
#     content_paragraphs = soup.find_all('div', {'class': "v_news_content"})
#     # 注意find_all获取到的数据格式为列表形式的，如果需要获取字符串，需要进行格式转换
#     time_element = soup.find_all('td', {'class': "timecount"})
#     time = time_element[0].get_text(strip=True) if time_element else None
#     time = extract_time(time)
#     # 输出详细内容
#     # print(f"title: {title}")
#     # print("Content:未格式化",content_paragraphs) 对数据进行格式化
#     # print("=========================获取到的格式化数据:=========================")
#     for paragraph in content_paragraphs:
#         images = paragraph.find_all('img')
#         # print(paragraph.get_text())
#         fullText = fullText + paragraph.get_text() + " "
#     # print("获取到的所有文章内容：", fullText)
#
#     # print(images)
#     # print("=========================获取到的格式化数据，完结==============================")
#
#     # print("=========================获取到的格式化图片url集合:")
#     for img in images:
#         # print(img)
#         # img_url = img.get('orisrc')  # 获取图片的 URL，河北经贸大学用的orisrc或src标识符，有两个
#         img_url = img.get('src')  # 获取图片的 URL，河北经贸大学用的orisrc或src标识符，有两个
#         # 如果 img_url 是相对路径，则拼接域名
#         if not img_url.startswith('http'):
#             img_url = 'https://news.hueb.edu.cn' + img_url
#             imgUrls = imgUrls + img_url + ","
#     # print("图片格式化地址：", imgUrls)
#     # 将抓取的数据保存到 data 中
#     data['title'].append(title)
#     data['schoolUrl'].append(detail_url)
#     data['content'].append(fullText)
#     data['filePath'].append(imgUrls)
#     data['publishTime'].append(time)
#     # 判断是否包含 "活动" 关键词，并分类为 1 或 0
#     if "活动" in title:
#         news_type = 1
#     else:
#         news_type = 0
#     data['type'].append(news_type)
#     # print("=========================获取到的格式化图片url，完结==============================")

def scrape_details(detail_url, title):
    global images, fullText, imgUrls
    fullText = ''
    imgUrls = ''

    try:
        # 尝试请求详情页面
        response = urllib.request.urlopen(detail_url)
    except urllib.error.HTTPError as e:
        # 如果返回HTTP错误，例如404
        print(f"HTTP Error {e.code}: {e.reason} for URL: {detail_url}")
        return  # 跳过当前详情页面
    except urllib.error.URLError as e:
        # 如果URL无效或其他网络问题
        print(f"URL Error: {e.reason} for URL: {detail_url}")
        return  # 跳过当前详情页面

    content = response.read().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

    content_paragraphs = soup.find_all('div', {'class': "v_news_content"})
    time_element = soup.find_all('td', {'class': "timecount"})
    time = time_element[0].get_text(strip=True) if time_element else None
    time = extract_time(time)

    for paragraph in content_paragraphs:
        images = paragraph.find_all('img')
        fullText = fullText + paragraph.get_text() + " "

    for img in images:
        img_url = img.get('src')
        if not img_url.startswith('http'):
            img_url = 'https://news.hueb.edu.cn' + img_url
            imgUrls = imgUrls + img_url + ","

    data['title'].append(title)
    data['schoolUrl'].append(detail_url)
    data['content'].append(fullText)
    data['filePath'].append(imgUrls)
    data['publishTime'].append(time)

    if "活动" in title:
        news_type = 1
    else:
        news_type = 0
    data['type'].append(news_type)

# 起始页 URL，对应的url替换，递归实现查询
def scrape_all_pages(start_url, start_num, max_pages):
    next_url = start_url
    page_count = 0  # 初始化抓取的页数计数器
    while next_url and page_count < max_pages:
        nextUrl = scrape_page(next_url)
        if start_num == 1:
            # 首页时获取到的下一页标识：带有：xywh标识，后续页没有
            next_url = 'https://news.hueb.edu.cn/' + nextUrl
        else:
            next_url = 'https://news.hueb.edu.cn/xywh/' + nextUrl

        start_num += 1
        page_count += 1

        # print("=========================下一页单纯地址不带url：", next_url, "=========================")
        print(f"Scraped page {page_count}")


# 处理文件保存的函数
def save_to_excel(filename):
    """将数据保存到 Excel 文件"""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")


# 添加时间格式转换：
def extract_time(date_string):
    # 使用正则表达式提取日期和时间部分
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_string)
    if match:
        time_string = match.group(0)
        # 将提取到的字符串转换为时间格式
        time_format = datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
        return time_format
    else:
        return None


# 起始页 URL
start_url = 'https://news.hueb.edu.cn/xywh.htm'
start_num = 1
max_pages = 264  # 限制爬取的页数
scrape_all_pages(start_url, start_num, max_pages)
save_to_excel('scraped_data.xlsx')
