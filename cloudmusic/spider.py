"""
爬取网易云音乐的歌单，并且爬取里面的歌曲信息
使用requests和bs4分析
过程中遇到到的问题：
1、通过复制浏览器的url爬取，没有发现歌单数据，内容也不是Ajax加载
通过查看浏览器后台请求的url，发现和浏览器地址栏上的url是不一致的
浏览器地址栏：http://music.163.com/#/discover/playlist
浏览器后台请求的url：http://music.163.com/discover/playlist
通过爬取第二个url，成功爬取到数据
"""
import re
import traceback
import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlencode
from pymongo import MongoClient
from multiprocessing import Pool, Queue
from functools import partial
from config import *

client = MongoClient(MONGO_HOST)
db = client[MONGO_DB]
q = Queue()
url = 'http://music.163.com/discover/playlist'


def get_one_page(url, args):
    try:
        headers = {"user-agent": UserAgent().random}
        response = requests.get(url, headers=headers, params=args)
        # print(response.url)
        if response.status_code == 200:
            return response.text
        else:
            print("响应码：", response.status_code)
    except Timeout:
        print("请求超时")


def parse_page(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        songs = soup.select('#m-pl-container > li')
        for song in songs:
            item = {
                "title": song.select('p[class="dec"] > a')[0].text,
                "username": song.select('p > a')[1].text,
                "listeners": song.select('div > div > span')[1].text,
                "href": "http://music.163.com" + song.select('p[class="dec"] > a')[0].attrs['href'],
                "image": song.select('div > img')[0].get('src')
            }
            q.put(item['href'])
            yield item
    except Exception:
        traceback.print_exc()


def save_to_mongo(data, tb_name):
    try:
        if db[tb_name].insert(data):
            print("插入DB成功：", data)
        else:
            print("插入DB失败")
    except Exception:
        traceback.print_exc()


def get_args(page_number):
    return {
        "order": "hot",
        "cat": "全部",
        "limit": 35,
        "offset": 35 * page_number,
    }


def run_main(args, url):
    # 获取页面
    html = get_one_page(url, args)
    # 分析页面，得到所有歌单的简单信息
    data = parse_page(html)
    # 保存歌单信息到db
    save_to_mongo(data, ALL_SHEETS)
    #  todo 获取歌单里面的歌曲信息,得不到歌曲的时长和专辑名称
    # get_songs_from_page()


def get_songs_from_page():
    try:
        print("队列长度：", q.qsize())
        url = q.get()
        print("url:", url)
        if url:
            html = get_one_page(url, args=None)
            parse_song_info(html)
    except Exception:
        traceback.print_exc()


def parse_song_info(html):  # 后续再考虑怎么获取
    soup = BeautifulSoup(html, 'lxml')
    song_list = soup.select('.m-table')
    # print(song_list)
    with open("soup.html", 'w', encoding='utf-8') as fd:
        fd.write(html)
    for song in song_list:
        item = {
            "title": soup.title.string.strip().split('-')[0],
            # "song_name": song.select()
        }
        print(item)


def multi_main():
    p = Pool(4)
    p.map(partial(run_main, url=url), [get_args(i) for i in range(38)])  # 总共38页
    p.close()
    p.join()


if __name__ == "__main__":
    # run_main()

    multi_main()
