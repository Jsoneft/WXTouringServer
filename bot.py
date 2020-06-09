# --coding:utf-8--

import commands
import lark


def do_specialText(userInfo):
    specialText = userInfo.find("Content").text
    specialText_list = specialText.split()
    article = lark.Message(userInfo)
    print(specialText)
    check = commands.process_input_info(specialText_list, article)
    if check:
        return article.generateMessage()
    else:
        return ""

# info = '''<xml>
#   <ToUserName><![CDATA[toUser]]></ToUserName>
#   <FromUserName><![CDATA[fromUser]]></FromUserName>
#   <CreateTime>1348831860</CreateTime>
#   <MsgType><![CDATA[text]]></MsgType>
#   <Content><![CDATA[bq 动漫]]></Content>
#   <MsgId>1234567890123456</MsgId>
# </xml>'''
#
# from lxml import etree
# userInfo = etree.XML(info)
# print(do_specialText(userInfo))