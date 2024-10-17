import re
import urllib.request
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup

# 存储抓取的数据
data = {
    'alumniName': [],  # 存储校友名称
    'comeYear': [],  # 存储校友进学校时间
    'department': [],  # 存储校友毕业院系
    'participate_time': [],  # 存储捐款时间
    'id': [],  # 存储捐款编号:
    'feedback': [],  # 存储就是祝福语啥的，对应类型为：0
    'URL': []  # 存照片
}


def scrape_page(url):
    # 读取给定 url 的 html 代码
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')

    # 转换读取到的 html 文档
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

    # 获取表格的内容
    div = soup.find_all('div', {'class': "listBody"})   # 捐款者
    td = soup.find_all('td', {'class': "w50"})   # 捐款者
    lis = td[0].find_all('td', {'class': "tit1"})
    tr = td[0].find_all('td', {'class': "tit1"})

    # 遍历获取到的 lis 列表，并从中抓取链接和标题
    for li in td:
        print("", li.find_all('a')[0].get("href"))
        print(li.find_all('a')[0].get_text(strip=True))
        # 存储获得的数据
        link = li.find_all('a')[0].get("href")
        alumniName = li.find_all('a')[0].get_text(strip=True)
        # 首页是：info/1014/15340.htm样式，
        # 部分内容存在：../info/1014/15340.htm样式的
        link = re.sub(r"^\.\./", r"", link)
        # 正则表达式 r"^\.\./", "/" 将路径前面出现的 "../" 替换为""，即全消除
        full_link = 'https://alumni.hueb.edu.cn/' + link  # 完整链接
        print(f"Scraping details from: {full_link}")
        scrape_details(full_link, alumniName)  # 访问具体页面并抓取详细内容

    # 查找下一页的链接
    next_page = soup.find('a', text='下页')  # 假设下一页的按钮文字是 "下一页"
    if next_page:
        next_page_url = next_page.get('href')
        if next_page_url:
            return next_page_url
    return None


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
start_url = 'https://alumni.hueb.edu.cn/donationre/202302181'
start_num = 1
max_pages = 40  # 限制爬取的页数
scrape_all_pages(start_url, start_num, max_pages)
save_to_excel('捐款信息.xlsx')
