import os
import re
import requests

head = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    }

picBytes = []

def get_pix_url(page_url:str):
    try:
        global pic_urls
        request = requests.get(page_url, headers=head)
        pic_url = re.search(r'<img class="biaoqingpp" src="(.*?)"', request.text).group(1)
        image = requests.get(pic_url, headers=head)

        picBytes.append(image.content)

    except:
        return None

def get_pix_by_key(key:str, GET_PIC_NUM=1):
    """
    :param key: A string describing the image to be searched
    :return: Image cache path
    """
    target_url = "https://fabiaoqing.com/search/search/keyword/{}".format(key)

    response = requests.get(target_url, headers=head)
    imgs = []
    img_tags = re.findall(r'<a href="/biaoqing/detail/id/(.*?)>', response.text)
    for img_tag in img_tags[0:GET_PIC_NUM]:
        img_title = re.search(r'title="(.*?)"', img_tag).group(1)
        img_id = re.match(r'\d+', img_tag).group(0)
        imgs.append({"Title": img_title, "Id": img_id})
    # 图片网页模板 (https://fabiaoqing.com/biaoqing/detail/id/375460.html)
    page_TemplateUrl = "https://fabiaoqing.com/biaoqing/detail/id/{}.html"

    global picBytes
    picBytes = []
    # threadCount = []

    # for img in imgs:
    #     page_url = page_TemplateUrl.format(img.get("Id","0"))
    #     crawl = threading.Thread(target=get_pix_url, args=(page_url,))
    #     crawl.start()
    #     threadCount.append(crawl)
    # for i in range(len(imgs)):
    #     threadCount[i].join()
    page_url = page_TemplateUrl.format(imgs[0].get("Id","0"))
    get_pix_url(page_url)
    return picBytes
