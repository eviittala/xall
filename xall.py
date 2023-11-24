import os
import sys
import re
import tarfile
import zipfile
import argparse
import shutil
import gzip

paths = []

def is_gzipfile(filename):
    tail = getFileTail(filename)
    return tail == "gz"

def isCompressedFile(filename):
    try:
        return tarfile.is_tarfile(filename) or zipfile.is_zipfile(filename) or is_gzipfile(filename)
    except:
        return False

def getFileHead(filename):
    pattern = re.compile(r'\.')
    m = pattern.split(filename)
    return m[0]

def getFileTail(filename):
    pattern = re.compile(r'\.')
    m = pattern.split(filename)
    return m[-1]

def extractFile(folder, filename):
    print("{0} ... ".format(filename), end='')
    head = folder + "/" + getFileHead(filename)
    file = folder + "/" + filename
    try:
        if tarfile.is_tarfile(file):
            try:
                os.mkdir(head)
            except FileExistsError:
                pass
            tar = tarfile.open(file)
            tar.extractall(head)
            tar.close()
        elif zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as myzip:
                myzip.extractall(head)
        elif is_gzipfile(file):
            try:
                os.mkdir(head)
            except FileExistsError:
                pass
            with gzip.open(file, 'rb') as f_in:
                # TODO filenamewithout extension
                with open(head + "/" + getFileHead(filename), "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
    except:
        print("nok")
        return False
    print("ok")
    return True

def xfile(folder, filename, remove_file = False):
    head = getFileHead(filename)
    if extractFile(folder, filename):
        paths.append(folder + "/" + head)
        if remove_file:
            os.remove(folder + "/" + filename)

def searchCompressedFiles(folder):
    with os.scandir(folder) as it:
        for entry in it:
            if not entry.name.startswith('.'):
                if entry.is_file():
                    if isCompressedFile(folder + "/" + entry.name):
                        xfile(folder, entry.name, remove_file=True)
                elif entry.is_dir():
                    paths.append(folder + "/" + entry.name)

def goThroughAllPaths():
    while len(paths) > 0:
        path = paths[0]
        paths.pop(0)
        searchCompressedFiles(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=sys.argv[0], description='Extracts all compressed files')
    parser.add_argument('filename', help='Filename to compress')
    parser.add_argument('-v', '--version', help='Version of this file', action='version', version='%(prog)s 1.2')
    args = parser.parse_args()
    if isCompressedFile(args.filename):
        xfile(".", args.filename)
        goThroughAllPaths()
    else:
        print("Filename: {0} is not compressed file.".format(args.filename))

