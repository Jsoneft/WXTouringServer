import time
import os
from lxml import etree
import requests

# 设置发送给微信服务器的头部
head = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/80.0.3987.163 Safari/537.36 "
}

class Message():

    def __init__(self, userInfo):
        """
        初始化Message
        :param userInfo:传入用户信息，用于定向发送信息
        """
        self.sendMessage = []
        self.headArticle(userInfo)
        # self.Articles = etree.Element("Articles")
        # self.item = etree.SubElement(self.Articles, "item")
        # self.append_Description("Title", userInfo.find("Content").text)

    def append_Description(self, key: str, value):
        """
        在xml的回复信息中追加语句
        :param key: 回复信息类型
        :param value: 值
        :return: None
        """
        # 在sendMessage中追加一个字典
        # 使用dict
        # 1。防止出现关键字重复被覆盖
        # 2。dict的key，value对于createXML来说重用性更好
        self.sendMessage.append({key:value})

    def create_xml(self, xmlValue, headElement=None):
        """
        创建xml树，传入的标签需要为dict格式，
        可以用list来传入多个dict，可以相互
        嵌套，使得它的格式支持更多。
        :param xmlValue:
        :param headElement:
        :return:
        """
        # 判断是否有头部element，没有则创建根头部
        if headElement is None:
            headElement = etree.Element("xml")
            # 用来判断当前是否为主create_xml
            flag = True
        else:
            flag = False

        # 如果传入的为dict类型
        if isinstance(xmlValue, dict):

            # 提取dict的key与value，将其添加至element之中
            for key, data in xmlValue.items():
                # 创建一个关于key的element
                element = etree.SubElement(headElement, str(key))
                # 判断其中是否包含套娃dict或list
                if isinstance(data, dict):
                    # data为dict，将element传入create_xml，此时key为根节点
                    self.create_xml(data, element)
                elif isinstance(data, list):
                    # data为list，分别获取，将element传入create_xml，此时key为根节点
                    for value in data:
                        self.create_xml(value, element)
                else:
                    if isinstance(data, int):
                        # 如果data为int，则不需要使用CDATA类型
                        element.text = str(data)
                    else:
                        # 使用CDATA，可以让文本兼容性更好
                        element.text = etree.CDATA(str(data))

        # data为list，分别获取，将element传入create_xml，此时headElement为根节点
        if isinstance(xmlValue, list):
            for value in xmlValue:
                self.create_xml(value, headElement)

        # 判断这个create_xml是否为主函数，如果是，返回str，不是则直接结束
        if flag:
            # 将etree打印出来转化为str，使用pretty_print使输出格式可读性高
            # 可以方便调试
            xmlText = etree.tostring(headElement, encoding="utf-8", pretty_print=True).decode("utf-8")
            return xmlText

    def headArticle(self, userInfo):
        """
        微信头部返回内容的建立
        :param userInfo: 用户的信息
        :return: None
        """
        # 根据微信的需求，完成对应通用的首部格式的制作
        headDic = {
            "ToUserName": userInfo.find("FromUserName").text,
            "FromUserName": userInfo.find("ToUserName").text,
            "CreateTime": int(time.time())
        }
        # 将其添加至sendMessage
        self.sendMessage.append(headDic)

    def MsgType(self,type: str):
        """
        制定发送的微信信息的格式
        :param type: 需要发送给用户的内容格式
        如：text为文本，image为图片
        :return: None
        """
        # 将其添加至sendMessage
        self.sendMessage.append({"MsgType":type})

    def generateMessage(self):
        """
        将sendMessage转化为字符串，如果出错这返回空
        :return: str
        """
        # 尝试创建xml，并获得返回的str
        try:
            return self.create_xml(self.sendMessage)
        except:
            # 失败返回空字符串
            return ""

    def send_WXpic(self,picByte):
        """
        将图片picByte发送给微信服务器
        :param picByte:bstr类型，需要发送到微信服务器的图片
        :return:微信的media_id
        """
        # 设置微信发送的参数
        param = {
            "access_token":self.get_accessToken(),
            "type":"image"
        }
        # 将图片临时存入缓存
        # 本地测试可以修改为自己的目录
        # "/tmp/WXtempIMG.jpg"为服务器所使用的临时目录
        with open("/tmp/WXtempIMG.jpg","wb") as f:
            f.write(picByte)
        response = requests.post("http://file.api.weixin.qq.com/cgi-bin/media/upload",params = param,files={"picpath":open("/tmp/WXtempIMG.jpg","rb")})
        # 将获取到的response解析为json
        resJson = response.json()

        # 尝试获取其中的media_id
        try:
            return resJson["media_id"]
        except:
            # 失败尝试获取错误信息
            try:
                print(resJson["errmsg"])
                return ""
            except:
                # 获取错误信息失败表示POST失败
                print("POST getPicId Faild")
                return ""



    def get_accessToken(self):
        """
        获取微信的accessToken
        :return: access_token：str
        """
        # 判断之前获得的微信accessToken是否存在
        if os.path.isfile("WXaccessToken.txt"):
            # 如果存在，判断他的创建时间
            last_tokenTime = os.path.getmtime("WXaccessToken.txt")
            # 现在时间
            now_time = time.time()
            # 通过比对，如果时间超过2h表示该迷失已经过期
            # 需要重新获取
            if now_time-last_tokenTime>7200:
                # 重新获取
                if not self.send_client_credential():
                    return ""
        else:
            # 如果没有之前的accessToken，则首先获得accessToken
            if not self.send_client_credential():
                return ""

        # 打开文件获得accessToken
        with open("WXaccessToken.txt","r") as f:
            access_token = f.read()

        #返回accessToken
        return access_token


    def send_client_credential(self):
        """
        想微信服务器发送请求，获得access_token
        :return: True/False
        """

        # 尝试打开文件，确认accessSecret密匙存在
        if os.path.isfile("WXaccessSecret.txt"):
            with open("WXaccessSecret.txt", "r") as f:
                secert = f.read()
        # 发送微信服务器的头部
        param = {
            "grant_type": "client_credential",
            "appid": "wxef446a2455cef80c",
            "secret": secert
        }
        # 获取微信服务器返回的JSON
        responseAPI = requests.get("https://api.weixin.qq.com/cgi-bin/token", params=param)

        # 对json进行解析
        tokenJson = responseAPI.json()

        # 尝试获取json的数据
        try:
            # 获取access_token
            access_token = tokenJson["access_token"]
            # 将其写入"WXaccessToken.txt"
            with open("WXaccessToken.txt", "w") as f:
                f.write(access_token)
                f.close()
            return True
        except:
            # 如果失败
            try:
                # 尝试获取errmsg
                errmsg = tokenJson["errmsg"]
                print(errmsg)
                return False
            except:
                # GET请求失败
                print("GET access_token FROM WX faild")
                return False