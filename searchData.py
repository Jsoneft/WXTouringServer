from docx import Document
from fuzzywuzzy import fuzz


# 从题库搜索题目
def search(searchStr: str):
    # 尝试打开题库
    try:
        document = Document("TiKu.docx")
        # 初始设定
        # count：匹配题目数
        # reSearch：是否为重新搜索模式
        count = 0
        reSearch = False
        responseStr = ""
        responseStr += "--------------"
    except:
        # 出错
        return "题库异常，请联系管理员。\n"

    # 进入搜索
    while count == 0:
        # 如果需要research
        if reSearch:
            # 对searchStr重新修改
            searchStr = searchStr.replace("(", "（")
            searchStr = searchStr.replace(")", "）")
            searchStr = searchStr.replace("-", "")
            reSearch = False
        else:
            # 第一次搜索，修改
            searchStr = searchStr.strip()
            searchStr = searchStr.replace(" ", "")
            searchStr = searchStr.replace("\n", "")

        # 初始化find_ans为false
        find_ans = False

        # 开始对docx文本进行搜索
        for paragraph in document.paragraphs:
            # 尝试获取文本内容的rgb
            try:
                rgb = paragraph.runs[0].font.color.rgb.__str__()
            except:
                # 如果获取失败，自动设定为None
                rgb = "None"

            # 如果找到了匹配而且这个文本是答案（答案为红色，其rgb为非空）
            if find_ans and rgb != "None":
                # 将答案存入输出信息中
                responseStr += f"{paragraph.text}\n"
                continue
            else:
                # 如果到了题目，则取消find_ans
                find_ans = False
                # 最多输出3个相似题目
                if count > 3:
                    break

            # rgb为None，表示为题目
            if rgb == "None":
                # 获取输入文本与待匹配文本的相似度
                similar = fuzz.partial_ratio(paragraph.text, searchStr)
                # 相似度大于90，则输出该题
                if similar > 90:
                    responseStr += f"\n相似度{fuzz.partial_ratio(paragraph.text, searchStr)}=> {paragraph.text}\n"
                    # 题目数+1
                    count += 1
                    # 开始find_ans
                    find_ans = True

        # 如果没有找到答案，而且reSearch过后也没有，则表示搜索失败
        if count == 0 and reSearch == False:
            responseStr += "\n未搜索到!\n"
            break
        # 如果找到了答案，则跳出循环
        if count != 0:
            reSearch = False
    responseStr += "--------------"

    # 返回题目与答案信息
    return responseStr
