import asyncio
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import csv
import random
from constants import USER_AGENT
from util.html_utils import get_html_string



async def search_sitemap(page, url):
    query = f"site:{url} sitemap"
    # query = f"site:{url} filetype:xml sitemap"
    if 'google' not in page.url:
        await page.goto('https://www.google.com/')
        await page.wait_for_timeout(1000)
    if 'google' in page.url and 'search' not in page.url:
        await page.locator('textarea[aria-label="Search"]').clear()
        await page.locator('textarea[aria-label="Search"]').press_sequentially(query,delay=50)
        await page.locator('input[value="Google Search"]:visible').click()
    elif 'google' in page.url and 'search' in page.url:
        await page.locator('textarea[aria-label="Search"]').clear()
        await page.locator('textarea[aria-label="Search"]').press_sequentially(query,delay=50)
        await page.locator('button[aria-label="Search"]:visible').click()

    no_result_img = page.locator('div[jsname="N8SwGb"]')
    no_document_div = page.locator('div:has-text("Your search did not match any documents")').nth(0)
    search_tab = page.locator('div#search>div')

    while True:
        if await no_result_img.is_visible() or await no_document_div.is_visible():
            return []
        if await search_tab.is_visible():
            break
        await asyncio.sleep(1)

    first_result = page.locator('div#search span>a').nth(0)
    first_url = await first_result.get_attribute('href')
    return first_url

def check_sitemap_page(url):
    html_string = get_html_string(url)
    if not html_string:
        return []

    soup = BeautifulSoup(html_string, 'html.parser')
    links = soup.find_all('a', href=True)

    sitemap_links = [link['href'] for link in links if 'sitemap' in link['href'].lower() or 'site-index' in link['href'].lower()]
    sitemap_links = list(set(sitemap_links))
    return sitemap_links

def check_robots_txt(url):
    robots_url = f"{url}/robots.txt"
    html_string = get_html_string(robots_url)
    if not html_string:
        return []

    sitemaps = []
    for line in html_string.split('\n'):
        if 'sitemap' in line.lower():
            sitemaps.append(line.split(':', 1)[1].strip())
            return sitemaps

def check_Yoast_sitemap(url):

    sitemap_links = []
    sitemap_links.append(f"{url}/post-sitemap.xml")

    valid_sitemaps = []
    for sitemap in sitemap_links:
        html_string = get_html_string(sitemap)
        if html_string:
            valid_sitemaps.append(sitemap)
    return valid_sitemaps


async def main():
    sitemap_data = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        with open('CU_sites_List.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                url = f"https://{row[1]}"
                print(f"Searching sitemap for {url}...")

                # step1: check robots.txt
                sitemap_links = check_robots_txt(url)
                if not sitemap_links:
                    # step2: check links from homepage
                    sitemap_links = check_sitemap_page(url)
                    if not sitemap_links:
                        # step3: check Yoast sitemap
                        print(f"No sitemap found on homepage for {url}, trying Yoast sitemap...")
                        sitemap_links = check_Yoast_sitemap(url)
                        if not sitemap_links:
                            # step4: use Google search
                            print(f"No sitemap found on homepage for {url}, trying Google search...")
                            sitemap_link = await search_sitemap(page, url)
                            sitemap_links = [sitemap_link] if sitemap_link else []

                sitemap_data.append([url, sitemap_links])
                print(f"Sitemap link for {url}: {sitemap_links}")

        await browser.close()

    with open('target_site/sitemap_links.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['url', 'sitemap_link'])
        writer.writerows(sitemap_data)
        print("sitemap_links.csv file created successfully.")

asyncio.run(main())


