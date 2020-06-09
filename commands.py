import datetime
import time
import lark
import crawler


def deal_time(words, article):
    article.MsgType("text")
    article.append_Description("Content", time.strftime('(ﾉ´ヮ´)ﾉ*:･ﾟ✧现在的时间是 %Y.%m.%d %H:%M:%S 哦(๑^ں^๑)', time.localtime(time.time())))
    return True


def deal_sticker(words, article):
    if len(words) != 2:
        return False
    else:
        picBytes = crawler.get_pix_by_key(words[1])
        pic_dicList = []
        for picByte in picBytes:
            picID = article.send_WXpic(picByte)
            pic_dicList.append({"MediaId":picID})
        article.MsgType("image")
        article.append_Description("Image",pic_dicList)
        return True


def deal_todo(words, article):
    return True
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


def process_input_info(words:list, article):
    if words[0] == "time":
        return deal_time(words, article)
    elif words[0] == 'bq':
        return deal_sticker(words, article)
    elif words[0] == '/todo':
        # deal_todo(words, article)
        return False
    else:
        return False
