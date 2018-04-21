"""
WOFF结构详情可以查看官方文档：http://www.w3.org/TR/WOFF/
本代码是在github在别人写的（忘了链接，尬尴），这份代码分析WOFF结构，得到图元信息
但是猫眼电影的字库并不是按0-9顺序排序，所以最后的映射结果是错误的，同时也不建议用这种方法
分析WOFF字库，有现成的模块fontTools分析会更加简单，看另外woff.py

"""

import struct
import zlib


def woff_headers(infile):
    WOFFHeader = {'signature': struct.unpack(">I", infile.read(4))[0],
                  'flavor': struct.unpack(">I", infile.read(4))[0],
                  'length': struct.unpack(">I", infile.read(4))[0],
                  'numTables': struct.unpack(">H", infile.read(2))[0],
                  'reserved': struct.unpack(">H", infile.read(2))[0],
                  'totalSfntSize': struct.unpack(">I", infile.read(4))[0],
                  'majorVersion': struct.unpack(">H", infile.read(2))[0],
                  'minorVersion': struct.unpack(">H", infile.read(2))[0],
                  'metaOffset': struct.unpack(">I", infile.read(4))[0],
                  'metaLength': struct.unpack(">I", infile.read(4))[0],
                  'metaOrigLength': struct.unpack(">I", infile.read(4))[0],
                  'privOffset': struct.unpack(">I", infile.read(4))[0],
                  'privLength': struct.unpack(">I", infile.read(4))[0]}
    return WOFFHeader


def get_dict_numb_from_woff(path):
    with open(path, "rb") as fd:
        return analyze_font(fd)


def get_dict_numb_from_BytesIO(fd):
    return analyze_font(fd)


def analyze_font(fd):
    char_num = []
    dict_num = dict()
    _woff_headers = woff_headers(fd)
    TableDirectoryEntries = []

    for i in range(0, _woff_headers['numTables']):
        TableDirectoryEntries.append({'tag': struct.unpack(">I", fd.read(4))[0],
                                      'offset': struct.unpack(">I", fd.read(4))[0],
                                      'compLength': struct.unpack(">I", fd.read(4))[0],
                                      'origLength': struct.unpack(">I", fd.read(4))[0],
                                      'origChecksum': struct.unpack(">I", fd.read(4))[0]})
    for TableDirectoryEntry in TableDirectoryEntries:
        fd.seek(TableDirectoryEntry['offset'])
        compressedData = fd.read(TableDirectoryEntry['compLength'])
        if TableDirectoryEntry['compLength'] != TableDirectoryEntry['origLength']:
            uncompressedData = zlib.decompress(compressedData)
        else:
            uncompressedData = compressedData

        if b"uni" in uncompressedData:
            for cha in uncompressedData.split(b"\x07"):
                if b"uni" in cha:
                    char_num.append(cha.strip(b"\x00"))
    for k, _unicode in enumerate(char_num):
        dict_num[_unicode] = str(k)  # 猫眼电影的字库并不是按顺序排序，所以这样做也是错误的
    dict_num['.'] = '.'
    return dict_num


if __name__ == "__main__":
    print(get_dict_numb_from_woff("test.woff"))
