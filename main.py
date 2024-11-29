import os
import csv
from util.htmlParse import simplify_html, clean_html
from util.html_utils import get_html_string, build_block_tree

faq_links_file = 'faq_links_list.csv'
faq_links = []
faq_links_test = [('https://www.boulderdamcu.org/', ['How-Can-We-Help#Lost-Card', 'How-Can-We-Help#Apply-Online', 'How-Can-We-Help#Mobile-App', 'How-Can-We-Help#How-to-Join', 'Contact-Us', 'How-Can-We-Help'])]


with open(faq_links_file, 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for line in reader:
        url, links = line
        faq_links.append((url, eval(links)))


for url, links in faq_links:
    print(f"===================Processing {url}====================")
    for link in links:
        if isinstance(link, tuple):
            link = link[0]  # Extract the first element if link is a tuple
        full_url = link if link.startswith('http') else url + '/'+link
        html_string = get_html_string(full_url)
        html_string_clean = clean_html(html_string)
        # target_trees, html_string = build_block_tree(html_string_clean, max_node_words=50)

        if '//' in url:
            folder_name = url.split('//')[1].split('/')[0]
        else:
            folder_name = url.split('/')[0]
        file_name = link.split('/')[-1] or 'index'
        file_path = os.path.join('data', folder_name)

        os.makedirs(file_path, exist_ok=True)
        with open(os.path.join(file_path, f'{file_name}.html'), 'w') as f:
            f.write(html_string_clean)
