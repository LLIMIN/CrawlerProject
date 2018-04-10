"""
爬取猫眼电影榜单的热映榜单前10，主要是使用requests和正则表达式
爬取过程中遇到的问题：
1、遇到猫眼的反爬虫机制，自定义headers即可避免
2、保存文件时fd.writer报需要bytes非str，原因是open模式是ab，改成a即可
3、data.txt中的中文是unicode格式，解决open时使用utf-8编码，json时ensure_ascii=False
"""
import re
import requests
from requests.exceptions import RequestException


def get_one_page(url):
    try:
        headers = {'user-agent': 'my-app/0.0.1'}
        html = requests.get(url, headers=headers)
    except RequestException as e:
        print(e)
    else:
        if html.status_code == 200:
            return html.text
        return None


def parse_one_page():
    url = "http://maoyan.com/board/"
    html = get_one_page(url)
    # print(html)
    print("-" * 40)
    if html:
        pattern = re.compile(
            '<dd>.*?board-index.*?>(.*?)</i>.*?title="(.*?)".*?data-src="(.*?)".*?"star">(.*?)</p>.*?"releasetime">(.*?)</p>.*?"integer">(.*?)</i>.*?"fraction">(.*?)</i>.*?</dd>',
            re.S)
        items = re.findall(pattern, html)
        # print(items)
        for item in items:
            yield {
                "ranking": item[0],
                "name": item[1],
                "images": item[2],
                "stars": item[3].strip()[3:],
                "time": item[4][5:],
                "score": item[5] + item[6]
            }


def save_to_file(content):
    import json
    with open("data.txt", "a", encoding="utf-8") as fd:
        fd.write(json.dumps(content, ensure_ascii=False) + "\n")


def run_main():
    data = parse_one_page()
    for item in data:
        save_to_file(item)


if __name__ == "__main__":
    run_main()
