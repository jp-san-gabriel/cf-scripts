from datetime import datetime, timedelta
from time import time
from sys import argv
from pytz import UTC
from collections import defaultdict
from math import ceil, log
import matplotlib.pyplot as plt
from os import mkdir
from os.path import exists, join, basename

X_RES = 120

# load the dir and extensions categories
EXTENSIONS = {}
with open('extensions.txt', 'r') as file:
    for line in file:
        line = line.split(' ')
        EXTENSIONS[line[0].strip()] = line[1].strip()

def create_path_list(grouped_lines: dict, date_index: int, mac: str, category: str, base_dir: str):
    # convert to list of tuples to enable sorting
    grouped_lines = [(k, v) for k, v in grouped_lines.items()]
    grouped_lines.sort(key=lambda i: len(i[1]), reverse=True)

    # write to file
    with open(join(base_dir, f"{category}-{mac}-file-list.txt"), 'w') as file:
        for cat, lines in grouped_lines:
            file.write(f"{cat} - {mac} ({len(lines)}):\n")
            lines.sort(key=lambda i: i[date_index])
            for i, line in enumerate(lines, 1):
                file.write(f"{i: >10} | {line[date_index]} | {line[16]}\n")
            file.write('\n')


def make_year_graph(lines: list, date_index: int, cat_index: int, start: int, end: int, tz,
                    mac: str, category: str, base_dir):

    print(f'Creating graph for {category} of files {mac} from {start} to {end}')
    # create x data
    x_data = []
    start_date = datetime(start, 1, 1, 0, 0, 0, tzinfo=tz)
    end_date = datetime(end + 1, 1, 1, tzinfo=tz)
    diff_in_seconds = end_date.timestamp() - start_date.timestamp()
    increment = diff_in_seconds / (X_RES)
    for i in range(X_RES):
        x_data.append(datetime.fromtimestamp(start_date.timestamp() + (increment * i), tz=tz))

    # create y data
    y_data = defaultdict(lambda: [0] * X_RES)
    grouped_lines = defaultdict(list) # Used to create the text file containing the file paths grouped by category
    for line in lines:
        y_data[line[cat_index]][int((line[date_index].timestamp() - start_date.timestamp()) // increment)] += 1
        grouped_lines[line[cat_index]].append(line)

    plt.title(f'{category} of files {mac} from {start} to {end}')
    plt.ylabel(f'Natural logarithm of 1+count')
    plt.xlabel(f'Date', fontsize=8)
    plt.xticks(rotation=45)

    labels = []
    for k, v in y_data.items():
        plt.plot(x_data, [log(1 + i) for i in v], label=k)
        labels.append(k)

    if len(labels) > 5:
        plt.legend(labels, loc='upper left', prop={'size': 7}, bbox_to_anchor=(1.02, 1.05))
    else:
        plt.legend(labels, prop={'size': 7})
    plt.savefig(join(base_dir, f'{category.lower()}-{mac.lower()}-{start}-{end}'), bbox_inches='tight')
    plt.close()

    create_path_list(grouped_lines, date_index, mac, category, base_dir)

def make_minute_graph(lines: list, date_index: int, cat_index: int, start: int, end: int, tz,
                    mac: str, category: str, base_dir):

    print(f'Creating graph for {category} of files {mac} from hours {start} to {end}')
    # create x data
    x_data = []
    start_sec = 60 * start
    end_sec = 60 * (end + 1)
    diff_in_secs = end_sec - start_sec
    increment = diff_in_secs / (X_RES)

    for i in range(X_RES):
        x_data.append(start + round((i * increment) / 60, 4))


    # create y data
    SECS_IN_HOUR = 3600
    y_data = defaultdict(lambda: [0] * X_RES)
    grouped_lines = defaultdict(list)
    for line in lines:
        index = int(((line[date_index].timestamp() % SECS_IN_HOUR) - start_sec) // increment)
        y_data[line[cat_index]][index] += 1
        grouped_lines[line[cat_index]].append(line)

    plt.title(f'{category} of files {mac} from minutes {start} to {end + 1}')
    plt.ylabel(f'Natural logarithm of 1+count')
    plt.xlabel(f'Minutes')

    labels = []
    for k, v in y_data.items():
        plt.plot(x_data, [log(1 + i) for i in v], label=k)
        labels.append(k)

    if len(labels) > 5:
        plt.legend(labels, loc='upper left', prop={'size': 7}, bbox_to_anchor=(1.02, 1.05))
    else:
        plt.legend(labels, prop={'size': 7})
    plt.savefig(join(base_dir, f'{category.lower()}-{mac.lower()}-mins-{start}-{end}'), bbox_inches='tight')
    plt.close()

    create_path_list(grouped_lines, date_index, mac, category, base_dir)

def make_hour_graph(lines: list, date_index: int, cat_index: int, start: int, end: int, tz,
                    mac: str, category: str, base_dir):

    print(f'Creating graph for {category} of files {mac} from hours {start} to {end}')
    # create x data
    x_data = []
    start_sec = 3600 * start
    end_sec = 3600 * (end + 1)
    diff_in_secs = end_sec - start_sec
    increment = diff_in_secs / (X_RES)

    for i in range(X_RES):
        x_data.append(start + round((i * increment) / 3600, 4))


    # create y data
    DAY_IN_SECS = 24 * 3600
    y_data = defaultdict(lambda: [0] * X_RES)
    grouped_lines = defaultdict(list)
    for line in lines:
        index = int(((line[date_index].timestamp() % DAY_IN_SECS) - start_sec) // increment)
        y_data[line[cat_index]][index] += 1
        grouped_lines[line[cat_index]].append(line)

    plt.title(f'{category} of files {mac} from hours {start} to {end}')
    plt.ylabel(f'Natural logarithm of 1+count')
    plt.xlabel(f'Hours')

    labels = []
    for k, v in y_data.items():
        plt.plot(x_data, [log(1 + i) for i in v], label=k)
        labels.append(k)

    if len(labels) > 5:
        plt.legend(labels, loc='upper left', prop={'size': 7}, bbox_to_anchor=(1.02, 1.05))
    else:
        plt.legend(labels, prop={'size': 7})
    plt.savefig(join(base_dir, f'{category.lower()}-{mac.lower()}-hours-{start}-{end}'), bbox_inches='tight')
    plt.close()

    create_path_list(grouped_lines, date_index, mac, category, base_dir)

def make_week_graph(lines: list, date_index: int, cat_index: int, start: int, end: int, tz,
                    mac: str, category: str, base_dir):

    print(f'Creating graph for {category} of files {mac} from week days {start} to {end}')
    # create x data
    x_data = []
    start_sec = 3600 * 24 * start
    end_sec = 3600 * 24 * (end + 1)
    diff_in_secs = end_sec - start_sec
    increment = diff_in_secs / (X_RES)

    for i in range(X_RES):
        # x_data.append(start + round((i * increment) / (3600 * 24), 4))
        x_data.append(round((start_sec + (i * increment)) / (3600 * 24), 4))


    # create y data
    # WEEK_IN_SECS = 24 * 3600 * 7
    y_data = defaultdict(lambda: [0] * X_RES)
    grouped_lines = defaultdict(list)
    for line in lines:
        # index = int(((line[date_index].timestamp() % WEEK_IN_SECS) - start_sec) // increment)
        d = line[date_index]
        index = int(((d.weekday() * 3600 * 24) + (d.hour * 3600) + (d.minute * 60) + round(d.second) - start_sec) // increment)
        y_data[line[cat_index]][index] += 1
        grouped_lines[line[cat_index]].append(line)

    if start == end:
        plt.title(f'{category} of files {mac} on week day {start}')
    else:
        plt.title(f'{category} of files {mac} from week days {start} to {end}')
    plt.ylabel(f'Natural logarithm of 1+count')
    plt.xlabel(f'Week Day')

    labels = []
    for k, v in y_data.items():
        plt.plot(x_data, [log(1 + i) for i in v], label=k)
        labels.append(k)

    if len(labels) > 5:
        plt.legend(labels, loc='upper left', prop={'size': 7}, bbox_to_anchor=(1.02, 1.05))
    else:
        plt.legend(labels, prop={'size': 7})
    plt.savefig(join(base_dir, f'{category.lower()}-{mac.lower()}-week-days-{start}-{end}'), bbox_inches='tight')
    plt.close()

    create_path_list(grouped_lines, date_index, mac, category, base_dir)

def year_filter(lines: list, start: int, end: int, tz, base_dir: str):
    mlines = []
    alines = []
    clines = []
    for line in lines:
        if line[13].year >= start and line[13].year <= end:
            clines.append(line)
        if line[14].year >= start and line[14].year <= end:
            mlines.append(line)
        if line[15].year >= start and line[15].year <= end:
            alines.append(line)

    for lines, date_index, date_type in zip([clines, mlines, alines], [13, 14, 15], ['created', 'modified', 'accessed']):
        for cat_index, cat_type in zip([7, 8, 6], ['Topdirs', 'Botdirs', 'Extensions']):
            make_year_graph(lines, date_index, cat_index, start, end, tz, date_type, cat_type, base_dir)

def hour_of_day_filter(lines: list, start: int, end: int, tz, base_dir):
    mlines = []
    alines = []
    clines = []

    DAY_IN_SECS = 3600 * 24
    start_sec = 3600 * start
    end_sec = 3600 * (end + 1)
    for line in lines:
        for d, l in zip(line[13:16], [clines, mlines, alines]):
            ts = d.timestamp()
            if ts % DAY_IN_SECS >= start_sec and ts % DAY_IN_SECS < end_sec:
                l.append(line)
    for lines, date_index, date_type in zip([clines, mlines, alines], [13, 14, 15], ['created', 'modified', 'accessed']):
        for cat_index, cat_type in zip([7, 8, 6], ['Topdirs', 'Botdirs', 'Extensions']):
            make_hour_graph(lines, date_index, cat_index, start, end, tz, date_type, cat_type, base_dir)

def minute_filter(lines: list, start: int, end: int, tz, base_dir: str):
    mlines = []
    alines = []
    clines = []

    SECS_IN_HOUR = 3600
    start_min = 60 * start
    end_min = 60 * (end + 1)
    for line in lines:
        for d, l in zip(line[13:16], [clines, mlines, alines]):
            ts = d.timestamp()
            if ts % SECS_IN_HOUR >= start_min and ts % SECS_IN_HOUR < end_min:
                l.append(line)

    for lines, date_index, date_type in zip([clines, mlines, alines], [13, 14, 15], ['created', 'modified', 'accessed']):
        for cat_index, cat_type in zip([7, 8, 6], ['Topdirs', 'Botdirs', 'Extensions']):
            make_minute_graph(lines, date_index, cat_index, start, end, tz, date_type, cat_type, base_dir)


def day_of_week_filter(lines: list, start: int, end: int, tz, base_dir: str):
    mlines = []
    alines = []
    clines = []

    # WEEK_IN_SECS = 3600 * 24 * 7
    # start_sec = 3600 * 24 * start
    # end_sec = 3600 * 24 * (end + 1)
    for line in lines:
        for d, l in zip(line[13:16], [clines, mlines, alines]):
            ts = d.timestamp()
            # if ts % WEEK_IN_SECS >= start_sec and ts % WEEK_IN_SECS < end_sec:
            if d.weekday() >= start and d.weekday() < end + 1:
                l.append(line)
    for lines, date_index, date_type in zip([clines, mlines, alines], [13, 14, 15], ['created', 'modified', 'accessed']):
        for cat_index, cat_type in zip([7, 8, 6], ['Topdirs', 'Botdirs', 'Extensions']):
            make_week_graph(lines, date_index, cat_index, start, end, tz, date_type, cat_type, base_dir)

filters = {
    'year': year_filter,
    'week': day_of_week_filter,
    'min': minute_filter,
    'hour': hour_of_day_filter,
}

def make_graphs(file_name: str, filter_type: str, start: str, end: str, tz: str=None):
    start = int(start)
    end = int(end)
    if tz:
        TIMEZONE = pytz.timezone(f"Etc/{tz}")
    else:
        TIMEZONE = UTC

    filter = filters[filter_type]

    # load lines of file
    lines = []
    with open(file_name, 'r') as file:
        for line in file:
            # convert dates to datetime objects and load the extension categories
            line = line.rstrip().split('|')
            if line[13] and line[14] and line[15]:
                line[13] = datetime.fromtimestamp(int(line[13])).astimezone(TIMEZONE)
                line[14] = datetime.fromtimestamp(int(line[14])).astimezone(TIMEZONE)
                line[15] = datetime.fromtimestamp(int(line[15])).astimezone(TIMEZONE)
                line[7] = EXTENSIONS.get(line[7], line[7])
                line[6] = EXTENSIONS.get(line[6], line[6])
                line[8] = EXTENSIONS.get(line[8], line[8])
                lines.append(line)

    # determine basedir
    type_desc = {
        'year': 'years',
        'week': 'week-days',
        'min': 'mins',
        'hour': 'hours'
    }
    base_dir = f"{basename(file_name).replace('.', '_')}-{type_desc[filter_type]}-{start}-{end}"
    if not exists(base_dir):
        mkdir(base_dir)

    # filter the creation times
    filter(lines, start, end, TIMEZONE, base_dir)

if __name__ == '__main__':
   make_graphs(*argv[1:])
