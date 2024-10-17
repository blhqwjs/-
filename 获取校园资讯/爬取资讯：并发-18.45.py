import asyncio
import re
import time
from datetime import datetime

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

# 存储抓取的数据
data = {
    'title': [],
    'schoolUrl': [],
    'content': [],
    'publishTime': [],
    'filePath': [],
    'type': []
}
# 存在很多问题，到3后自动没了

# 处理页面内容
async def fetch_page(session, url):
    try:
        async with session.get(url) as response:
            content = await response.text()
            return content
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


# 解析页面
async def scrape_page(session, url):
    content = await fetch_page(session, url)
    if content is None:
        return None

    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
    td = soup.find_all('td', {'class': "list"})
    if not td:
        return None

    lis = td[0].find_all('td', {'class': "tit1"})
    tasks = []
    for li in lis:
        link = li.find_all('a')[0].get("href")
        title = li.find_all('a')[0].get("title")
        link = re.sub(r"^\.\./", r"", link)
        full_link = 'https://news.hueb.edu.cn/' + link
        tasks.append(scrape_details(session, full_link, title))  # 传递 title

    await asyncio.gather(*tasks)

    next_page = soup.find('a', text='下页')
    if next_page:
        next_page_url = next_page.get('href')
        if next_page_url:
            next_page_url = 'https://news.hueb.edu.cn/' + next_page_url
            print(f"Next page URL: {next_page_url}")  # 打印调试信息
            return next_page_url
    else:
        print(f"No next page found on {url}")  # 打印调试信息
    return None


# 处理详情页内容
async def scrape_details(session, detail_url, title):
    content = await fetch_page(session, detail_url)
    if content is None:
        return

    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
    content_paragraphs = soup.find_all('div', {'class': "v_news_content"})
    time_element = soup.find_all('td', {'class': "timecount"})
    time = time_element[0].get_text(strip=True) if time_element else None
    time = extract_time(time)

    full_text = ''  # 使用局部变量
    img_urls = ''  # 使用局部变量

    for paragraph in content_paragraphs:
        images = paragraph.find_all('img')
        full_text = full_text + paragraph.get_text() + " "

        for img in images:
            img_url = img.get('src')
            if not img_url.startswith('http'):
                img_url = 'https://news.hueb.edu.cn' + img_url
            img_urls = img_urls + img_url + ","

    # 保存到全局数据结构中
    data['title'].append(title)
    data['schoolUrl'].append(detail_url)
    data['content'].append(full_text)
    data['filePath'].append(img_urls)
    data['publishTime'].append(time)

    # 分类内容
    news_type = 1 if "活动" in title else 0
    data['type'].append(news_type)


# 时间格式转换
def extract_time(date_string):
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_string)
    if match:
        time_string = match.group(0)
        time_format = datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
        return time_format
    else:
        return None


# 异步爬取所有页面
async def scrape_all_pages(start_url, max_pages):
    next_url = start_url
    page_count = 0

    async with aiohttp.ClientSession() as session:
        while next_url and page_count < max_pages:
            next_url = await scrape_page(session, next_url)
            page_count += 1
            print(f"Scraped page {page_count}")
            # 增加延迟，避免触发反爬虫机制
            time.sleep(0.5)  # 1秒延迟，可以根据需要调整


# 保存数据到 Excel
def save_to_excel(filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")


# 起始页 URL
start_url = 'https://news.hueb.edu.cn/xywh.htm'
max_pages = 256  # 限制爬取的页数

# 启动异步任务
asyncio.run(scrape_all_pages(start_url, max_pages))
save_to_excel('scraped_data_async3.xlsx')
