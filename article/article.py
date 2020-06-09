import time

from lxml import etree


class Article():

    def __init__(self, userInfo):
        self.sendMessage = []
        self.headArticle(userInfo)
        self.Articles = etree.Element("Articles")
        self.item = etree.SubElement(self.Articles, "item")
        self.append_Description("Title", userInfo.find("Content").text)

    def append_Description(self, key: str, value: str):
        description = etree.SubElement(self.item, str(key))
        description.text = etree.CDATA(str(value))

    def create_xml(self, xmlValue, headElement=None):
        if headElement is None:
            headElement = etree.Element("xml")
            flag = True
        else:
            flag = False

        if isinstance(xmlValue, dict):
            for key, data in xmlValue.items():
                element = etree.SubElement(headElement, str(key))
                if isinstance(data, dict):
                    self.create_xml(data, element)
                else:
                    if isinstance(data, int):
                        element.text = str(data)
                    else:
                        element.text = etree.CDATA(str(data))

        if isinstance(xmlValue, list):
            for value in xmlValue:
                self.create_xml(value, headElement)

        if flag:
            headElement.append(self.Articles)
            xmlText = etree.tostring(headElement, encoding="utf-8", pretty_print=True).decode("utf-8")
            return xmlText.rstrip("\n")

    def headArticle(self, userInfo):
        headDic = {
            "ToUserName": userInfo.find("FromUserName").text,
            "FromUserName": userInfo.find("ToUserName").text,
            "CreateTime": int(time.time()),
            "MsgType": "news",
            "ArticleCount": 1
        }
        self.sendMessage.append(headDic)

    def generateArticle(self):
        try:
            return self.create_xml(self.sendMessage)
        except:
            return ""