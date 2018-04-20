"""
爬取猫眼电影榜单的国内票房榜前10，主要是使用requests和bs4
遇到的问题：
1、票房数据其实是加密过的生僻unicode编码，而且每次访问获得的unicode是随机生成的
方法一、需要分析外部字体(eot,woff)，得到相应的数字，分析方法有误，失败了
方法二、发现有个接口可以直接获取猫眼的票房信息（http://piaofang.maoyan.com/history/date/box.json），GET方法即可，简单可行
"""
import re
from bs4 import BeautifulSoup
import requests
from requests.exceptions import Timeout
from fake_useragent import UserAgent

url = 'http://maoyan.com/board/1'
headers = {
    "User-Agent": UserAgent().random
}


def get_page(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except Timeout:
        get_page(url)


def parse_page(context):
    soup = BeautifulSoup(context, 'lxml')
    css = soup.find('style')
    eot_url = get_eot_url(css.__str__())
    print(eot_url)
    num_chars = num_char(eot_url)
    print(num_chars)

    def _filter_star(data):
        if data:
            return data[0].text[3:]
        else:
            return ""

    all_info = soup.select('#app > div > div > div > dl > dd')
    for info in all_info:
        # print('before yield')
        yield {
            # "ranking": info.select('i')[0].text,
            "name": info.select('p > a')[0].attrs['title'],
            # "star": _filter_star(info.select('p[class="star"]')),
            # "time": info.select('p[class="releasetime"]')[0].text[5:],
            "real_boxoffice": num_mapping(info.select('span[class="stonefont"]')[0].text, num_chars),
            # "real_times": info.select('p[class="realtime"]')[0].text,
            # "total_boxoffice": info.select('p[class="total-boxoffice"]')[0].text.strip()[3:],
            "total_boxoffice": num_mapping(info.select('span[class="stonefont"]')[1].text, num_chars),
            # "image": info.select('img[class="board-img"]')[0].attrs['data-src']
        }
        # print('after yield')


def run_main():
    context = get_page(url)
    # print(context)
    data = parse_page(context)
    for i in data:
        print(i)


def get_eot_url(css):
    """从源代码中的css中获取外部字体路径，一般有eot(ie使用),woff(通用),这里获取eot字体路径，以后最好还是使用woff"""
    p = re.compile(r".*?src: url\('(.*?)'\);")
    eot_url = re.findall(p, css)
    return 'http:' + eot_url[0]


def num_char(eot_url):
    """以二进制的方式打开eot字库，一堆乱码，刷洗得到码位，然后以0-9排序，结果呵呵"""

    import io
    r = requests.get(eot_url, headers=headers)
    data = io.BytesIO(r.content)
    lines = data.readlines()
    p = re.compile(b"\x07uni(....)")
    nums = re.findall(p, lines[-1])
    # return dict(enumerate(nums, start=0))
    return dict(zip([i.decode() for i in nums], range(10)))  # 字体不是从0-9排序的(乱序)，所以结果都错了，不能用这种方法读取字库


def num_mapping(data, num_chars):
    """映射关系"""
    nums = []
    data = repr(data)
    print(data)
    for char in data.upper().split(r'\U'):
        if char in ("'", None):
            continue
        if char.count('.'):
            num = num_chars.get(char.split('.')[0])
            nums.append(str(num) + '.')
        elif char.count("'"):
            num = num_chars.get(char.split("'")[0])
            nums.append(str(num))
        else:
            num = num_chars.get(char)
            nums.append(str(num))
    return ''.join(nums)


if __name__ == "__main__":
    run_main()

    # url2 = 'http://piaofang.maoyan.com/history/date/box.json'
    # response = requests.get(url2, headers=headers)
    # print(response.text)

    #
    # url3 = 'http://vfile.meituan.net/colorstone/28fae620c7ecd2a899049027110985e93168.eot'
    # num_char(url3)
