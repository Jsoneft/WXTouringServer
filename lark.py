import time
import os
from lxml import etree
import requests
head = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    }

class Message():

    def __init__(self, userInfo):
        self.sendMessage = []
        self.headArticle(userInfo)
        # self.Articles = etree.Element("Articles")
        # self.item = etree.SubElement(self.Articles, "item")
        # self.append_Description("Title", userInfo.find("Content").text)

    def append_Description(self, key: str, value):
        self.sendMessage.append({key:value})

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
                elif isinstance(data, list):
                    for value in data:
                        self.create_xml(value, element)
                else:
                    # if isinstance(data, int):
                    #     element.text = str(data)
                    # else:
                    element.text = etree.CDATA(str(data))

        if isinstance(xmlValue, list):
            for value in xmlValue:
                self.create_xml(value, headElement)

        if flag:
            xmlText = etree.tostring(headElement, encoding="utf-8", pretty_print=True).decode("utf-8")
            return xmlText.rstrip("\n")

    def headArticle(self, userInfo):
        headDic = {
            "ToUserName": userInfo.find("FromUserName").text,
            "FromUserName": userInfo.find("ToUserName").text,
            "CreateTime": int(time.time())
        }
        self.sendMessage.append(headDic)

    def MsgType(self,type:str):
        self.sendMessage.append({"MsgType":type})

    def generateMessage(self):
        try:
            return self.create_xml(self.sendMessage)
        except:
            return ""

    def send_WXpic(self,picByte):
        param = {
            "access_token":self.get_accessToken(),
            "type":"image"
        }
        with open("/tmp/WXtempIMG.jpg","wb") as f:
            f.write(picByte)
        response = requests.post("http://file.api.weixin.qq.com/cgi-bin/media/upload",params = param,files={"p_w_picpath":open("/tmp/WXtempIMG.jpg","rb")})
        resJson = response.json()
        try:
            return resJson["media_id"]
        except:
            try:
                print(resJson["errmsg"])
                return ""
            except:
                print("POST getPicId Faild")
                return ""



    def get_accessToken(self):
        if os.path.isfile("WXaccessToken.txt"):
            last_tokenTime = os.path.getmtime("WXaccessToken.txt")
            now_time = time.time()
            if now_time-last_tokenTime>7100:
                if not self.send_client_credential():
                    return ""
        else:
            if not self.send_client_credential():
                return ""
        with open("WXaccessToken.txt","r") as f:
            access_token = f.read()
        return access_token


    def send_client_credential(self):
        if os.path.isfile("WXaccessSecret.txt"):
            with open("WXaccessSecret.txt", "r") as f:
                secert = f.read()
        param = {
            "grant_type": "client_credential",
            "appid": "wxef446a2455cef80c",
            "secret": secert
        }
        responseAPI = requests.get("https://api.weixin.qq.com/cgi-bin/token", params=param)
        tokenJson = responseAPI.json()
        try:
            access_token = tokenJson["access_token"]
            with open("WXaccessToken.txt", "w") as f:
                f.write(access_token)
                f.close()
            return True
        except:
            try:
                errmsg = tokenJson["errmsg"]
                print(errmsg)
                return False
            except:
                print("GET access_token FROM WX faild")
                return False
