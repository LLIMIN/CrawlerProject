"""
使用selenium+PhantomJS模拟点击，在天猫上搜索关键字获取产品信息（bs4分析html）
注释：
presence_of_element_located   等待元素加载完成 ，这里是判断搜索输入框是否加载
element_to_be_clickable    等待是否可以点击，搜索按钮
-----
WebDriverWait.until()返回WebElement对象，该对象属性查看：
http://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.remote.webelement
"""
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as PQ
from config import *
from pymongo import MongoClient

browser = webdriver.PhantomJS(service_args=SERVICR_ARGS)
browser.set_window_size(1400, 900)
wait = WebDriverWait(browser, 10)
client = MongoClient(MONGO_HOST)
db = client[MONGO_DB]


def search_keyword(keyword=KEYWORD):
    """
    在天猫上搜索关键字
    :param keyword: 关键字，str
    :return: 总页数，str
    """
    url = "https://www.tmall.com"
    try:
        browser.get(url)
        assert "天猫" in browser.title
        input_keyword = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mq")))
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#mallSearch > form > fieldset > div > button")))
        # 输入搜索关键字
        input_keyword.send_keys(keyword)
        # 提交搜索
        submit.click()
        # 等待搜索加载出现页数元素
        total = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div/div[8]/div/b[2]/form/input[3]'))
        )
        # 获取商品信息
        get_page_products()
        # 返回页数元素的值
        return total.get_property("value")
    except TimeoutException:
        return search_keyword()
    except Exception as e:
        print("意外出错", e)


def auto_next_page(page_number):
    """
    到下一页
    :param page_number: 页数
    :return:
    """
    try:
        # 页码输入框
        input_page = wait.until(
            EC.presence_of_element_located((By.NAME, 'jumpto'))
        )
        # 页码提交按钮
        submit = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[8]/div/b[2]/form/button'))
        )
        now_page = int(input_page.get_property("value"))
        print("当前页数：", now_page)
        if now_page != page_number - 1:
            print("页码不对应")  # todo 页码数不对应的异常处理
        # 清除当前默认的页码数
        input_page.clear()
        input_page.send_keys(page_number)
        submit.click()
        get_page_products()
    except TimeoutException:
        print("翻页超时")
        deal_not_find_product_page()


def deal_not_find_product_page():
    try:
        nothing = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content > div > div.searchTip > h2"))
        )
        # print(nothing.text)
        assert "喵~没找到" in nothing.text
    except TimeoutException:
        pass
    except AssertionError:
        pass
    else:
        print(nothing.text)
        browser.quit()


def get_page_products():
    """
    获取当前页面的商品
    :return:
    """
    import traceback
    try:
        # 判断加载商品完成
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_ItemList  .product   .product-iWrap"))
        )
        # pyquery分析html源码
        pq = PQ(browser.page_source)
        items = pq('#J_ItemList  .product   .product-iWrap').items()
        for item in items:
            # 处理商品中的广告位置
            if item.find('.productAlbum'):
                print("非商品-广告图片")
                continue
            product = {
                "productPrice": item.find(".productPrice").text()[1:],
                "productTitle": item.find('.productTitle').text(),
                "productShop": item.find('.productShop-name').text(),
                "productStatus": item.find('.productStatus').text()[6:-1],
                "productImage": item.find('.productImg-wrap > a > img').attr('src')
            }
            # print(product)
            save_to_mongo(product)
    except TimeoutException:
        print("获取当前页面的商品超时")
    except Exception as e:
        traceback.print_exc()


def save_to_mongo(product):
    if db[MONOGO_TABLE].insert(product):
        print("保存到mongodb成功", product)
    else:
        print("保存失败")


def run_main():
    try:
        pages_number = search_keyword()
        print("总页数：", pages_number)
        if isinstance(pages_number, str):
            pages_number = int(pages_number)
        for page_number in range(2, pages_number + 1):
            auto_next_page(page_number)
    except ConnectionError:
        pass
    except Exception as e:
        pass
    finally:
        browser.quit()


if __name__ == "__main__":
    run_main()
