"""
爬取猫眼电影榜单的热映榜单前10，主要是使用requests和xpath
"""

import requests
from requests.exceptions import RequestException
from lxml import etree
from fake_useragent import UserAgent


def get_one_page(url):
    try:
        headers = {'user-agent': UserAgent().random}
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
    # print("-" * 40)
    selector = etree.HTML(html)

    # ranking = selector.xpath(r'//*[@id="app"]/div/div/div/dl/dd/i/text()')
    # name = selector.xpath(r'//*[@id="app"]/div/div/div/dl/dd/div/div/div[1]/p[1]/a/text()')
    # images = selector.xpath(r'//*[@id="app"]/div/div/div/dl/dd/a/img[2]/@data-src')
    # stars = list(map(lambda x: x.strip()[3:], selector.xpath(r'//*[@class="star"]/text()')))
    # times = list(map(lambda x: x[5:], selector.xpath(r'//*[@class="releasetime"]/text()')))
    # score = _deal_score_data(selector.xpath(r'//*[@class="score"]/i/text()'))
    # data = list(zip(ranking, name, images, stars, times, score))
    # item_list = ["ranking", "name", "images", "stars","times", "score"]
    # for item in data:
    #     yield dict(zip(item_list, item))

    items = {}
    items["ranking"] = selector.xpath(r'//*[@id="app"]/div/div/div/dl/dd/i/text()')
    items["name"] = selector.xpath(r'//*[@id="app"]/div/div/div/dl/dd/div/div/div[1]/p[1]/a/text()')
    items["images"] = selector.xpath(r'//*[@id="app"]/div/div/div/dl/dd/a/img[2]/@data-src')
    items["stars"] = list(map(lambda x: x.strip()[3:], selector.xpath(r'//*[@class="star"]/text()')))
    items["times"] = list(map(lambda x: x[5:], selector.xpath(r'//*[@class="releasetime"]/text()')))
    items["score"] = _deal_score_data(selector.xpath(r'//*[@class="score"]/i/text()'))
    data = list(zip(items["ranking"], items["name"], items["images"], items["stars"], items["times"], items["score"]))
    for item in data:
        yield dict(zip(items.keys(), item))


def _deal_score_data(data):
    if isinstance(data, list):
        rel = []
        for score in zip(data[0::2], data[1::2]):
            rel.append("".join(score))
        return rel


def run_main():
    data = parse_one_page()
    for item in data:
        print(item)


if __name__ == "__main__":
    run_main()
