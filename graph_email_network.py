import csv
from sys import argv
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from json import dumps

emails = defaultdict(lambda: defaultdict(int))
with open(argv[1], 'r') as file:
    reader = csv.reader(file)
    for i, row in enumerate(reader):
        if i == 0:
            continue

        sender = row[1].strip().lower()
        receivers = row[2].strip().lower()
        if receivers:
            receivers = [r.lower().strip() for r in receivers.split(';') if r.strip()]
            for receiver in receivers:
                emails[sender][receiver] += 1
                emails[receiver][sender] += 1

print(dumps(emails, indent=3))

names = set()
g = Network('100%', '100%') #nx.Graph()
for sender, receivers in emails.items():
    for receiver, weight in receivers.items():
        names.add(sender)
        if sender in ['shepherd, denise', 'gegg, emily']:
            g.add_node(sender, label=sender, color='green')
        elif 'escada' in sender:
            g.add_node(sender, label=receiver, color='orange')
        elif '@' in sender:
            g.add_node(sender, label=receiver, color='gray')
        else:
            g.add_node(sender, label=sender)
        if receiver not in names:
            if receiver in ['shepherd, denise', 'gegg, emily']:
                g.add_node(receiver, label=receiver, color='green')
            elif 'escada' in receiver:
                g.add_node(receiver, label=receiver, color='orange')
            elif '@' in receiver:
                g.add_node(receiver, label=receiver, color='gray')
            else:
                g.add_node(receiver, label=receiver)
            g.add_edge(sender, receiver, value=weight)

# nx.draw(g, with_labels=True, node_size=100, linewidths=10)
# plt.show()
g.show('network.html')
