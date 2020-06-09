
import time
import crawler


def deal_time(article):  # todo fix
    article.append_Description("Description", time.strftime('(ﾉ´ヮ´)ﾉ*:･ﾟ✧\n现在的时间是 %Y.%m.%d %H:%M:%S 哦\n(๑^ں^๑)', time.localtime(time.time())))
    return True


def deal_sticker(words, article):
    if len(words) != 2:
        article.append_Description("Description", "关键词只能有一个的说，喵•ू(ᵒ̴̶̷ωᵒ̴̶̷*•ू) ​ )੭ु⁾！")
        return True
    else:
        article.append_Description("Description", "ƪ(˘⌣˘)┐\n为你找到以下的图片")
        pic_urls = crawler.get_pix_by_key(words[1])
        for pic_url in pic_urls:
            article.append_Description("PicUrl", pic_url)
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
        return deal_time(article)
    elif words[0] == 'bq':
        return deal_sticker(words, article)
    elif words[0] == 'todo':
        # deal_todo(words, article)
        return False
    else:
        return False
