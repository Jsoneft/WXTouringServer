# --coding:utf-8--

import commands
import message_xml


def do_specialText(userInfo):

    """
    检查用户的消息内容，如果出现关键词，则回复关键词对应的内容。
    :param userInfo: 用户的信息，为微信发送过来的xml信息，dict类型
    :return: 如果关键词被执行，返回需要发送的xml内容， 否则返回空字符串
    """
    # 提取出用户需要的信息
    specialText = userInfo.find("Content").text
    # 用户信息按空格分割
    specialText_list = specialText.split()

    # 处理需要发送的微信内容头部
    article = message_xml.Message(userInfo)
    print(specialText)

    # 检查关键词是否被执行成功
    check = commands.process_input_info(specialText_list, article)
    if check:
        # 执行成功，返回xml文本
        return article.generateMessage()
    else:
        # 否则，返回空字符串
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