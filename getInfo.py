import requests

def 章节获取(packid, Authorization, deviceId, phoneModel, apkVersion, terminalVersion, UserAgent):
    url = f"https://prod.nxjyz.net/prod-api/app/student/course/getInfo?id={packid}"
    headers = {
    "businessId": str(packid),  # 转换为字符串
    "identifier": "PClassList",
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
    "Host": "prod.nxjyz.net",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": UserAgent
    }

    res = requests.get(url, headers=headers)
    zjdata = res.json()
    if zjdata['code'] != 200:
        return None, f"课程请求状态码错误: {zjdata['code']}"
    chapters = zjdata.get("data", {}).get("children", [])
    if not chapters:
        return None, "未找到课程记录"
    if len(chapters) == 0:
        return None, "课程列表为空"
    
    all_sections = []
    for chapter in chapters:
        # 获取每个章的信息
        chapter_info = {
            "chapter_name": chapter.get("name", ""),  # 章的名称，如"第1章总体国家安全观"
            "chapter_id": chapter.get("id", ""),      # 章的ID
            "sections": []
        }
        
        # 获取该章下所有小节的信息
        sections = chapter.get("children", [])
        for section in sections:
            section_info = {
                "name": section.get("name", ""),           # 小节名称
                "id": section.get("id", ""),               # 小节ID
                "state": section.get("state", ""),         # 学习状态 N表示未完成
                "lastStudyNum": section.get("lastStudyNum", 0),  # 上次学习时长（毫秒）
                "mainResourceLength": section.get("mainResourceLength", 0),  # 资源总长度（毫秒）
                "type": section.get("type", 1)            # 节类型，1表示小节
            }
            chapter_info["sections"].append(section_info)
            
        all_sections.append(chapter_info)
    
    return all_sections, None