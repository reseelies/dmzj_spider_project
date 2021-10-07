import os
import random
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


# 创建一个函数验证路径是否存在，不存在就创建，存在就不健
def Make_Dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

        
# 从漫画主页提取所需信息，包括名称、每一章地址、名称，以字典形式返回
def get_info(url, header):
    dic_t = {}
    dic_t["title"] = []
    dic_t["href"] = []
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    soup = bs(r.text, "html.parser")
    dic_t["name"] = soup.find("h1").string
    cartoon_online_borders = soup.find_all("div", {"class":"cartoon_online_border"})
    cartoon_online_border_other = soup.find("div", {"class":"cartoon_online_border_other"})
    if cartoon_online_border_other != None:
        a_n = eval(input("下载那一部分？(0为每一话的版本，1为单行本版本)"))
        if a_n == 0:
            for cartoon_online_border in cartoon_online_borders:
                for a in cartoon_online_border.find_all('a'):
                    dic_t["title"].append(a.attrs["title"])
                    dic_t["href"].append(a.attrs["href"])
        elif a_n == 1:
            for a in cartoon_online_border_other.find_all('a'):
                dic_t["title"].append(a.attrs["title"])
                dic_t["href"].append(a.attrs["href"])
    else:
        for cartoon_online_border in cartoon_online_borders:
            for a in cartoon_online_border.find_all('a'):
                dic_t["title"].append(a.attrs["title"])
                dic_t["href"].append(a.attrs["href"])
    return dic_t


def get_cpt(url, path, header):
    urls = []
    # 下面这段代码是不让模拟浏览器显示出来的
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options = chrome_options)

    driver.get(url)
    html = driver.page_source
    soup = bs(html, "html.parser")
    driver.close()
    select = soup.find("select")
    options = select.find_all("option")
    for option in options:
        urls.append("https:" + option.attrs["value"])
    page = len(urls)
    for i, url_img in enumerate(urls):
        sleep = random.randint(1,3) + random.random()
        time.sleep(sleep)
        img = requests.get(url_img, headers = header)
#         name = url_img.split('/')[-1]
        name = "{:0>3d}.".format(i + 1) + url_img.split('.')[-1]
        with open(path + '/' + name, "wb") as fo:
            fo.write(img.content)
    return page


def main(url_h):
    pages = 0
    start = time.time()
    header1 = {"Host":"manhua.dmzj.com", 
              "User-Agent":"""Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
              AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"""}
    header2 = {"Referer":"https://manhua.dmzj.com/", 
              "User-Agent":"""Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
              AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"""}
    dic_home = get_info(url_h, header1) 
    start_chapt = eval(input("请输入爬取的开始章节数(从0开始)："))
    end_chapt = eval(input("请输入爬取的结束章节数(输入0表示后续全部)："))
    if end_chapt == 0:
        href_ls = dic_home["href"][start_chapt:]
    else:
        href_ls = dic_home["href"][start_chapt:end_chapt]
    plus = int(input("请输入开始序号(无特殊需求请输入0)："))
    b = input("爬取章节为：{} - {}，是否爬取？(y/n)".format(dic_home["title"][start_chapt], dic_home["title"][end_chapt - 1]))
    if b == 'n':
        exit(0)
    Make_Dir("./{}".format(dic_home["name"]))  # 创建漫画名的文件夹
    # 这里用for循环提取每一章漫画所有的图片
    for i, url in enumerate(href_ls, start = plus):
        path = "./{}/{:0>3d}.{}".format(dic_home["name"], i, dic_home["title"][start_chapt + i - plus])
        try:
            Make_Dir(path)
            pages += get_cpt("https://manhua.dmzj.com" + url + "#@page=1", path, header2)
        except:
            print(dic_home["title"][start_chapt + i - plus], "爬取失败")
        else:
            print(dic_home["title"][start_chapt + i - plus], "Done")
        time.sleep(5)

    end = time.time()
    print("{} 爬取完成，共{}页，用时{:.2f}s".format(dic_home["name"], pages, end - start))
    input("按回车键退出……")


url = input("请输入漫画地址： ")
main(url)
