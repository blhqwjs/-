import re
import urllib.request
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

# 用于存储抓取到的新闻数据
data = {
    'title': [],  # 存储新闻标题
    'schoolUrl': [],  # 存储新闻页面的完整链接
    'content': [],  # 存储新闻页面的详细内容
    'publishTime': [],  # 存储新闻的发布时间
    'filePath': [],  # 存储图片链接
    'type': []  # 存储资讯类型（0为普通资讯，1为活动类资讯）
}


# 从给定的URL中抓取页面内容
def scrape_page(url):
    # 读取给定 url 的 html 代码
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')

    # 使用BeautifulSoup解析html文档
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

    # 获取包含标题的表格内容
    lis = soup.find_all('td', {'class': "tit1"})

    # 遍历列表，抓取链接和标题
    for li in lis:
        # 抓取链接和标题
        link = li.find_all('a')[0].get("href")
        title = li.find_all('a')[0].get("title")

        # 处理链接，消除前面的相对路径符号
        link = re.sub(r"^\.\./", r"", link)
        full_link = 'https://news.hueb.edu.cn/' + link  # 构造完整链接

        # 打印并抓取详细内容
        print(f"Scraping details from: {full_link}")
        scrape_details(full_link, title)  # 访问具体页面并抓取详细内容

    # 查找并返回下一页的链接
    next_page = soup.find('a', text='下页')  # 下一页的按钮文字是"下页"
    if next_page:
        next_page_url = next_page.get('href')
        if next_page_url:
            return next_page_url
    return None


# 访问详细页面并抓取具体内容
def scrape_details(detail_url, title):
    global images, fullText, imgUrls
    fullText = ''
    imgUrls = ''
    try:
        # 请求详情页面内容
        response = urllib.request.urlopen(detail_url)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} for URL: {detail_url}")
        return  # 如果请求失败，跳过该页面
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason} for URL: {detail_url}")
        return  # 跳过无效URL

    # 解析页面内容
    content = response.read().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

    # 获取页面中的正文和发布时间
    content_paragraphs = soup.find_all('div', {'class': "v_news_content"})
    time_element = soup.find_all('td', {'class': "timecount"})
    time = time_element[0].get_text(strip=True) if time_element else None
    time = extract_time(time)  # 转换发布时间为标准格式

    # 获取正文中的文字内容
    for paragraph in content_paragraphs:
        images = paragraph.find_all('img')  # 查找图片
        fullText += paragraph.get_text() + " "  # 拼接所有段落内容

    # 处理图片链接
    for img in images:
        img_url = img.get('src')
        if not img_url.startswith('http'):
            img_url = 'https://news.hueb.edu.cn' + img_url  # 拼接完整图片链接
        imgUrls += img_url + ","  # 多个图片用逗号分隔

    # 将抓取到的数据存储到data字典中
    data['title'].append(title)
    data['schoolUrl'].append(detail_url)
    data['content'].append(fullText)
    data['filePath'].append(imgUrls)
    data['publishTime'].append(time)

    # 判断是否为活动类资讯
    news_type = 1 if "活动" in title else 0
    data['type'].append(news_type)


# 递归抓取多页数据
def scrape_all_pages(start_url, start_num, max_pages):
    next_url = start_url
    page_count = 0  # 用于记录当前抓取的页数

    while next_url and page_count < max_pages:
        nextUrl = scrape_page(next_url)
        if start_num == 1:
            # 首页的下一页链接格式不同，需要处理
            next_url = 'https://news.hueb.edu.cn/' + nextUrl
        else:
            next_url = 'https://news.hueb.edu.cn/xywh/' + nextUrl

        start_num += 1
        page_count += 1
        print(f"Scraped page {page_count}")


# 将抓取的数据保存为Excel文件
def save_to_excel(filename):
    """将数据保存到 Excel 文件"""
    df = pd.DataFrame(data)  # 使用 pandas 将数据转换为 DataFrame
    df.to_excel(filename, index=False)  # 保存为Excel文件
    print(f"Data saved to {filename}")


# 将时间字符串提取并转换为标准格式
def extract_time(date_string):
    # 使用正则表达式提取日期和时间
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_string)
    if match:
        time_string = match.group(0)
        # 将字符串转换为datetime对象
        time_format = datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
        return time_format
    else:
        return None


# 设置起始页 URL 和最大抓取页数
start_url = 'https://news.hueb.edu.cn/xywh.htm'
start_num = 1
max_pages = 260  # 限制最多抓取260页
scrape_all_pages(start_url, start_num, max_pages)
save_to_excel('scraped_data.xlsx')  # 保存结果为 Excel 文件
