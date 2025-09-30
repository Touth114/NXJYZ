import requests

def 小节详情获取(sectionId, Authorization, deviceId, phoneModel, apkVersion, terminalVersion, UserAgent):
    url = f"https://prod.nxjyz.net/prod-api/app/student/course/getSectionDetail?id={sectionId}"
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
        "Host": "prod.nxjyz.net",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": UserAgent
    }

    res = requests.get(url, headers=headers)
    section_data = res.json()
    
    if section_data['code'] != 200:
        return None, f"小节详情请求状态码错误: {section_data['code']}"
    
    # 获取主要资源信息
    main_resources = section_data.get("data", {}).get("mainResources", [])
    if not main_resources:
        return None, "未找到主要资源"
    
    # 获取第一个资源的信息
    resource = main_resources[0]
    section_info = {
        "attachmentId": resource.get("attachmentId", ""),  # 资源ID
        "name": resource.get("name", ""),                  # 资源名称
        "url": resource.get("url", ""),                    # 视频URL
        "duration": resource.get("duration", "0"),         # 视频时长
    }
    
    # 获取学习记录
    study_record = resource.get("studyRecordVo", {})
    if study_record:
        section_info.update({
            "maxProgress": study_record.get("maxProgress", "0"),      # 最大进度
            "exitProgress": study_record.get("exitProgress", "0"),    # 退出时进度
            "exitTime": study_record.get("exitTime", ""),            # 退出时间
        })
    
    # 获取题目列表
    test_list = section_data.get("data", {}).get("courseSectionTestList", [])
    questions = []
    for test in test_list:
        questions.append({
            "id": test.get("id"),
            "systemAnswerValue": test.get("systemAnswerValue", [])
        })
    section_info["questions"] = questions
    
    return section_info, None