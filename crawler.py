import os
import re
import requests
import logging
import threading
import time

# 设置爬虫的headers
head = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}
# 给threading添加锁
lock = threading.Lock()
# 所获取的图片Bytes列表
pic_contents = []


def get_pix_content(page_url: str):
    """
    获取图片大图的content二进制
    :param page_url: 搜索出来的图片的页面信息
    :return: None
    """
    try:
        # 获取全局变量：lock锁
        global lock
        # 获取图片的页面信息
        request = requests.get(page_url, headers=head, timeout=0.5)
        # 提取出图片的大图链接
        pic_url = re.search(r'<img class="biaoqingpp" src="(.*?)"', request.text).group(1)
        # 获得图片的二进制
        image = requests.get(pic_url, headers=head, timeout=2)
        # 使用线程锁锁住picBytes，防止其他线程对其处理
        if lock.acquire():
            logging.debug(f"img_url: {image.url}")
            pic_contents.append(image)
        lock.release()
    except:
        return None


def get_pix_by_key(key: str, GET_PIC_NUM=1):
    """
    主要函数，获取图片的二进制列表。
    :param key: A string describing the image to be searched
    :return: Image cache path
    """
    # 通过target目标网站获取图像的目标地址，获得图像的关键信息
    target_url = "https://fabiaoqing.com/search/search/keyword/{}".format(key)

    # 发送
    response = requests.get(target_url, headers=head)
    imgs = []
    # 处理内容，获得图片的url地址
    img_tags = re.findall(r'<a href="/biaoqing/detail/id/(.*?)>', response.text)
    # 对图片的tag添加
    for img_tag in img_tags[0:GET_PIC_NUM]:
        img_title = re.search(r'title="(.*?)"', img_tag).group(1)
        img_id = re.match(r'\d+', img_tag).group(0)
        imgs.append({"Title": img_title, "Id": img_id})
    # 图片网页模板 (https://fabiaoqing.com/biaoqing/detail/id/375460.html)
    page_TemplateUrl = "https://fabiaoqing.com/biaoqing/detail/id/{}.html"

    # 获得全局的图片Bytes数组
    global pic_contents
    pic_contents = []
    # 用于管理线程
    threadCount = []

    # 获取图片
    for img in imgs:
        # 通过模板添加图片页面的url
        page_url = page_TemplateUrl.format(img.get("Id", "0"))
        # 创建多线程任务
        crawl = threading.Thread(target=get_pix_content, args=(page_url,))
        # 启动线程
        crawl.start()
        # 将线程对象添加到列表中
        threadCount.append(crawl)

    count = 0
    # 对线程堵塞，防止线程提前结束
    for thr in threadCount:
        thr.join()
    if not pic_contents:
        return None
    else:
        return pic_contents
