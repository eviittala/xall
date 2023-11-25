import unittest
from unittest.mock import patch, MagicMock, mock_open
import xall
import os

#https://stackoverflow.com/questions/65830675/is-it-possible-to-mock-os-scandir-and-its-attributes
class DirFileEntry:
    def __init__(self, filename, is_file):
        self.name = filename
        self.filetype = is_file

    def __enter__(self):
        return [self]

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def is_file(self):
        return self.filetype

    def is_dir(self):
        return not self.filetype

    def path(self):
        return self.path


class ZipFile:
    def __init__(self, filename, path):
        self.filename = filename
        self.path = path
        self.extractCalled = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def extractall(self, path):
        if path != self.path:
            print("extractall is called with incorrect path: {0} != {1}".format(path, self.path))
        else:
            self.extractCalled = True

class Gzip:
    def __init__(self, filename):
        self.filename = filename
        self.read_called = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self, arg):
        if arg == 1:
            self.read_called = True

class TestXall(unittest.TestCase):

    def setup(self):
        pass

    def tearDown(self):
        pass

    @patch("xall.gzip.open")
    def testIsGzipFile(self, gzip):
        gzip.return_value = Gzip("test.gz")
        self.assertTrue(xall.isGzipFile("test.gz"))
        self.assertTrue(gzip.return_value.read_called)
        gzip.assert_called_with("test.gz", 'rb')

    def testIsGzipFileReturnsFalse(self):
        self.assertFalse(xall.isGzipFile("test.zip"))

    @patch("xall.tarfile.is_tarfile")
    def testIsCompressedFileTar(self, mockTarfile):
        mockTarfile.return_value = True
        self.assertTrue(xall.isCompressedFile("test.tar.gz"))
        mockTarfile.assert_called_with("test.tar.gz")

    @patch("xall.zipfile.is_zipfile")
    @patch("xall.tarfile.is_tarfile")
    def testIsCompressedFileZip(self, mockTarfile, mockZipfile):
        mockTarfile.return_value = False
        mockZipfile.return_value = True
        self.assertTrue(xall.isCompressedFile("test.zip"))
        mockTarfile.assert_called_with("test.zip")
        mockZipfile.assert_called_with("test.zip")

    def testGetFileHead(self):
        self.assertEqual("file", xall.getFileHead("file.zip"))
        self.assertEqual("file", xall.getFileHead("file.tar.gz"))
        self.assertEqual("file", xall.getFileHead("file.log.tar.gz"))

    @patch("os.mkdir")
    @patch("xall.tarfile")
    def testExtractFileTar(self, mockTarfile, mockOsMkdir):
        mockTarfile.is_tarfile.return_value = True
        tar = mockTarfile.open.return_value
        folder = "."
        file = "test.tar.gz"
        xall.extractFile(folder, file)
        mockTarfile.is_tarfile.assert_called_with("./" + file)
        mockTarfile.open.assert_called_with("./" + file)
        mockOsMkdir.assert_called_with("./" + "test")
        tar.extractall.assert_called_with("./" + "test")
        tar.close.assert_called_with()

    @patch("xall.tarfile.is_tarfile")
    @patch("xall.zipfile")
    def testExtractFileZip(self, mockZipfile, mockTarfile):
        folder = "."
        file = "test.zip"
        mockTarfile.return_value = False
        mockZipfile.is_zipfile.return_value = True
        zipfile = ZipFile("./" + file, folder + "/" + file[:-4])
        mockZipfile.ZipFile.return_value = zipfile
        xall.extractFile(folder, file)
        mockZipfile.is_zipfile.assert_called_with("./" + file)
        mockZipfile.ZipFile.assert_called_with("./" + file)
        self.assertTrue(zipfile.extractCalled)

    @patch("os.mkdir")
    @patch("xall.tarfile.is_tarfile")
    @patch("xall.zipfile.is_zipfile")
    @patch("xall.isGzipFile")
    @patch("xall.gzip.open")
    @patch("xall.shutil.copyfileobj")
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def testExtractFileGzip(self, builtInsOpen,  copyfileobj, gzip, mockIsGzip, mockZipfile, mockTarfile, mockOsMkdir):
        folder = "."
        file = "test.gz"
        mockTarfile.return_value = False
        mockZipfile.return_value = False
        mockIsGzip.return_value = True
        gzip.return_value = Gzip("test.gz")
        xall.extractFile(folder, file)
        mockOsMkdir.assert_called_with("./" + "test")
        builtInsOpen.assert_called_with("./" + "test/test", 'wb')
        copyfileobj.assert_called_with(gzip.return_value.__enter__(), builtInsOpen.return_value)

    @patch("os.remove")
    @patch("xall.extractFile")
    def testXfile(self, extractFile, osRemove):
        folder = "."
        file = "test.zip"
        xall.xfile(folder, file, True)
        extractFile.assert_called_with(folder, file)
        osRemove.assert_called_with(folder + "/" + file)

    @patch("os.scandir")
    @patch("xall.isCompressedFile")
    @patch("xall.xfile")
    def testSearchCompressedFiles(self, xfile, isCompressedFile, osScandir):
        osScandir.return_value = DirFileEntry("test.zip", True)
        isCompressedFile.return_value = True
        folder = "testFolder"
        xall.searchCompressedFiles(folder)
        osScandir.assert_called_with(folder)
        xfile.assert_called_with(folder, "test.zip", remove_file=True)
        isCompressedFile.assert_called_with(folder + "/" + "test.zip")

    @patch("os.scandir")
    def testSearchCompressedFiles(self, osScandir):
        osScandir.return_value = DirFileEntry("myFolder", False)
        folder = "testFolder"
        xall.searchCompressedFiles(folder)
        osScandir.assert_called_with(folder)
        self.assertEqual(xall.paths[0], folder + "/" +"myFolder")
        self.assertEqual(len(xall.paths), 1)

    @patch("xall.searchCompressedFiles")
    def testGoThroughAllPaths(self, searchCompressedFiles):
        folder = "testFolder"
        xall.paths.append(folder)
        xall.goThroughAllPaths()
        searchCompressedFiles.assert_called_with(folder)
        self.assertEqual(len(xall.paths), 0)

unittest.main()
