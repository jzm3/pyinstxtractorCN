"""
PyInstaller Extractor v2.0 (支持 pyinstaller 6.12.0 及更低版本)
汉化版本
"""

from __future__ import print_function
import os
import struct
import marshal
import zlib
import sys
from uuid import uuid4 as uniquename

class CTOCEntry:
    def __init__(self, position, cmprsdDataSize, uncmprsdDataSize, cmprsFlag, typeCmprsData, name):
        self.position = position
        self.cmprsdDataSize = cmprsdDataSize
        self.uncmprsdDataSize = uncmprsdDataSize
        self.cmprsFlag = cmprsFlag
        self.typeCmprsData = typeCmprsData
        self.name = name

class PyInstArchive:
    PYINST20_COOKIE_SIZE = 24
    PYINST21_COOKIE_SIZE = 24 + 64
    MAGIC = b'MEI\014\013\012\013\016'

    def __init__(self, path):
        self.filePath = path
        self.pycMagic = b'\0' * 4
        self.barePycList = []

    def open(self):
        try:
            self.fPtr = open(self.filePath, 'rb')
            self.fileSize = os.stat(self.filePath).st_size
        except:
            print('[!] 错误：无法打开文件 {0}'.format(self.filePath))
            return False
        return True

    def close(self):
        try:
            self.fPtr.close()
        except:
            pass

    def checkFile(self):
        print('[+] 正在处理文件 {0}'.format(self.filePath))
        searchChunkSize = 8192
        endPos = self.fileSize
        self.cookiePos = -1

        if endPos < len(self.MAGIC):
            print('[!] 错误：文件过小或已损坏')
            return False

        while True:
            startPos = endPos - searchChunkSize if endPos >= searchChunkSize else 0
            chunkSize = endPos - startPos

            if chunkSize < len(self.MAGIC):
                break

            self.fPtr.seek(startPos, os.SEEK_SET)
            data = self.fPtr.read(chunkSize)

            offs = data.rfind(self.MAGIC)

            if offs != -1:
                self.cookiePos = startPos + offs
                break

            endPos = startPos + len(self.MAGIC) - 1
            if startPos == 0:
                break

        if self.cookiePos == -1:
            print('[!] 错误：未找到特征标识，可能是不支持的PyInstaller版本或非PyInstaller打包文件')
            return False

        self.fPtr.seek(self.cookiePos + self.PYINST20_COOKIE_SIZE, os.SEEK_SET)

        if b'python' in self.fPtr.read(64).lower():
            print('[+] PyInstaller 版本：2.1+')
            self.pyinstVer = 21
        else:
            self.pyinstVer = 20
            print('[+] PyInstaller 版本：2.0')

        return True

    def getCArchiveInfo(self):
        try:
            if self.pyinstVer == 20:
                self.fPtr.seek(self.cookiePos, os.SEEK_SET)
                (magic, lengthofPackage, toc, tocLen, pyver) = \
                struct.unpack('!8siiii', self.fPtr.read(self.PYINST20_COOKIE_SIZE))

            elif self.pyinstVer == 21:
                self.fPtr.seek(self.cookiePos, os.SEEK_SET)
                (magic, lengthofPackage, toc, tocLen, pyver, pylibname) = \
                struct.unpack('!8sIIii64s', self.fPtr.read(self.PYINST21_COOKIE_SIZE))

        except:
            print('[!] 错误：该文件不是PyInstaller打包文件')
            return False

        self.pymaj, self.pymin = (pyver//100, pyver%100) if pyver >= 100 else (pyver//10, pyver%10)
        print('[+] Python 版本：{0}.{1}'.format(self.pymaj, self.pymin))
        tailBytes = self.fileSize - self.cookiePos - (self.PYINST20_COOKIE_SIZE if self.pyinstVer == 20 else self.PYINST21_COOKIE_SIZE)
        self.overlaySize = lengthofPackage + tailBytes
        self.overlayPos = self.fileSize - self.overlaySize
        self.tableOfContentsPos = self.overlayPos + toc
        self.tableOfContentsSize = tocLen

        print('[+] 包体长度：{0} 字节'.format(lengthofPackage))
        return True

    def parseTOC(self):
        self.fPtr.seek(self.tableOfContentsPos, os.SEEK_SET)
        self.tocList = []
        parsedLen = 0

        while parsedLen < self.tableOfContentsSize:
            (entrySize, ) = struct.unpack('!i', self.fPtr.read(4))
            nameLen = struct.calcsize('!iIIIBc')

            (entryPos, cmprsdDataSize, uncmprsdDataSize, cmprsFlag, typeCmprsData, name) = \
            struct.unpack( \
                '!IIIBc{0}s'.format(entrySize - nameLen), \
                self.fPtr.read(entrySize - 4))

            try:
                name = name.decode("utf-8").rstrip("\0")
            except UnicodeDecodeError:
                newName = str(uniquename())
                print('[!] 警告：文件名 {0} 包含非法字符，已替换为随机名称 {1}'.format(name, newName))
                name = newName
            
            if name.startswith("/"):
                name = name.lstrip("/")

            if len(name) == 0:
                name = str(uniquename())
                print('[!] 警告：发现未命名文件，已使用随机名称 {0}'.format(name))

            self.tocList.append(CTOCEntry(
                self.overlayPos + entryPos,
                cmprsdDataSize,
                uncmprsdDataSize,
                cmprsFlag,
                typeCmprsData,
                name
            ))
            parsedLen += entrySize
        print('[+] 在CArchive中发现 {0} 个文件'.format(len(self.tocList)))

    def _writeRawData(self, filepath, data):
        nm = filepath.replace('\\', os.path.sep).replace('/', os.path.sep).replace('..', '__')
        nmDir = os.path.dirname(nm)
        if nmDir != '' and not os.path.exists(nmDir):
            os.makedirs(nmDir)

        with open(nm, 'wb') as f:
            f.write(data)

    def extractFiles(self):
        print('[+] 开始提取文件...请稍候')
        extractionDir = os.path.join(os.getcwd(), os.path.basename(self.filePath) + '_extracted')

        if not os.path.exists(extractionDir):
            os.mkdir(extractionDir)

        os.chdir(extractionDir)

        for entry in self.tocList:
            self.fPtr.seek(entry.position, os.SEEK_SET)
            data = self.fPtr.read(entry.cmprsdDataSize)

            if entry.cmprsFlag == 1:
                try:
                    data = zlib.decompress(data)
                except zlib.error:
                    print('[!] 错误：解压缩 {0} 失败'.format(entry.name))
                    continue
                assert len(data) == entry.uncmprsdDataSize

            if entry.typeCmprsData == b'd' or entry.typeCmprsData == b'o':
                continue

            basePath = os.path.dirname(entry.name)
            if basePath != '':
                if not os.path.exists(basePath):
                    os.makedirs(basePath)

            if entry.typeCmprsData == b's':
                print('[+] 可能入口点：{0}.pyc'.format(entry.name))
                if self.pycMagic == b'\0' * 4:
                    self.barePycList.append(entry.name + '.pyc')
                self._writePyc(entry.name + '.pyc', data)

            elif entry.typeCmprsData == b'M' or entry.typeCmprsData == b'm':
                if data[2:4] == b'\r\n':
                    if self.pycMagic == b'\0' * 4: 
                        self.pycMagic = data[0:4]
                    self._writeRawData(entry.name + '.pyc', data)
                else:
                    if self.pycMagic == b'\0' * 4:
                        self.barePycList.append(entry.name + '.pyc')
                    self._writePyc(entry.name + '.pyc', data)
            else:
                self._writeRawData(entry.name, data)
                if entry.typeCmprsData == b'z' or entry.typeCmprsData == b'Z':
                    self._extractPyz(entry.name)

        self._fixBarePycs()

    def _fixBarePycs(self):
        for pycFile in self.barePycList:
            with open(pycFile, 'r+b') as pycFile:
                pycFile.write(self.pycMagic)

    def _writePyc(self, filename, data):
        with open(filename, 'wb') as pycFile:
            pycFile.write(self.pycMagic)
            if self.pymaj >= 3 and self.pymin >= 7:
                pycFile.write(b'\0' * 4)
                pycFile.write(b'\0' * 8)
            else:
                pycFile.write(b'\0' * 4)
                if self.pymaj >= 3 and self.pymin >= 3:
                    pycFile.write(b'\0' * 4)
            pycFile.write(data)

    def _extractPyz(self, name):
        dirName =  name + '_extracted'
        if not os.path.exists(dirName):
            os.mkdir(dirName)

        with open(name, 'rb') as f:
            pyzMagic = f.read(4)
            assert pyzMagic == b'PYZ\0'

            pyzPycMagic = f.read(4)
            if self.pycMagic == b'\0' * 4:
                self.pycMagic = pyzPycMagic
            elif self.pycMagic != pyzPycMagic:
                self.pycMagic = pyzPycMagic
                print('[!] 警告：PYZ内的pyc特征码与CArchive不一致')

            if self.pymaj != sys.version_info.major or self.pymin != sys.version_info.minor:
                print('[!] 警告：当前Python版本({0}.{1})与打包时版本({2}.{3})不同'.format(
                    sys.version_info.major, 
                    sys.version_info.minor,
                    self.pymaj,
                    self.pymin))
                print('[!] 建议使用Python {0}.{1}运行本脚本'.format(self.pymaj, self.pymin))
                print('[!] 已跳过PYZ提取')
                return

            (tocPosition, ) = struct.unpack('!i', f.read(4))
            f.seek(tocPosition, os.SEEK_SET)

            try:
                toc = marshal.load(f)
            except:
                print('[!] 错误：反序列化失败，无法提取 {0}'.format(name))
                return

            print('[+] 在PYZ中发现 {0} 个文件'.format(len(toc)))

            if type(toc) == list:
                toc = dict(toc)

            for key in toc.keys():
                (ispkg, pos, length) = toc[key]
                f.seek(pos, os.SEEK_SET)
                fileName = key

                try:
                    fileName = fileName.decode('utf-8')
                except:
                    pass

                fileName = fileName.replace('..', '__').replace('.', os.path.sep)

                if ispkg == 1:
                    filePath = os.path.join(dirName, fileName, '__init__.pyc')
                else:
                    filePath = os.path.join(dirName, fileName + '.pyc')

                fileDir = os.path.dirname(filePath)
                if not os.path.exists(fileDir):
                    os.makedirs(fileDir)

                try:
                    data = f.read(length)
                    data = zlib.decompress(data)
                except:
                    print('[!] 错误：{0} 解压失败（可能已加密），已保存原始数据'.format(filePath))
                    open(filePath + '.encrypted', 'wb').write(data)
                else:
                    self._writePyc(filePath, data)

def main():
    if len(sys.argv) < 2:
        print('[+] 用法：pyinstxtractor <文件名>')
    else:
        arch = PyInstArchive(sys.argv[1])
        if arch.open():
            if arch.checkFile():
                if arch.getCArchiveInfo():
                    arch.parseTOC()
                    arch.extractFiles()
                    arch.close()
                    print('[+] 文件提取成功：{0}'.format(sys.argv[1]))
                    print('\n现在可以对提取目录中的pyc文件使用反编译工具')
                    return
            arch.close()

class PyInstExtractorError(Exception):
    """异常基类"""
    pass

class InvalidFileError(PyInstExtractorError):
    """无效文件异常"""
    pass

class ExtractionError(PyInstExtractorError):
    """提取失败异常"""
    pass

def dcp(file_path: str, output_dir: str = None) -> str:
    """
    解包PyInstaller打包文件
    
    :param file_path: 要解包的可执行文件路径
    :param output_dir: 输出目录（默认：当前目录/[文件名]_extracted）
    :return: 解包后的目录路径
    :raises: PyInstExtractorError 解包失败时抛出
    """
    try:
        arch = PyInstArchive(file_path)
        
        if not arch.open():
            raise InvalidFileError("无法打开文件")
        
        if not arch.checkFile():
            raise InvalidFileError("文件格式验证失败")
        
        if not arch.getCArchiveInfo():
            raise InvalidFileError("CArchive信息获取失败")
        
        arch.parseTOC()
        arch.extractFiles()
        arch.close()
        print('\n现在可以对提取目录中的pyc文件使用反编译工具')
    
    except Exception as e:
        # 保留原始错误打印逻辑
        if hasattr(e, '__cause__') and e.__cause__:
            err_msg = f"{str(e)} (原因: {str(e.__cause__)})"
        else:
            err_msg = str(e)
        raise PyInstExtractorError(err_msg) from None

if __name__ == '__main__':
    main()
