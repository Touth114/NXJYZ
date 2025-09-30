import requests

def 课程获取(Authorization, deviceId, phoneModel, apkVersion, terminalVersion, UserAgent):
    url = "https://prod.nxjyz.net/prod-api/app/student/course/queryMySelfCourseInfo?pageSize=100&semester=1"
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
    "Host": "prod.nxjyz.net",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": UserAgent
    }

    res = requests.get(url, headers=headers)
    kcdata = res.json()
    if kcdata['code'] != 200:
        return None, f"课程请求状态码错误: {kcdata['code']}"

    records = kcdata.get("data", {}).get("records", [])
    if not records:
        return None, "未找到课程记录"
    if len(records) == 0:
        return None, "课程列表为空"
    
    courses = []
    for record in records:
        course_info = {
            "packId": record['packId'],
            "name": record['name']
        }
        courses.append(course_info)
    
    return courses, None