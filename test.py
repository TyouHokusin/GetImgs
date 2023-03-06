# -*- coding:utf-8 -*-
# Author:Zhang Beichen

import requests
import time
import urllib
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import os
import re

USERNAME = ""
PASSWORD = ""
URL = ""
save_path = ""
#%%
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


#%%
class ImageDownloader:
    def __init__(self, img_num=20, path="D:\\img"):
        self.img_num = img_num
        self.path = path

    """
    def download_img(self,img_url,item):
        #print (img_url)
        
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'\
                             ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'} # 
        r = requests.get(img_url, headers=header, stream=True)
        #print(r.status_code) 
        if r.status_code == 200:
            open(self.path+item, 'wb').write(r.content) 
            print("done")
        del r
    """

    def get_html(self, item):
        url = URL + item + "&s=" + str(48)
        html = urllib.request.urlopen(url)
        return html

    def login(self, browser):
        url = URL + urllib.parse.quote("item") + "&s=" + str(48)

        wait = WebDriverWait(browser, 5)
        browser.get(url)
        browser.find_element_by_id("fm-login-id").send_keys(USERNAME)
        browser.find_element_by_id("fm-login-password").send_keys(PASSWORD)
        browser.find_element_by_class_name("fm-btn").click()
        try:
            slidebar = wait.until(
                lambda browser: browser.find_element_by_xpath('//*[@id="nc_1_n1z"]')
            )
            # browser.find_element_by_xpath('//*[@id="nc_1_n1z"]')
            webdriver.ActionChains(browser).click_and_hold(slidebar).perform()
            webdriver.ActionChains(browser).move_by_offset(
                xoffset=290, yoffset=0
            ).perform()
            webdriver.ActionChains(browser).release().perform()
        except:
            print("fail in slide bar")
        browser.find_element_by_class_name("fm-btn").click()
        browser.implicitly_wait(10)
        wait.until_not(lambda browser: browser.find_element_by_class_name("fm-btn"))
        print("login success")

    def get_img_urls(self, browser, item):
        url = URL + urllib.parse.quote(item) + "&s=" + str(48)
        browser.get(url)
        browser.implicitly_wait(10)

        html = browser.page_source
        bs = BeautifulSoup(html, "html.parser")
        # print(bs)
        img_tags = bs.find_all(
            attrs={"data-src": re.compile("\.jpg")}, limit=self.img_num
        )
        price_tags = bs.find_all(
            "div", {"class": "price g_price g_price-highlight"}, limit=self.img_num
        )
        sale_tags = bs.find_all("div", {"class": "deal-cnt"}, limit=self.img_num)
        shop_tags = bs.find_all(
            "a", {"class": "shopname J_MouseEneterLeave J_ShopInfo"}, limit=self.img_num
        )
        if len(img_tags) < self.img_num:
            print("imgs not enough")

        img_urls = []
        names = []
        prices = []
        sales = []
        shops = []
        for img_tag, price_tag, sale_tag, shop_tag in zip(
            img_tags, price_tags, sale_tags, shop_tags
        ):
            img_urls.append(img_tag.get("data-src"))
            names.append(img_tag.get("alt"))
            prices.append(float(price_tag.strong.get_text()))
            sales.append(float(re.findall(r"\d+\.?\d*", sale_tag.get_text())[0]))
            shops.append(shop_tag.find_all("span")[-1].get_text())
        return img_urls, names, prices, sales, shops

    def download_imgs(
        self, items, properties=["image", "name", "price", "sales", "shop"]
    ):
        browser = webdriver.Chrome()
        try:
            self.login(browser)
        except:
            print("login failed")
        for item in items:
            img_urls, names, prices, sales, shops = self.get_img_urls(browser, item)
            try:
                os.makedirs(save_path + item)
            except:
                print("already exist")
            for i, img_url in enumerate(img_urls):
                urllib.request.urlretrieve(
                    "http:" + img_url, save_path + item + "//img" + str(i) + ".jpg",
                )
        return names, prices, sales, shops


#%%
if __name__ == "__main__":
    a = ImageDownloader(img_num=20)
    img_list = ["iphone10"]
    a.download_imgs(img_list)

