import json
import selectors
import socket
import logging
import time
import bot
import requests
from hashlib import sha1, md5
from lxml import etree

LOG_FORMAT = "%(asctime)s - %(funcName)s - %(processName)s - %(thread)s	 - %(message)s - %(msecs)d"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

TOKEN = "weixingongzhonghao"
EncodingAESKey = "UaohLPWNrrgCfIQvgBGWLZnCrpAktoNF3jhue6SVgLW"


class MYRequestHandler:
        disable_nagle_algorithm = True  # https://blog.csdn.net/themagickeyjianan/article/details/53736445
        protocol_version = 'HTTP/1.1'
        TouringID = "4fd840e39b5a4ca8950a5c956e77dab7"
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

        TouringInterface = "http://openapi.tuling123.com/openapi/api/v2"

        def __init__(self):
                pass

        def getParams(self, key):
                try:
                        return self.param[key]
                except:
                        return None

        def saveParams(self):
                try:
                        for parameter in self.path.split("?")[1].split("&"):
                                dic = parameter.split("=")
                                self.param[dic[0]] = dic[1]
                except:
                        self.param = {}

        def checkSignature(self):
                self.saveParams()
                try:
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
                TemporaryStr = sha1(TemporaryStr.encode('utf-8')).hexdigest()
                logging.debug(f"[MyHandler.checkSignature] TemporaryStr = {TemporaryStr}")

                return signature == TemporaryStr

        def handle_one_request(self, buffer: str):
                logging.debug(f"[handle_one_request] buf {buffer}")
                self.raw_requestlines = buffer.split('\r\n')
                print(self.raw_requestlines)
                if not self.raw_requestlines:
                        # print("[MYRequestHandler.handle_one_request] 读入失败")
                        logging.debug(f"[MYRequestHandler.handle_one_request] 读入失败")
                        return self.Response("", 400, "BadRequest")
                # raw_requestline = b'GET / HTTP/1.1\r\n'
                if not self.parse_request():
                        return self.Response("", 400, "BadRequest")

                mname = 'do_' + self.command
                if not hasattr(self, mname):
                        # print(["[MYRequestHandler.handle_one_request] 没有实现 {}方法".format(mname)])
                        logging.debug(f"[MYRequestHandler.handle_one_request] 没有实现 {mname}方法")
                        return self.Response("", 400, "BadRequest")

                if not self.checkSignature():
                        return self.Response("", 200, "OK")

                method = getattr(self, mname)
                return method()

        def parse_request(self):
                """
                        The request should be stored in self.raw_requestline;
                        The results are in self.command, self.path, self.request_version and
                        self.headers.
                        """
                # raw_requestline = b'GET / HTTP/1.1\r\n'
                requestline = self.raw_requestlines.pop(0)
                # https://baike.baidu.com/item/ISO-8859-1/7878872?fr=aladdin
                # requestline = 'GET / HTTP/1.1\r\n'
                requestline = requestline.rstrip('\r\n')
                # requestline = 'GET / HTTP/1.1'
                words = requestline.split()
                # words = ['GET', '/', 'HTTP/1.1']

                if len(words) <= 2:
                        # print("[MYRequestHandler. parse_request] Bad request syntax, requestline : {} ".format(requestline))
                        logging.debug(f"[MYRequestHandler. parse_request] Bad request syntax, requestline : {requestline} ")
                        return False

                version = words[-1]
                if not version.startswith('HTTP/'):
                        # print("[MYRequestHandler. parse_request] Bad request syntax, requestline : {} ".format(requestline))
                        logging.debug(f"[MYRequestHandler. parse_request] Bad request syntax, requestline : {requestline} ")
                        return False

                self.version = version
                self.command, self.path = words[:2]

                headers = []
                try:
                        while True:
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
                # '
                headers_lines = hstring.split('\r\n')
                self.headers = {}

                for line in headers_lines:
                        key_val = line.split(': ')
                        if key_val[0] != '':
                                self.headers[key_val[0]] = key_val[1]
                return True

        def create_xml(self, xmlDict: dict):
                xml = etree.Element("xml")
                for key, data in xmlDict.items():
                        element = etree.SubElement(xml, str(key))
                        element.text = etree.CDATA(str(data))
                xmlBytes = etree.tostring(xml, encoding="utf-8", pretty_print=True).decode("utf-8")
                return xmlBytes

        def normal_headers(self, code, message, dic=None):
                '''
                        创建一般报文头部.
                        :param code:
                        :param message:
                        :return:
                        '''
                self._headers_buffer = []
                self._headers_buffer.append(("%s %d %s\r\n" %
                                             (self.protocol_version, code, message)))
                self.dict_header("Server", "Zjx_HttpServer")
                self.dict_header("Date", time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))

                if type(dic) == "dict":
                        for key, value in dic.items():
                                self.dict_header(key, value)

                self._headers_buffer.append("\r\n")
                return "".join(self._headers_buffer)

        def dict_header(self, keyword, value):
                '''
                        通过key,value创建报文.
                        :param keyword:
                        :param value:
                        :return:
                        '''
                if not hasattr(self, '_headers_buffer'):
                        self._headers_buffer = []
                self._headers_buffer.append(
                        ("%s: %s\r\n" % (keyword, value)))

        def Response(self, body="", code=200, message="OK"):
                dic = {'Content-Type': 'text/xml'}
                headersText = self.normal_headers(code, message, dic)
                sendMes = headersText + body
                return sendMes

        def do_GET(self):
                EchoStr = self.getParams("echostr")
                return self.Response(body=EchoStr)

        def do_POST(self):
                XmlText = "".join(self.raw_requestlines)
                userInfo = etree.XML(XmlText)
                cli_type = userInfo.find("MsgType").text
                logging.debug(f"[do_post] cli_type = {cli_type}")
                if cli_type == "text":
                        ret = bot.do_specialText(userInfo)
                        if ret != "":
                                return self.Response(ret+'\r\n')

                        ret_text = self.send_to_Turing(userInfo.find("Content").text)

                        dataDict = {
                                "ToUserName": self.getParams("openid"),
                                "FromUserName": userInfo.find("ToUserName").text,
                                "CreateTime": int(time.time()),
                                "MsgType": "text",
                                "Content": ret_text,
                        }

                        data = self.create_xml(dataDict)
                        return self.Response(data)

        def send_to_Turing(self, msg_from_cli: str):
                logging.debug(f"[send_to_Turing] msg = {msg_from_cli}")
                encrypt_openID = md5(self.param["openid"].encode('utf-8')).hexdigest()
                logging.debug(f"[send_to_Turing] encrypt_openID = {encrypt_openID}")
                self.data["perception"]["inputText"]["text"] = msg_from_cli
                self.data["userInfo"]["userId"] = encrypt_openID
                logging.debug(f"[send_to_Turing] data = {self.data}")
                req = requests.post(self.TouringInterface, json=self.data, headers=self.headers)
                TouringRSP = json.loads(req.text)
                logging.debug(f"[MyHandler.send_to_Turing] send_to_Turing = {req.text}")
                try:
                        TouringText = TouringRSP["results"][0]["values"]["text"]
                        return TouringText
                except:
                        return "TouringBUUUUG!!!"


handle = MYRequestHandler()


def handleRequest(buffer: str):
        sendMes = str(handle.handle_one_request(buffer))
        print(sendMes)
        return sendMes
