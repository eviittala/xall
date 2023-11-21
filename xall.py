import os
import sys
import re
import tarfile
import zipfile
import argparse

paths = []

def isCompressedFile(filename):
    try:
        return tarfile.is_tarfile(filename) or zipfile.is_zipfile(filename)
    except:
        return False

def getFileHead(filename):
    pattern = re.compile(r'\.')
    m = pattern.split(filename)
    return m[0]

def extractFile(folder, filename):
    head = folder + "/" + getFileHead(filename)
    file = folder + "/" + filename
    if tarfile.is_tarfile(file):
        os.mkdir(head)
        tar = tarfile.open(file)
        tar.extractall(head)
        tar.close()
    elif zipfile.is_zipfile(file):
        with zipfile.ZipFile(file) as myzip:
            myzip.extractall(head)

def xfile(folder, filename, remove_file = False):
    head = getFileHead(filename)
    extractFile(folder, filename)
    paths.append(folder + "/" + head)
    if remove_file:
        os.system("rm" + " " + folder + "/" + filename)

def searchCompressedFiles(folder):
    with os.scandir(folder) as it:
        for entry in it:
            if not entry.name.startswith('.'):
                if entry.is_file():
                    if isCompressedFile(folder + "/" + entry.name):
                        xfile(folder, entry.name, remove_file=True)
                elif entry.is_dir():
                    paths.append(folder + "/" + entry.name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=sys.argv[0], description='Extracts all compressed files')
    parser.add_argument('filename', help='Filename to compress')
    parser.add_argument('-v', '--version', help='Version of this file', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    if isCompressedFile(args.filename):
        xfile(".", args.filename)
        while len(paths) > 0:
            path = paths[0]
            paths.pop(0)
            searchCompressedFiles(path)

