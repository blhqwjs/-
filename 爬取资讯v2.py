import re
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd

# 确保抓取的数据结构正确
data = {
    'Title': [],  # 存储页面标题
    'Full Link': [],  # 存储页面的完整链接
    'Image URL': []  # 存储图片链接
}


def scrape_page(url):
    """抓取每页的链接和标题"""
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

    td = soup.find_all('td', {'class': "list"})
    lis = td[0].find_all('td', {'class': "tit1"})

    for li in lis:
        link = li.find_all('a')[0].get("href")
        title = li.find_all('a')[0].get("title")

        link = re.sub(r"^\.\./", r"", link)  # 去除相对路径的 "../"
        full_link = 'https://news.hueb.edu.cn/' + link  # 完整链接

        print(f"Scraping details from: {full_link}")
        scrape_details(full_link, title)  # 抓取详细页面的内容

    next_page = soup.find('a', text='下页')
    if next_page:
        next_page_url = next_page.get('href')
        if next_page_url:
            return next_page_url
    return None


def scrape_details(detail_url, title):
    """抓取详细页面内的图片 URL 和标题"""
    response = urllib.request.urlopen(detail_url)
    content = response.read().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

    content_paragraphs = soup.find_all('div', {'class': "v_news_content"})
    images = []
    for paragraph in content_paragraphs:
        images.extend(paragraph.find_all('img'))

    # 确保每个页面都有标题和图片链接
    for img in images:
        img_url = img.get('src')  # 获取图片的 URL
        if not img_url.startswith('http'):
            img_url = 'https://news.hueb.edu.cn' + img_url

        # 将抓取的数据保存到 data 中
        data['Title'].append(title)
        data['Full Link'].append(detail_url)
        data['Image URL'].append(img_url)


def scrape_all_pages(start_url, start_num, max_pages):
    """递归抓取所有页面，限制最大页数"""
    next_url = start_url
    page_count = 0  # 初始化抓取的页数计数器

    while next_url and page_count < max_pages:
        nextUrl = scrape_page(next_url)
        if start_num == 1:
            next_url = 'https://news.hueb.edu.cn/' + nextUrl
        else:
            next_url = 'https://news.hueb.edu.cn/xywh/' + nextUrl

        start_num += 1
        page_count += 1  # 增加计数器

        print(f"Next page: {next_url}")
        print(f"Scraped {page_count} page(s) out of {max_pages}.")


def save_to_excel(filename):
    """将数据保存到 Excel 文件"""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")


# 起始页 URL
start_url = 'https://news.hueb.edu.cn/xywh.htm'
start_num = 1
max_pages = 3  # 设置要爬取的最大页数

scrape_all_pages(start_url, start_num, max_pages)

# 保存数据到 Excel 文件
save_to_excel('scraped_data.xlsx')
