# --coding:utf-8--

import commands
import article


def do_specialText(userInfo):
    specialText = userInfo.find("Content").text
    specialText_list = specialText.split()
    Article = article.Article(userInfo)

    print(specialText)
    check = commands.process_input_info(specialText_list, Article)
    if check:
        return Article.generateArticle()
    else:
        return ""

info = '''<xml>
  <ToUserName><![CDATA[toUser]]></ToUserName>
  <FromUserName><![CDATA[fromUser]]></FromUserName>
  <CreateTime>1348831860</CreateTime>
  <MsgType><![CDATA[text]]></MsgType>
  <Content><![CDATA[bq 动漫]]></Content>
  <MsgId>1234567890123456</MsgId>
</xml>'''

from lxml import etree

userInfo = etree.XML(info)
h = do_specialText(userInfo)
print(h)