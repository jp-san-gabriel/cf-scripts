from csv import reader
import matplotlib.pyplot as plt
from collections import defaultdict
from sys import argv
from math import log
from os.path import basename
from whois import whois

domains = defaultdict(int)
with open(argv[1], 'r') as file:
    r = reader(file)
    for row in r:
        index = row[2].find('@')
        if index > -1:
            domains[row[2][index + 1:]] += 1

names = []
counts = []
for k, v in domains.items():
    w = whois(k)
    if w['domain_name']:
        print(f'domain: {k}, count: {v}')
    # if v > 1:
        names.append(k)
        counts.append(log(1 + v))

plt.title('Counts of Email addresses by Domain')
plt.barh(names, counts)
plt.yticks(fontsize=8)
plt.ylabel('Domain')
plt.xlabel('Natural logarithm of 1+count')
plt.grid(axis='y')
plt.tight_layout()

filename = basename(argv[1])
dot_index = filename.rfind('.')
if dot_index > -1 and len(filename) - dot_index <= 5:
    filename = filename[:dot_index].replace('.', '_') + '-domain-counts'
plt.savefig(filename)
