import xml.etree.ElementTree as et
from math import log, e
from sys import argv
from datetime import datetime, timedelta
from os.path import exists, isdir, join, basename
from os import mkdir
from time import time
import pytz
from collections import defaultdict
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt

# CONSTANTS - adjust as necessary
START_YEAR = 1995
END_YEAR = 2006
INODES_XRES = 120           # X resolution for inodes graph
ALL_TIME_USAGE_XRES = 113   # X resolution for all time usage graph
WEEKLY_USAGE_XRES = 113     # X resolution for weekly usage graph
DAY_USAGE_XRES = 113        # X resolution for day usage graph
HOUR_USAGE_XRES = 113       # X resolution for hour usage graph
SIZE_DISTRIBUTION_XRES = 113 # X resoultion for file size distribution graph

# check command line arguments
if len(argv) < 2 or not exists(argv[1]):
    print('Usage: plot.py <DFXML file> [<timezone>]')
    print('Defaults to UTC if timezone is not supplied.')
    exit()

# set timezone from command-line args if supplied
if len(argv) >= 3:
    TIMEZONE = pytz.timezone(f"Etc/{argv[2]}")
else:
    TIMEZONE = pytz.UTC

DTD = '{http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML}'
TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

# Parse the out file
t0 = time()
print(f'Loading {argv[1]}...', end=' ', flush=True)
with open(argv[1], 'r') as file:
    lines = file.readlines()
print(f'Completed in {round(time() - t0, 3)} seconds.')

# Get the drive name from file name
file_name = basename(argv[1])
if file_name.rfind('.') > 0:
    drive_name = file_name[:file_name.rfind('.')].replace('.', '_')
else:
    drive_name = file_name

print(f"drive_name: {drive_name}")
output_dir = drive_name + '-graphs'

# Create the output directory
if not isdir(output_dir) or not exists(output_dir):
    mkdir(output_dir)


# Retrieve necessary data from text file ----------------------------------------------------------
t0 = time()
print('Gathering data...', end=' ', flush=True)

inodes = []
mtimes = []
atimes = []
ctimes = []
depths = []
sizes = []
file_paths = []

for i, line in enumerate(lines):
    line = line.rstrip().split('|')

    inodes.append(int(line[12]))

    # add the mac times to the list
    if line[13] and line[14] and line[15] :
        mtimes.append(datetime.fromtimestamp(int(line[14])).astimezone(TIMEZONE))
        atimes.append(datetime.fromtimestamp(int(line[15])).astimezone(TIMEZONE))
        ctimes.append(datetime.fromtimestamp(int(line[13])).astimezone(TIMEZONE))

    # add the depth of file into the depths list
    filename = line[16]
    depths.append(len(filename.split('/')))

    # add the filename to file_paths
    file_paths.append(filename)

    # add the size of file into the sizes list
    if line[9]:
        sizes.append(int(line[9]))

print(f'Completed in {round(time() - t0, 3)} seconds.')

# plot the inodes graphs ------------------------------------------------------------------
t0 = time()
print('Generating inodes graph...', end=' ', flush=True)
max_inode = max(inodes)
DIVISOR = round(max_inode / INODES_XRES)
length = (max_inode // (DIVISOR - 1)) + 1
inode_counts = [0] * length


for inode in inodes:
    inode_counts[inode // DIVISOR] += 1

fig, ax = plt.subplots()
ax.set_title(drive_name)
ax.set_ylabel('Natural logarithm of 1+count')
ax.set_xlabel('Inode Number')
ax.plot([i * DIVISOR for i in range(len(inode_counts))], [log(1 + i, e) for i in inode_counts], linewidth=.75)

plt.savefig(join(output_dir, f'{drive_name}-inodes'))
plt.close()


# Create all time usage graph -------------------------------------------------------
t0 = time()
print('Generating all time usage graph...', end=' ', flush=True)

# plot the alltime usage
# min_date = min(mtimes) - timedelta(days=365)
min_date = datetime(START_YEAR, 1, 1).astimezone(TIMEZONE)
max_date = max(atimes) + timedelta(days=365)
# min_date = min(min(mtimes), min(atimes), min(ctimes)) - timedelta(days=365)
# max_date = max(max(mtimes), max(ctimes), max(atimes)) + timedelta(days=365)

# get the divisor
duration = max_date - min_date
DIVISOR = int(round(duration.total_seconds() / ALL_TIME_USAGE_XRES))
length = (int(duration.total_seconds()) // DIVISOR) + 1

ctime_counts = [0] * length
atime_counts = [0] * length
mtime_counts = [0] * length

all_times = zip(mtimes, atimes, ctimes)
for mtime, atime, ctime in all_times:
    index = int((mtime - min_date).total_seconds()) // DIVISOR
    if index < len(mtime_counts) and index >= 0:
        mtime_counts[index] += 1
    index = int((atime - min_date).total_seconds()) // DIVISOR
    if index < len(atime_counts) and index >= 0:
        atime_counts[index] += 1
    index = int((ctime - min_date).total_seconds()) // DIVISOR
    if index < len(ctime_counts) and index >= 0:
        ctime_counts[index] += 1

# Plot them all
fig, ax = plt.subplots()
ax.set_title(drive_name)
ax.set_ylabel('Natural logarithm of 1+count')
ax.set_xlabel('Year')

# create the x-axis
LINE_WIDTH = .75
x_data = [min_date + timedelta(seconds=i * DIVISOR) for i in range(length)]
y_data = [log(1 + count, e) for count in ctime_counts]
ax.plot(x_data, y_data, color="red", linewidth=LINE_WIDTH, label='creation')
y_data = [log(1 + count, e) for count in mtime_counts]
ax.plot(x_data, y_data, color="green", linewidth=LINE_WIDTH, label='modification')
y_data = [log(1 + count, e) for count in atime_counts]
ax.plot(x_data, y_data, color="blue", linewidth=LINE_WIDTH, label='access')

plt.legend()
plt.savefig(join(output_dir, f'{drive_name}-all-time'))
plt.close()

print(f'Completed in {round(time() - t0, 3)} seconds.')

# Create Weekly Usage graph ------------------------------------------------------
t0 = time()
print('Generating weekly usage graph...', end=' ', flush=True)

ctime_counts = [0] * WEEKLY_USAGE_XRES
atime_counts = [0] * WEEKLY_USAGE_XRES
mtime_counts = [0] * WEEKLY_USAGE_XRES

get_index = lambda _time: round((WEEKLY_USAGE_XRES - 1) * ((_time.weekday() + \
    (((_time.hour * 60 * 60) + (_time.minute * 60) + _time.second) / (60*60*24))) / 7))

for mtime, atime, ctime in zip(mtimes, atimes, ctimes):
    mtime_counts[get_index(mtime)] += 1
    atime_counts[get_index(atime)] += 1
    ctime_counts[get_index(ctime)] += 1

# Create x_axis
x_data = [(7 / WEEKLY_USAGE_XRES) * i for i in range(WEEKLY_USAGE_XRES)]
fig, ax = plt.subplots()
ax.set_title(drive_name)
ax.set_ylabel('Natural logarithm of 1+count')
ax.set_xlabel('Days Starting Monday midnight')

# create the x-axis
LINE_WIDTH = .75
y_data = [log(1 + count, e) for count in ctime_counts]
ax.plot(x_data, y_data, color="red", linewidth=LINE_WIDTH, label='creation')
y_data = [log(1 + count, e) for count in mtime_counts]
ax.plot(x_data, y_data, color="green", linewidth=LINE_WIDTH, label='modification')
y_data = [log(1 + count, e) for count in atime_counts]
ax.plot(x_data, y_data, color="blue", linewidth=LINE_WIDTH, label='access')

plt.legend()
plt.savefig(join(output_dir, f'{drive_name}-week'))
plt.close()

print(f'Completed in {round(time() - t0, 3)} seconds.')

# Create the day usage graph -----------------------------------------------
t0 = time()
print('Generating day usage graph...', end=' ', flush=True)

mtime_counts = [0] * DAY_USAGE_XRES
atime_counts = [0] * DAY_USAGE_XRES
ctime_counts = [0] * DAY_USAGE_XRES

get_index = lambda _time: round((DAY_USAGE_XRES - 1) * (((_time.hour * 60 * 60) + \
    (_time.minute * 60) + _time.second) / (24 * 60 * 60)))
for mtime, atime, ctime in zip(mtimes, atimes, ctimes):
    mtime_counts[get_index(mtime)] += 1
    atime_counts[get_index(atime)] += 1
    ctime_counts[get_index(ctime)] += 1

x_data = [(24 / DAY_USAGE_XRES) * i for i in range(DAY_USAGE_XRES)]
fig, ax = plt.subplots()
ax.set_title('Day Usage')
ax.set_ylabel('Natural logarithm of 1+count')
ax.set_xlabel('Hours of Day')

# create the x-axis
LINE_WIDTH = .75
y_data = [log(1 + count, e) for count in ctime_counts]
ax.plot(x_data, y_data, color="red", linewidth=LINE_WIDTH, label='creation')
y_data = [log(1 + count, e) for count in mtime_counts]
ax.plot(x_data, y_data, color="green", linewidth=LINE_WIDTH, label='modification')
y_data = [log(1 + count, e) for count in atime_counts]
ax.plot(x_data, y_data, color="blue", linewidth=LINE_WIDTH, label='access')

plt.legend()
plt.savefig(join(output_dir, f'{drive_name}-days'))
plt.close()

print(f'Completed in {round(time() - t0, 3)} seconds.')

# Create the hour usage graph -----------------------------------------------
t0 = time()
print('Generating hour usage graph...', end=' ', flush=True)
mtime_counts = [0] * HOUR_USAGE_XRES
atime_counts = [0] * HOUR_USAGE_XRES
ctime_counts = [0] * HOUR_USAGE_XRES

get_index = lambda _time: round((HOUR_USAGE_XRES - 1) * ((
    (_time.minute * 60) + _time.second) / (60 * 60)))
for mtime, atime, ctime in zip(mtimes, atimes, ctimes):
    mtime_counts[get_index(mtime)] += 1
    atime_counts[get_index(atime)] += 1
    ctime_counts[get_index(ctime)] += 1

x_data = [(60 / HOUR_USAGE_XRES) * i for i in range(HOUR_USAGE_XRES)]
fig, ax = plt.subplots()
ax.set_title('Hour Usage')
ax.set_ylabel('Natural logarithm of 1+count')
ax.set_xlabel('Minutes in Hour')

# create the x-axis
LINE_WIDTH = .75
y_data = [log(1 + count, e) for count in ctime_counts]
ax.plot(x_data, y_data, color="red", linewidth=LINE_WIDTH, label='creation')
y_data = [log(1 + count, e) for count in mtime_counts]
ax.plot(x_data, y_data, color="green", linewidth=LINE_WIDTH, label='modification')
y_data = [log(1 + count, e) for count in atime_counts]
ax.plot(x_data, y_data, color="blue", linewidth=LINE_WIDTH, label='access')

plt.legend()
plt.savefig(join(output_dir, f'{drive_name}-hours'))
plt.close()

print(f'Completed in {round(time() - t0, 3)} seconds.')

# Create the depths graph --------------------------------------------------
t0 = time()
print('Generating file depths graph...', end=' ', flush=True)
depth_counts = [0] * (max(depths))
for depth in depths:
    depth_counts[depth - 1] += 1

x_data = [i for i in range(1, len(depth_counts) + 1)]
y_data = [log(1 + count, e) for count in depth_counts]
fig, ax = plt.subplots()
ax.set_title('Depth of Files')
ax.set_ylabel('Natural logarithm of 1+count')
ax.set_xlabel('Depth in file hierarchy')
ax.plot(x_data, y_data, linewidth=1)

plt.savefig(join(output_dir, f'{drive_name}-depth-of-files'))
plt.close()

print(f'Completed in {round(time() - t0, 3)} seconds.')

# Plot the file sizes distribution --------------------------------------------
t0 = time()
print('Generating file size distribution graph...', end=' ', flush=True)

file_size_counts = [0] * SIZE_DISTRIBUTION_XRES

file_sizes = [log(1 + size, e) for size in sizes] # convert to natural log value
max_size = max(file_sizes)

get_index = lambda size: round((len(file_size_counts) - 1) * (size / max_size))

for size in file_sizes:
    file_size_counts[get_index(size)] += 1

x_data = [(max_size / len(file_size_counts)) * i for i in range(len(file_size_counts))]
y_data = [log(1 + i, e) for i in file_size_counts]

fig, ax = plt.subplots()
ax.set_title('Distribution of File Sizes')
ax.set_ylabel('Natural logarithm of 1+count')
ax.set_xlabel('Natural logarithm of 1+size in bytes')
ax.plot(x_data, y_data, linewidth=1)

plt.savefig(join(output_dir, f'{drive_name}-size-distribution'))
plt.close()

print(f'Completed in {round(time() - t0, 3)} seconds.')

# Plot the filename extensions graph --------------------------------------------
t0 = time()
print('Generating file extensions count graph...', end=' ', flush=True)

extensions = defaultdict(int)
NO_EXT = 'no extension'
for file_path in file_paths:
    file_name = basename(file_path).lower()
    dot_index = file_name.rfind('.')
    if dot_index > -1:
        extensions[file_name[dot_index + 1:]] += 1
    else:
        extensions[NO_EXT] += 1

# Sort the data:
extensions = [(k, v) for k, v in extensions.items()]
extensions.sort(key=lambda i: i[1], reverse=True)

# Write to file:
with open(join(output_dir, f'{drive_name}-extension-counts.csv'), 'w') as file:
    writer = csv.writer(file)
    writer.writerow(['Extension', 'Count'])
    writer.writerows(extensions)


print(f"Completed in {round(time() - t0, 3)} seconds.")
