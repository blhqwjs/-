import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

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

# 最大线程数
max_threads = 5
# 用于存储线程
executor = ThreadPoolExecutor(max_workers=max_threads)


def scrape_page(url):
    try:
        response = urllib.request.urlopen(url)
        content = response.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
        td = soup.find_all('td', {'class': "list"})
        lis = td[0].find_all('td', {'class': "tit1"})

        for li in lis:
            link = re.sub(r"^\.\./", r"", li.find_all('a')[0].get("href"))
            full_link = 'https://news.hueb.edu.cn/' + link
            title = li.find_all('a')[0].get("title")
            print(f"Scraping details from: {full_link}")
            scrape_details(full_link, title)

        next_page = soup.find('a', text='下页')
        if next_page:
            return next_page.get('href')
        return None
    except Exception as e:
        print(f"Error while scraping {url}: {e}")
        return None


def scrape_details(detail_url, title):
    global images, fullText, imgUrls
    fullText = ''
    imgUrls = ''

    try:
        response = urllib.request.urlopen(detail_url)
        content = response.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

        content_paragraphs = soup.find_all('div', {'class': "v_news_content"})
        time_element = soup.find_all('td', {'class': "timecount"})
        time = time_element[0].get_text(strip=True) if time_element else None
        time = extract_time(time)

        for paragraph in content_paragraphs:
            images = paragraph.find_all('img')
            fullText += paragraph.get_text() + " "

        for img in images:
            img_url = img.get('src')
            if not img_url.startswith('http'):
                img_url = 'https://news.hueb.edu.cn' + img_url
            imgUrls += img_url + ","

        data['title'].append(title)
        data['schoolUrl'].append(detail_url)
        data['content'].append(fullText)
        data['filePath'].append(imgUrls)
        data['publishTime'].append(time)
        data['type'].append(1 if "活动" in title else 0)

    except Exception as e:
        print(f"Error in scrape_details for {detail_url}: {e}")


def extract_time(date_string):
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_string)
    if match:
        return datetime.strptime(match.group(0), '%Y-%m-%d %H:%M:%S')
    return None


def scrape_all_pages_threaded(start_url, max_pages):
    next_url = start_url
    page_count = 0

    while next_url and page_count < max_pages:
        future = executor.submit(scrape_page, next_url)
        result = future.result()

        if result:
            next_url = 'https://news.hueb.edu.cn/xywh/' + result
        else:
            break

        page_count += 1
        print(f"Scraped page {page_count}")
        time.sleep(1)  # 控制请求频率


def save_to_excel(filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")


# 启动抓取
start_url = 'https://news.hueb.edu.cn/xywh.htm'
max_pages = 5  # 限制爬取的页数
scrape_all_pages_threaded(start_url, max_pages)
save_to_excel('scraped_data19.xlsx')
