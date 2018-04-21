"""
猫眼电影的字库每次的Unicode编码和对应的数字值不一样，但是每个字库里的数字值都是0-9(还有个"."和空白）
因此随便使用个猫眼电影的字库作为基础字库，其他字库通过对比该基础字库的字形数据就可以得到对应的数字值
识别字库可以使用工具：http://fontstore.baidu.com/static/editor/index.html

这里使用fontTools工具分析WOFF字库，该工具支持otf，ttf，woff，不支持eot，svg没有试过
该工具还提供几个客户端命令，功能强大，如ttx可以格式，具体看：https://darknode.in/font/font-tools-guide/
或者：https://pypi.org/project/FontTools/

关于woff，eot，ttf，otf字库等介绍：https://www.jianshu.com/p/0d3be9b77eb9

主要参考文章：https://zhuanlan.zhihu.com/p/33112359

"""

from fontTools.ttLib import TTFont


class AnalysisFont(object):
    def __init__(self):
        self.num_mapping = {}
        # 使用个基础字库（人工识别），然后可以通过比对基础字体字形数据，得到其真实的数字值
        self.base_font = TTFont('base.woff')
        self.base_num_list = ['.', '5', '3', '7', '6', '2', '0', '9', '1', '4', '8']
        self.base_unicode = ['x', 'uniF04B', 'uniE493', 'uniEDC1', 'uniE03C', 'uniF8F9', 'uniE35B', 'uniF6E4',
                             'uniE5F6', 'uniEE26', 'uniF39E']

    def get_num_list(self, woff_file):
        my_font = TTFont(woff_file)
        my_unicode = my_font.getGlyphOrder()  # 字符编码,例：['glyph00000', 'x', 'uniF866', 'uniF8D8', 'uniF353', 'uniE58E', 'uniF668', 'uniF811', 'uniE004', 'uniF664', 'uniF12B', 'uniE060']
        # my_tb = my_font.keys()  # 表 ['GlyphOrder', 'head', 'hhea', 'maxp', 'OS/2', 'hmtx', 'cmap', 'loca', 'glyf', 'name', 'post', 'GSUB']

        for i in range(1, 12):  # self.my_unicode 第0个是空（glyph00000），所以从1开始，共11个，0-9和.
            my_glyph = my_font['glyf'][my_unicode[i]]  # glyf表数据
            for j in range(11):  # 基础字库已经过滤第0个是空（glyph00000）的情况，所以从0开始
                base_glyph = self.base_font['glyf'][self.base_unicode[j]]
                if my_glyph == base_glyph:  # 对比字形数据，得到数字值
                    self.num_mapping[my_unicode[i]] = self.base_num_list[j]
                    break
        return self.num_mapping


if __name__ == "__main__":
    maoyanfont = AnalysisFont()
    print(maoyanfont.get_num_list('test.woff'))
    # {'x': '.', 'uniF866': '6', 'uniF8D8': '7', 'uniF353': '3', 'uniE58E': '8', 'uniF668': '4', 'uniF811': '1',
    # 'uniE004': '5', 'uniF664': '2', 'uniF12B': '9', 'uniE060': '0'}
