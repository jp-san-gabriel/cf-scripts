import csv
from sys import argv
import re
from os.path import join, basename, isfile, isdir
from os import listdir
from time import time
from collections import defaultdict
from json import dumps

PATTERN = 'http[s]{,1}://(.*)/'
IP_PATTERN = '[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}'
URLS_HOME = '/home/jp/Documents/Programming/Java/spring/projects/ws-cybersecurity-audit/vapt-audit-files-loader/res/urls/'

urls = {}
# load urls
def load_urls(file_path: str, urls: dict):
    category = basename(file_path)
    for file in listdir(file_path):
        full_path = join(file_path, file)
        if isdir(full_path):
            load_urls(full_path, urls)
        else:
            with open(full_path, 'r') as text_file:
                for line in text_file:
                    urls[line.strip().lower()] = category
# t0 = time()
# print('Loading urls... ', end='', flush=True)
# load_urls(URLS_HOME, urls)
# print(f'completed in {round(time() - t0, 4)}')

# load domains
domains = defaultdict(int)
with open(argv[1], 'r') as file:
    reader = csv.reader(file)

    for row in reader:
        texts = re.findall(PATTERN, row[1])
        if texts:
            index = texts[0].find('/')
            text = texts[0]
            if index > -1:
                text = text[:index]
            if text.startswith('www.'):
                text = text[4:]
            # if re.match(IP_PATTERN, text):
            #     print(text)
            domains[text] += 1

    # print(domains)
# ctr = 0
# categories = defaultdict(int)
# for domain in domains:
#     cat = urls.get(domain, None)
#     if cat:
#         ctr += 1
#         print(f"{domain}:{domains[domain]} -> {cat}")
#         categories[cat] += 1
print(f"{len(domains)}")
# print(dumps(categories, indent=3))

domains = [(k, v) for k, v in domains.items()]
domains.sort(key=lambda i: i[1], reverse=True)

filename = basename(argv[1])
i = filename.rfind('.')
if len(filename) - i > 5:
    filename += '-top-sites.txt'
else:
    filename = filename[:i] + '-top-sites.txt'

with open(filename, 'w') as file:
    ctr = 0
    while ctr < 50:
        d, c = domains[ctr]
        file.write(f"{d}|{c}|\n")
        print(f"{d}|{c}|")
        ctr += 1
    print(ctr)
