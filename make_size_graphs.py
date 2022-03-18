from datetime import datetime, timedelta
from time import time
from sys import argv
from pytz import UTC
from collections import defaultdict
from math import ceil, log, e
import matplotlib.pyplot as plt
from os import mkdir
from os.path import exists, join, basename

X_RES = 30

# load the dir and extensions categories
EXTENSIONS = {}
with open('extensions.txt', 'r') as file:
    for line in file:
        line = line.split(' ')
        EXTENSIONS[line[0].strip()] = line[1].strip()

def make_graph(category, x_data, y_data, min_size, max_size, base_dir):

    plt.title(f'Distribution of Files with size between log {min_size} to {max_size} to {category}')
    plt.ylabel(f'Natural logarithm of 1+count')
    plt.xlabel(f'Natural logarithm of 1+size in bytes')

    labels = []
    for k, v in y_data.items():
        plt.plot(x_data, [log(1 + i) for i in v])
        labels.append(k)

    plt.legend(labels, loc='upper left', prop={'size': 7}, bbox_to_anchor=(1.02, 1.05))
    plt.savefig(join(base_dir, f'{category}-of-files-sizes-{min_size}-{max_size}.png'), bbox_inches='tight')
    plt.close()

def create_path_list(grouped_lines, category, base_dir):
    grouped_lines = [(k, v) for k, v in grouped_lines.items()]
    grouped_lines.sort(key=lambda i: len(i[1]), reverse=True)

    with open(join(base_dir, f"{category}-file-list.txt"), "w") as file:
        for cat, lines in grouped_lines:
            file.write(f"{cat} ({len(lines)})\n")
            lines.sort(key=lambda i: i[16])
            for i, line in enumerate(lines, 1):
                file.write(f"{i: >10} | {line[9]:>12} | {line[16]}\n")
            file.write(f"{'-' * 80}\n")

def make_graphs(file_name: str, min_log, max_log):
    min_size = (e ** float(min_log)) - 1
    max_size = (e ** float(max_log)) - 1

    # create the basedir
    base_dir = f"{basename(file_name).replace('.', '_')}-file-sizes-{min_log}-{max_log}"
    if not exists(base_dir):
        mkdir(base_dir)

    # create the x-axis
    increment = (max_size - min_size) / X_RES
    x_data = []
    for i in range(X_RES):
        x_data.append(log(1 + round(min_size + (i * increment))))

    topdirs = defaultdict(lambda: [0] * X_RES)
    botdirs = defaultdict(lambda: [0] * X_RES)
    extensions = defaultdict(lambda: [0] * X_RES)

    topdir_lines = defaultdict(list)
    botdir_lines = defaultdict(list)
    extension_lines = defaultdict(list)

    lines = []
    with open(file_name, 'r') as file:
        for line in file:
            # convert size to int and load the extension categories
            line = line.rstrip().split('|')
            size = int(line[9])
            if size >= min_size and size <= max_size:
                line[7] = EXTENSIONS.get(line[7], line[7])
                line[6] = EXTENSIONS.get(line[6], line[6])
                line[8] = EXTENSIONS.get(line[8], line[8])
                line[9] = int(line[9])
                lines.append(line)
                topdirs[line[7]][int((line[9] - min_size) // increment)] += 1
                botdirs[line[8]][int((line[9] - min_size) // increment)] += 1
                extensions[line[6]][int((line[9] - min_size) // increment)] += 1

                topdir_lines[line[7]].append(line)
                botdir_lines[line[8]].append(line)
                extension_lines[line[6]].append(line)

    for y_data, category in zip([topdirs, botdirs, extensions], ['topdirs', 'botdirs', 'extensions']):
        make_graph(category, x_data, y_data, min_log, max_log, base_dir)

    for category, grouped_lines in [
        ('topdirs', topdir_lines),
        ('botdirs', botdir_lines),
        ('extensions', extension_lines)
    ]:
        create_path_list(grouped_lines, category, base_dir)


if __name__ == '__main__':
   make_graphs(*argv[1:])
