# coding: utf-8
"""
time: 2019-4-4
function: 爬取漫画
user: 五根弦的吉他
"""
import requests
from multiprocessing.pool import Pool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote,urlencode
import time, random, os
from retry import retry
from fake_useragent import UserAgent
from lxml import etree
from datetime import datetime

os.environ['no_proxies'] = '*'
keyword = '妖怪名单'
BASE_URL = 'http://www.chuixue.net'
headers = {'User-Agent': UserAgent().random}

# ip代理池接口
def get_proxy():
    try:
        response = requests.get(url='http://127.0.0.1:5010/get/')
        if response.status_code == 200:
            return response.text              # 直接返回一个proxy
    except ConnectionError:
        return None


def search_manhua():
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)
    browser.get(url=BASE_URL)
    # print(browser.page_source)

    input = browser.find_element_by_xpath('//input[@id="txtKey"]')
    input.clear()
    input.send_keys(keyword)
    time.sleep(1)
    button = browser.find_element_by_id('btnSend')
    button.click()
    # 判断是否跳转成功
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'span a.on'), str('点击次数')))
    # 找到目标漫画链接（在网页里看到的是只有一半链接，但是打印出来是全部的, 下面用requests的话又只能打印一半了）
    link = browser.find_element_by_xpath("//div[@id='dmList']//a[@class='pic']").get_attribute('href')
    print(link)
    # 关闭浏览器
    browser.quit()

    return link


def get_chapter(url):
    response = requests.get(url=url, headers=headers)
    #response.encoding='utf-8'
    #html = etree.parse(str(response.text), etree.HTMLParser())
    html = etree.HTML(response.content)
    response.close()
    chapter_list = html.xpath('//div[@id="play_0"]//li/a/@href')
    chaper_title = html.xpath('//div[@id="play_0"]//li/a/@title')
    for i in range(len(chaper_title)):
        chapter = {
            'title': chaper_title[len(chaper_title)-i-1],
            'chapter_link': BASE_URL+chapter_list[len(chapter_list)-i-1]
        }
        yield chapter

@retry( delay=1, backoff=2)
def save_chapter(item):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--proxy-server=http://' + get_proxy())  # selenium使用代理
        browser = webdriver.Chrome(chrome_options=options)
        wait = WebDriverWait(browser, 15)

        browser.get(url=item['chapter_link'])

        html = etree.HTML(browser.page_source)

        # 隐式等待
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#selectpage2')))
        page_num_list = html.xpath('//span[@id="selectpage2"]//option')
        time.sleep(1)

        return browser, wait, page_num_list
    except Exception:
        browser.quit()


@retry( delay=1, backoff=2)
def get_response_from_pic(url, headers, proxies, timeout):
    response = requests.get(url=url, headers=headers,
                             proxies=proxies,
                             timeout=timeout)
    return response


def download(dir, index, response):
    if not os.path.exists(dir + '/{}.jpg'.format(index + 1)):
        with open(dir + '/{}.jpg'.format(index + 1), 'wb') as f:
            f.write(response.content)
            print('已保存第%s张图片' % (index + 1))
            response.close()
    else:print("已存在{}".format(dir + '/{}.jpg'.format(index + 1)))


def get_pic(item):
    # for item in get_chapter(url):
    print("开始保存 {} 章节".format(item['title']))
    dir = './'+keyword + '/' + item['title']
    if not os.path.exists(dir):
        os.makedirs(dir)

    browser, wait, page_num_list = save_chapter(item)
    # 切换选项卡
    browser.execute_script('window.open()')
    browser.switch_to.window(browser.window_handles[1])
    # 构造每页的url
    url_list = []
    for each in range(len(page_num_list)):
        url_list.append(item['chapter_link']+'?page={}'.format(each+1))
    for index, link in enumerate(url_list):

        browser.get(url=link)

        # 模拟下拉操作
        browser.execute_script('window.scrollTo(0,200)')

        html2 = etree.HTML(browser.page_source)
        # 隐式等待
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#viewimages img')))
        imgsrc = html2.xpath('//div[@id="viewimages"]/img[1]/@src')
        print('imgsrc:', imgsrc)

        time.sleep(1)

        # 请求图片数据

        response3 = get_response_from_pic(imgsrc[0], headers=headers,
                              proxies={'http': 'http://' + get_proxy(), 'https': 'https//' + get_proxy()},
                              timeout=20)

        # 写入文件
        download(dir, index, response3)
        time.sleep(1)
    # 关闭浏览器
    browser.quit()
    #browser.switch_to.window(browser.window_handles[0])
    print("{}章节已爬取结束".format(item['title'])+'\n'+'='*50+'\n')


if __name__ == '__main__':
    start = datetime.now()
    # 获取proxy
    proxy = 'http://' + get_proxy()
    pool = Pool()

    link = search_manhua()
    # list = list(get_chapter(link))
    aux = [item for item in get_chapter(link)]

    pool.map(get_pic, aux)

    pool.close()
    pool.join()
    end = datetime.now()
    print("DONE!Duration:", end-start)
