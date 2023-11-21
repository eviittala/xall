import unittest
from unittest.mock import patch, MagicMock
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

class TestXall(unittest.TestCase):

    def setup(self):
        pass

    def tearDown(self):
        pass

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
        mockTarfile.return_value = False
        mockZipfile.is_zipfile.return_value = True
        folder = "."
        file = "test.zip"
        xall.extractFile(folder, file)
        mockZipfile.is_zipfile.assert_called_with("./" + file)
        mockZipfile.ZipFile.assert_called_with("./" + file)
        #TODO Eero: xall.extractall.assert_called_with("./" + "test")

    @patch("os.system")
    @patch("xall.extractFile")
    def testXfile(self, extractFile, osSystem):
        folder = "."
        file = "test.zip"
        xall.xfile(folder, file, True)
        extractFile.assert_called_with(folder, file)
        osSystem.assert_called_with("rm" + " " + folder + "/" + file)

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

unittest.main()
