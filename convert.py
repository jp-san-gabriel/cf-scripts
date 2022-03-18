# Read the file as XML
import xml.etree.ElementTree as et
from datetime import datetime
from time import time
from sys import argv
from _io import TextIOWrapper
from typing import List
from os.path import basename

NS = '{http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML}'
TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def load_xml(file_path):
    t0 = time()
    print(f'Parsing XML file {file_path}...', end=' ', flush=True)
    doc = et.parse(argv[1])
    print(f'completed in {round(time() - t0, 4)}s')
    return doc

def get_volumes(doc: et.ElementTree):
    root = doc.getroot()
    return root.findall(f"{NS}volume")

def get_element(el: et.ElementTree, name: str):
    el = el.find(f"{NS}{name}")
    if el is not None:
        return el.text
    return ''

def get_seconds_time(el: et.ElementTree, name: str):
    date_str = get_element(el, name)
    if date_str:
        return str(round(datetime.strptime(date_str, TIME_FORMAT).timestamp()))
    return ''

def save_metadata(vol: et.ElementTree, file:TextIOWrapper):
    for fo in vol.findall(f"{NS}fileobject"):
        # only include a file object if it is a regular file and has an inode
        inode = fo.find(f"{NS}inode")
        name_type = fo.find(f"{NS}name_type").text

        if inode is not None and name_type == 'r':
            # create a list with 20 items
            data = [''] * 20

            # save the inode
            data[12] = inode.text

            # save the hash digests
            hashdigests = fo.findall(f"{NS}hashdigest")
            for h in hashdigests:
                if h.get('type', '') == 'md5':
                    data[1] = h.text
                elif h.get('type', '') == 'sha1':
                    data[0] = h.text

            # get the file size
            data[9] = get_element(fo, 'filesize')

            # get the allocated value
            data[10] = get_element(fo, 'alloc')

            # get the mac times
            data[13] = get_seconds_time(fo, 'crtime')
            data[14] = get_seconds_time(fo, 'mtime')
            data[15] = get_seconds_time(fo, 'atime')

            # get the path
            data[16] = get_element(fo, 'filename')

            file.write(f"{'|'.join(data)}\n")


if __name__ == '__main__':
    doc = load_xml(argv[1])
    volumes = get_volumes(doc)
    t0 = time()
    print('Saving files metadata...', end=' ', flush=True)
    # create the output filename
    ext_index = basename(argv[1]).rfind('.')
    if ext_index > -1:
        file_name = basename(argv[1])[:ext_index] + '.out'
    else:
        file_name += argv[1] + '.out'
    with open(file_name, 'w') as file:
        for volume in volumes:
            save_metadata(volume, file)

    print(f"completed in {round(time() - t0, 4)} seconds.")

