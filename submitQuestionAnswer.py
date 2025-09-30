import requests
import json
import random

def 提交题目答案(
    questionId,
    answerValueStr,
    Authorization,
    deviceId,
    phoneModel,
    debug=False,
    apkVersion=None,
    terminalVersion=None,
    UserAgent=None
):
    """
    提交题目答案
    
    参数:
    questionId: 题目ID
    answerValueStr: 答案字符串，格式为"[答案ID]"
    Authorization: 授权token
    deviceId: 设备ID
    phoneModel: 手机型号
    debug: 是否开启调试模式，默认为False
    """
    url = "https://prod.nxjyz.net/prod-api/app/student/course/submitQuestionAnswer"
    headers = {
        "Authorization": Authorization,
        "version": apkVersion,
        "platform": "1",
        "deviceId": deviceId,
        "apkVersion": apkVersion,
        "clientType": "A",
        "collectionVersion": "3",
        "phoneModel": phoneModel,
        "terminalVersion": terminalVersion,
        "userType": "S",
        "Content-Type": "application/json;charset=utf-8",
        "Host": "prod.nxjyz.net",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": UserAgent
    }
    data = json.dumps({
        "questionId": int(questionId),
        "answerValueStr": json.dumps(answerValueStr, ensure_ascii=False)
    }, ensure_ascii=False)

    if debug:
        print("\n=== 答题调试信息 ===")
        print("请求URL:", url)
        print("请求头:")
        print(json.dumps(headers, indent=2, ensure_ascii=False))
        print("请求体:")
        print(data)
        print("============")

    res = requests.post(url, headers=headers, data=data)
    response_data = res.json()
    if debug:
        print("响应:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        print("============\n")
    return response_data