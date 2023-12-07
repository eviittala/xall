import os
import sys
import re
import tarfile
import zipfile
import argparse
import shutil
import gzip

paths = []

def isGzipFile(filename):
    tail = getFileTail(filename)
    if tail == "gz":
        with gzip.open(filename, 'rb') as f_in:
            try:
                f_in.read(1)
                return True
            except:
                pass
    return False

def isCompressedFile(filename):
    notCompressedFiles = ["bin", "log", "txt"]
    try:
        return getFileTail(filename) not in notCompressedFiles and (tarfile.is_tarfile(filename) or zipfile.is_zipfile(filename) or isGzipFile(filename))
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
    if __name__ == "__main__":
        print("{0} ... ".format(filename), end='')
    path = folder + "/" + getFileHead(filename)
    file = folder + "/" + filename
    try:
        if tarfile.is_tarfile(file):
            if __name__ == "__main__":
                print("tarfile: ", end='')
            try:
                os.mkdir(path)
            except FileExistsError:
                pass
            tar = tarfile.open(file)
            tar.extractall(path)
            tar.close()
        elif zipfile.is_zipfile(file):
            if __name__ == "__main__":
                print("zipfile: ", end='')
            with zipfile.ZipFile(file) as myzip:
                myzip.extractall(path)
        elif isGzipFile(file):
            if __name__ == "__main__":
                print("gzipfile: ", end='')
            try:
                os.mkdir(path)
            except FileExistsError:
                pass
            with gzip.open(file, 'rb') as f_in:
                with open(path + "/" + filename[0:-3], "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
    except:
        if __name__ == "__main__":
            print("nok")
        return False
    if __name__ == "__main__":
        print("ok")
    return True

def xfile(folder, filename, remove_file = False):
    head = getFileHead(filename)
    if extractFile(folder, filename):
        paths.append(folder + "/" + head)
        if remove_file:
            os.remove(folder + "/" + filename)

def searchCompressedFiles(folder):
    try:
        with os.scandir(folder) as it:
            for entry in it:
                if not entry.name.startswith('.'):
                    if entry.is_file():
                        if isCompressedFile(folder + "/" + entry.name):
                            xfile(folder, entry.name, remove_file=True)
                    elif entry.is_dir():
                        paths.append(folder + "/" + entry.name)
    except FileNotFoundError:
        pass

def goThroughAllPaths():
    while len(paths) > 0:
        path = paths[0]
        paths.pop(0)
        searchCompressedFiles(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=sys.argv[0], description='Extracts all compressed files')
    parser.add_argument('filename', help='Filename to compress')
    parser.add_argument('-v', '--version', help='Version of this file', action='version', version='%(prog)s 1.6')
    args = parser.parse_args()
    if isCompressedFile(args.filename):
        xfile(".", args.filename)
        goThroughAllPaths()
    else:
        print("Filename: {0} is not compressed file.".format(args.filename))

