import requests
from bs4 import BeautifulSoup
import csv
import random
import time
from constants import USER_AGENT, FAQ_KEYWORDS
from util.html_utils import get_html_string


# FAQ keywords
faq_keywords = FAQ_KEYWORDS


user_agents = USER_AGENT

def check_page_for_faq(url, keywords):
    html_string = get_html_string(url)
    if not html_string:
        return []

    soup = BeautifulSoup(html_string, 'html.parser')
    links = soup.find_all('a', href=True)

    faq_links = [link['href'] for link in links if any(keyword in link['href'].lower() for keyword in keywords)]
    faq_links = list(set(faq_links))
    return faq_links


def check_faq_page(url):
    return check_page_for_faq(url, faq_keywords)

def check_sitemap_for_faq(sitemap_url):
    return check_page_for_faq(sitemap_url, faq_keywords)


faq_data = []
with open('target_site/sitemap_links.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        url = row[0]
        sitemap_links = eval(row[1])
        faq_links = []

        if sitemap_links:
            # search faq url from sitemap page
            for sitemap_url in sitemap_links:
                if not sitemap_url.startswith('http'):
                    sitemap_url = url.rstrip('/') + '/' + sitemap_url.lstrip('/')
                faq_links.extend(check_sitemap_for_faq(sitemap_url))
        if not faq_links:
            # search faq url from homepage
            faq_links = check_faq_page(url)

        faq_data.append([url, faq_links])
        print(f"FAQ links for {url}: {faq_links}")
        time.sleep(random.uniform(1, 3))


with open('target_site/faq_links_list.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['url', 'faq_links'])
    writer.writerows(faq_data)
    print("faq_links_list.csv file created successfully.")