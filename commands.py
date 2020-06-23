import datetime
import time
import message_xml
import crawler
import searchData


def deal_time(words, article):
    """
    deal with time in the WeChat User send time command.
    :param words: WeChat User send content split by space.
    :param article: template WeChat receive object
    :return: function do correct/fail
    """
    # 消息格式为text
    article.MsgType("text")
    # 使用time库获取时间
    article.append_Description("Content", time.strftime('(ﾉ´ヮ´)ﾉ*:･ﾟ✧\n现在的时间是 %Y.%m.%d %H:%M:%S 哦\n(๑^ں^๑)', time.localtime(time.time())))
    return True


def deal_sticker(words, article):
    """
    deal with sticker in the WeChat User command.
    :param words: WeChat User send content split by space.
    :param article: template WeChat receive object
    :return: function do correct/fail
    """
    if len(words) != 2:
        return False
    else:
        # 获得图片的Bytes，并进行处理
        # WeChat限制， 一次最多只有一张图片能够显示， 故设置过多的图片没有意义
        picBytes = crawler.get_pix_by_key(words[1])
        pic_dicList = []

        # 获取图片的id
        for picByte in picBytes:
            # 将图片发送给WeChat， 返回一个微信服务器上对应图片的id
            picID = article.send_WXpic(picByte)
            # 将其追加到list中
            pic_dicList.append({"MediaId":picID})

        # 表示微信返回内容为image格式
        article.MsgType("image")
        # 添加内容
        article.append_Description("Image",pic_dicList)
        return True


def deal_todo(words, article):
    """
    you can add you want to do in the WeChat(NotRealized).
    :param words: WeChat User send content split by space.
    :param article: template WeChat receive object
    :return: function do correct/fail
    """
    return True
    # 功能暂未调试完成
    #     lark.send_message(access_token, event.get("open_id"), "
    #
    # else:
    #     h_m = words[1].split(':', 2)
    #
    #     inc_time = datetime.time(int(h_m[0]), int(h_m[1]), 00)
    #
    #     cur = datetime.datetime.now()
    #     left_s = inc_time.hour * 60 * 60 + inc_time.minute * 60 - cur.hour * 60 * 60 - cur.minute * 60 - cur.second
    #     if left_s < 0:
    #         lark.send_message(access_token, event.get("open_id"), "时间已经过了吧， 你再仔细检查检查")
    #     else:
    #         s = time.strftime('%Y.%m.%d %H:%M:%S ', time.localtime(time.time()))
    #         lark.send_message(access_token, event.get("open_id"),
    #                           "current time is: {}\n{} second(s) left".format(s, left_s))
    #         print("[commands.deal_todo] current time is: " + s, "%d second(s) left" % left_s)
    #         pass


def deal_search_tiku(words, article):
    """
    from TiKu.docx search most similar answer.
    :param words: WeChat User send content split by space.
    :param article: template WeChat receive object
    :return: function do correct/fail
    """
    # 消息返回类型为text
    article.MsgType("text")
    # 如果用户没有发送题目，则返回false，执行图灵机器人的消息
    if len(words) < 2:
        return False
    else:
        # 将split用户的消息，再次集合起来
        question = "".join(words[1:])
        # question = question.replace(' ', '')

    # 添加内容
    Ans = searchData.search(question)
    article.append_Description("Content", Ans)
    return True


def process_input_info(words: list, article):
    """
    find correct command from User send message.
    :param words: WeChat User send content split by space.
    :param article: template WeChat receive object
    :return: function do correct/fail
    """
    # 判断开头关键字
    if words[0] == "time":
        return deal_time(words, article)
    elif words[0] == 'bq':
        return deal_sticker(words, article)
    elif words[0] == 'st':
        return deal_search_tiku(words, article)
    elif words[0] == '/todo':
        # deal_todo(words, article)
        return False
    else:
        return False