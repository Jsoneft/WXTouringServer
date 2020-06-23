import json
import logging
import time
import bot
import requests
from hashlib import sha1, md5
from lxml import etree

# 设置日志格式
LOG_FORMAT = "%(asctime)s - %(funcName)s - %(processName)s - %(thread)s	 - %(message)s - %(msecs)d"
# 设置日志的时间格式
DATE_FORMAT = "%Y/%m/%d %H:%M:%S %p"
# 设置日志的输出等级.调试时为DEBUG
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

# 微信公众号的TOKEN，相当于微信的校验信息
TOKEN = "weixingongzhonghao"
EncodingAESKey = "UaohLPWNrrgCfIQvgBGWLZnCrpAktoNF3jhue6SVgLW"


# 处理C++发来的request
class MYRequestHandler:
    # https://blog.csdn.net/themagickeyjianan/article/details/53736445
    disable_nagle_algorithm = True
    protocol_version = 'HTTP/1.1'

    # 图灵机器人接口设置
    TouringID = "4fd840e39b5a4ca8950a5c956e77dab7"
    TouringInterface = "http://openapi.tuling123.com/openapi/api/v2"

    param = {}
    head = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    }
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": ""
            }
        },
        "userInfo": {
            "apiKey": TouringID,
            "userId": ""
        }
    }

    def __init__(self):
        """
                初始化
        """
        pass

    def getParams(self, key):
        """
                获取param内的参数
                :param key:关键词
                :return:参数
        """
        # 尝试根据关键词获取参数
        try:
            return self.param[key]
        except:
            # 失败返回None
            return None

    def saveParams(self):
        """
        处理链接的param
        :return:None
        """
        # 提取链接的param
        try:
            # 循环获取param
            # 获取链接？后的内容，并通过&符号分割
            for parameter in self.path.split("?")[1].split("&"):
                dic = parameter.split("=")
                self.param[dic[0]] = dic[1]
        except:
            # 如果没有param，返回空
            self.param = {}

    def checkSignature(self):
        """
        检查发送的http请求来自微信服务器
        :return: True/False
        """
        self.saveParams()
        try:
            # 提取参数进行校验
            signature = self.getParams("signature")
            timestamp = self.getParams("timestamp")
            nonce = self.getParams("nonce")
            _ = self.getParams("echostr")
            token = TOKEN
            TemporaryList = {token, timestamp, nonce}
            TemporaryList = sorted(TemporaryList)
        except:
            return False

        logging.debug(f"[MyHandler.checkSignature] TemporaryList = {TemporaryList}")
        TemporaryStr = "".join(TemporaryList)
        # 对信息进行sha1检验
        TemporaryStr = sha1(TemporaryStr.encode('utf-8')).hexdigest()
        logging.debug(f"[MyHandler.checkSignature] TemporaryStr = {TemporaryStr}")
        # 返回校验信息是否成立
        return signature == TemporaryStr

    def handle_one_request(self, buffer: str):
        logging.debug(f"[handle_one_request] buf {buffer}")
        # 将客户端发送的http报文进行分割
        self.raw_requestlines = buffer.split('\r\n')
        print(self.raw_requestlines)
        # 如果没有分割，或发送的消息为空
        if not self.raw_requestlines:
            # print("[MYRequestHandler.handle_one_request] 读入失败")
            logging.debug(f"[MYRequestHandler.handle_one_request] 读入失败")
            # 返回错误代码400
            return self.Response("", 400, "BadRequest")
        # raw_requestline = b'GET / HTTP/1.1\r\n'
        # 执行提取request头部信息
        if not self.parse_request():
            # 如果parse_request失败，表示可能收到的内容不是http请求，返回400
            return self.Response("", 400, "BadRequest")

        # 添加要处理的GET/POST请求
        mname = 'do_' + self.command
        # 检查类中是否有对应的处理方法，即do_GET,do_POST
        if not hasattr(self, mname):
            # print(["[MYRequestHandler.handle_one_request] 没有实现 {}方法".format(mname)])
            logging.debug(f"[MYRequestHandler.handle_one_request] 没有实现 {mname}方法")
            return self.Response("", 400, "BadRequest")

        # 进行微信校验，表示这个信息确实是微信发送的
        if not self.checkSignature():
            return self.Response("", 200, "OK")

        # 调用对应的函数
        # 如：do_GET,则调用do_GET方法
        method = getattr(self, mname)
        # 执行该方法
        return method()

    def parse_request(self):
        """
            The request should be stored in self.raw_requestline;
            the results are in self.command, self.path, self.request_version and
            self.headers.
            return：None
        """
        # raw_requestline = b'GET / HTTP/1.1\r\n'
        # 将http报文的头部提取出来
        requestline = self.raw_requestlines.pop(0)
        # https://baike.baidu.com/item/ISO-8859-1/7878872?fr=aladdin
        # requestline = 'GET / HTTP/1.1\r\n'
        # 去除右边的\r\n
        requestline = requestline.rstrip('\r\n')
        # requestline = 'GET / HTTP/1.1'
        # 按空格分割信息
        words = requestline.split()
        # words = ['GET', '/', 'HTTP/1.1']

        # 如果获取到的words数量不足，那么这个链接有可能就不是http的报文，那我我们就退出
        if len(words) <= 2:
            # print("[MYRequestHandler. parse_request] Bad request syntax, requestline : {} ".format(requestline))
            logging.debug(f"[MYRequestHandler. parse_request] Bad request syntax, requestline : {requestline} ")
            return False

        # 获得HTTP的Version
        version = words[-1]
        # 检测是否是http，排除https
        # 原因：
        # 1。http简单，没有https需要证书
        if not version.startswith('HTTP/'):
            # print("[MYRequestHandler. parse_request] Bad request syntax, requestline : {} ".format(requestline))
            logging.debug(f"[MYRequestHandler. parse_request] Bad request syntax, requestline : {requestline} ")
            return False
        # 将信息传入给类
        self.version = version
        self.command, self.path = words[:2]

        # 将http报文的头部中所包含的headers提取出来
        headers = []
        try:
            while True:
                # pop(0)即从首部提取
                line = self.raw_requestlines.pop(0)
                headers.append(line)
                if line in ('', '\r\n', '\n'):
                    break
        except:
            return False

        hstring = ''.join(headers)
        # 'Host: 10.254.147.98:5000
        # User-Agent: Go-http-client/1.1
        # Content-Length: 391
        # Content-Type: application/json;charset=utf-8
        # X-Request-Id: dafc4560-a66a-4013-9fb2-7cad38f96250
        # Accept-Encoding: gzip
        #
        # body

        # 进一步完善headers
        headers_lines = hstring.split('\r\n')
        # 将headers从str转化为字典格式
        self.headers = {}

        for line in headers_lines:
            key_val = line.split(': ')
            if key_val[0] != '':
                self.headers[key_val[0]] = key_val[1]
        return True

    def create_xml(self, xmlDict: dict):
        """
        通过dict创建xml树，返回pretty_print后的xml格式的字符串
        :param xmlDict: 需要转化的字典
        :return: str
        """
        # 创建头节点（xml）
        xml = etree.Element("xml")
        # 添加子节点
        for key, data in xmlDict.items():
            element = etree.SubElement(xml, str(key))
            element.text = etree.CDATA(str(data))
        # 将xml树转化为str类型
        xmlSTR = etree.tostring(xml, encoding="utf-8", pretty_print=True).decode("utf-8")

        # 返回pretty_print后的xml格式的字符串
        return xmlSTR

    def normal_headers(self, code, message, dic=None):
        '''
            创建一般报文头部.
            :param code:状态码
            :param message:信息
            :return:返回报文的头部
        '''

        self._headers_buffer = []
        # 添加headers
        self._headers_buffer.append(("%s %d %s\r\n" %
                                     (self.protocol_version, code, message)))

        # 添加额外的头部信息，服务器名称
        self.dict_header("Server", "Zjx_HttpServer")
        # 添加额外的头部信息，时间戳
        self.dict_header("Date", time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))

        # 添加其他的额外头部信息
        if type(dic) == "dict":
            for key, value in dic.items():
                self.dict_header(key, value)
        # 为消息尾部添加\r\n，换行，表示接下来是body信息
        self._headers_buffer.append("\r\n")

        # 将消息整合，从list转化为str
        return "".join(self._headers_buffer)

    def dict_header(self, keyword, value):
        '''
            通过key,value创建报文.
            :param keyword:关键词
            :param value:信息
            :return:str
        '''
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        self._headers_buffer.append(
            ("%s: %s\r\n" % (keyword, value)))

    def Response(self, body="", code=200, message="OK"):
        """
        返回内容的格式
        默认返回200，其中body为微信所需要的xml格式信息
        :param body: 发送消息的内容
        :param code: 状态码，默认为200，如果出错，则根据情况调整
        :param message:
        :return:
        """
        dic = {'Content-Type': 'text/xml'}
        headersText = self.normal_headers(code, message, dic)
        sendMes = headersText + body
        return sendMes

    def do_GET(self):
        """
        微信服务器的GET请求为一开始检验服务器的
        后续不常用
        :return:微信服务器校验需求信息
        """
        EchoStr = self.getParams("echostr")
        return self.Response(body=EchoStr)

    def do_POST(self):
        """
        处理主要的用户发送的信息
        :return: xml信息或空字符串（表示处理失败）
        """
        # 因为之前的paser_request将信息处理了，pop完首部，剩下即是body部分
        XmlText = "".join(self.raw_requestlines)

        # 通过etre，解析xml，并建立xml树
        userInfo = etree.XML(XmlText)

        # 获取用户发送的信息类型
        # 1。text文本
        # 2。image图像
        cli_type = userInfo.find("MsgType").text
        logging.debug(f"[do_post] cli_type = {cli_type}")

        # 如果用户发送的消息为text格式
        if cli_type == "text":
            # 判断是否为特殊的信息
            # 是：返回xml的字符串
            # 否：执行图灵机器人
            ret = bot.do_specialText(userInfo)

            # 判断特殊信息是否执行
            if ret != "":
                return self.Response(ret)
            # 如果没有包含特殊信息
            # 调用图灵接口
            ret_text = self.send_to_Turing(userInfo.find("Content").text)

            # 需要发送到微信接口的xml信息
            dataDict = {
                "ToUserName": self.getParams("openid"),
                "FromUserName": userInfo.find("ToUserName").text,
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": ret_text,
            }

            # 将dict格式的xml信息转化为str类型
            data = self.create_xml(dataDict)
            # 发送信息
            return self.Response(data)

    def send_to_Turing(self, msg_from_cli: str):
        """
        调用图灵接口，获得图灵返回的信息
        :param msg_from_cli: 用户发送的信息和用户名称
        :return: 图灵机器人发送的信息
        """
        logging.debug(f"[send_to_Turing] msg = {msg_from_cli}")

        # 将用户名称通过hash的md5转化为一串标准的，不含特殊字符的字符串
        # 同时做到了隐藏用户信息的目的
        # 使用用户名称可以做到图灵机器人的学习功能
        encrypt_openID = md5(self.param["openid"].encode('utf-8')).hexdigest()
        logging.debug(f"[send_to_Turing] encrypt_openID = {encrypt_openID}")

        # 将用户信息添加到data中
        self.data["perception"]["inputText"]["text"] = msg_from_cli
        self.data["userInfo"]["userId"] = encrypt_openID
        logging.debug(f"[send_to_Turing] data = {self.data}")

        # 将信息发送给图灵机器人对应的API当中
        req = requests.post(self.TouringInterface, json=self.data, headers=self.headers)

        # 处理图灵机器人的API返回JSON格式信息
        TouringRSP = json.loads(req.text)
        logging.debug(f"[MyHandler.send_to_Turing] send_to_Turing = {req.text}")

        # 尝试对JSON信息提取
        try:
            TouringText = TouringRSP["results"][0]["values"]["text"]
            return TouringText
        except:
            # 提取失败
            return "TouringBUUUUG!!!"


handle = MYRequestHandler()


def handleRequest(buffer: str):
    """
    处理c++发送过来的字符串
    :param buffer: 传入参数为c++所接收到客服端的参数
    :return: 发送给客户端的信息
    """
    # 调用类中的函数
    sendMes = str(handle.handle_one_request(buffer))
    print(sendMes)
    # 返回需要发送给客户端的信息
    return sendMes
