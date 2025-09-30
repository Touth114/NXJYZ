import requests
import json

def 上传学习记录(sectionId, Authorization, deviceId, phoneModel, attachmentId, 
                startProgress, exitProgress, startTime, exitTime, uuid, phoneMode,
                debug=False, apkVersion=None, terminalVersion=None, UserAgent=None):
    """
    上传学习记录
    
    参数:
    sectionId: 小节ID
    Authorization: 授权token
    deviceId: 设备ID
    phoneModel: 手机型号
    attachmentId: 资源ID
    startProgress: 开始进度（毫秒）
    exitProgress: 结束进度（毫秒）
    startTime: 开始时间（格式：YYYY-MM-DD HH:mm:ss:SSS）
    exitTime: 结束时间（格式：YYYY-MM-DD HH:mm:ss:SSS）
    uuid: 唯一标识（毫秒级时间戳）这里是开始时间的时间戳
    """
    url = "https://prod.nxjyz.net/prod-api/app/student/studyRecord/uploadStudyRecord"
    headers = {
        "businessId": str(sectionId),
        "identifier": "PClassDetail",
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
    
    # 构建请求数据
    record_data = [{
        "attachmentId": int(attachmentId),
        "exitProgress": exitProgress,
        "exitTime": exitTime,
        "maxProgress": exitProgress,   # maxProgress 应该和 exitProgress 一致
        "objectId": int(sectionId),
        "objectType": 1,
        "phoneModel": phoneMode,
        "startProgress": startProgress,
        "startTime": startTime,
        "uuid": uuid
    }]

    # 如果开启调试模式，打印请求信息
    if debug:
        print(f"\n    上传学习记录请求参数:")
        print(f"    上传URL: {url}")
        print(f"    请求数据:")
        print(json.dumps(record_data, indent=4, ensure_ascii=False).replace('\n', '\n    '))

    res = requests.post(url, headers=headers, data=json.dumps(record_data))
    response_data = res.json()
    
    if debug:
        print(f"\n    上传学习记录响应数据:")
        print(json.dumps(response_data, indent=4, ensure_ascii=False).replace('\n', '\n    '))
    
    if response_data['code'] != 200:
        return None, f"上传学习记录失败：{response_data.get('msg', '未知错误')}"
    
    return {
        "message": "上传成功",
        "start_time": startTime,
        "exit_time": exitTime,
        "progress": exitProgress
    }, None