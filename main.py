import time
from datetime import datetime
import random
import os
import json
import queryMySelfCourseInfo
import getInfo
import getSectionDetail
import uploadStudyRecord
from submitQuestionAnswer import 提交题目答案

# 调试模式开关
DEBUG_MODE = True  # 设置为 True 开启调试输出，False 关闭调试输出
MODE = True  # 设置为 True 时执行自动观看流程，False 时执行其他流程

# 认证信息 这些信息请替换为你自己的 这里推荐抓包获取
Authorization = "" #认证信息 抓包获取
phoneModel = "" #手机型号 抓包获取
deviceId = "" #设备ID 抓包获取
phoneMode = "" #手机代号 抓包获取
apkVersion = ""  # 软件版本号
terminalVersion = ""  # Android系统版本号或者IOS系统版本号
UserAgent = "okhttp/3.14.9"  # android为okhttp/3.14.9 IOS 为GasStation/3.5.11 (iPhone; iOS 18.6; Scale/3.00) 

def main():
    current_section_info = None  # 用于保存当前正在观看的小节信息    
    try:
        if MODE:
            # 获取课程信息
            courses, error = queryMySelfCourseInfo.课程获取(Authorization, deviceId, phoneModel, apkVersion, terminalVersion, UserAgent)
            if error:
                print(f"获取课程信息失败：{error}")
                return
                
            print(f"获取课程信息成功：")
            print(f"共找到 {len(courses)} 个课程")

            for i, course in enumerate(courses, 1):
                print(f"\n课程 {i}:")
                print(f"课程ID: {course['packId']}")
                print(f"课程名称: {course['name']}")
                
                packId = course['packId']
                
                # 获取课程章节信息
                chapters, error = getInfo.章节获取(packId, Authorization, deviceId, phoneModel, apkVersion, terminalVersion, UserAgent)
                if error:
                    print(f"获取章节信息失败：{error}")
                    continue
                    
                print(f"\n课程章节结构:")
                total_progress = 0
                total_sections = 0
                
                for chapter in chapters:
                    print(f"\n{chapter['chapter_name']} (ID: {chapter['chapter_id']})")
                    for section in chapter['sections']:
                        total_sections += 1
                        study_progress = section['lastStudyNum'] / section['mainResourceLength'] * 100 if section['mainResourceLength'] > 0 else 0
                        total_progress += study_progress
                        
                        # 打印小节信息
                        print(f"  - {section['name']}")
                        print(f"    小节ID: {section['id']}")
                        print(f"    学习状态: {'未学习' if section['state'] == 'N' else '已学习'}")
                        print(f"    学习进度: {study_progress:.1f}%")
                        print(f"    视频时长: {section['mainResourceLength']/1000:.1f}秒")
                        
                        # 如果已经学习完成，跳过
                        if section['state'] != 'N':
                            print(f"    状态: 此课程已经观看完成")
                            continue
                            
                        # 获取小节详细信息
                        section_detail, detail_error = getSectionDetail.小节详情获取(
                            section['id'], 
                            Authorization, 
                            deviceId, 
                            phoneModel, 
                            apkVersion, 
                            terminalVersion, 
                            UserAgent
                        )
                        
                        if detail_error:
                            print(f"    获取详情失败: {detail_error}")
                            continue
                        
                        print(f"    资源ID: {section_detail['attachmentId']}")
                        print(f"    资源名称: {section_detail['name']}")
                        print(f"    上次学习进度: {section['lastStudyNum']}ms")
                        print(f"    需要学习时长: {section['mainResourceLength']}ms")
                        
                        # 生成开始时间
                        # 保证三位毫秒精度
                        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
                        uuid = str(int(time.time() * 1000))
                        
                        # 保存当前学习小节信息
                        current_section_info = {
                            "section_id": section['id'],
                            "attachment_id": section_detail['attachmentId'],
                            "start_progress": section['lastStudyNum'],
                            "main_resource_length": section['mainResourceLength'],
                            "start_time": start_time,
                            "uuid": uuid,
                            "phoneMode": phoneMode
                        }
                        
                        # 计算需要观看的时长（毫秒）并等待
                        remaining_time = (section['mainResourceLength'] - section['lastStudyNum']) / 1000  # 转换为秒
                        
                        # 计算分钟和秒
                        end_timestamp = time.time() + remaining_time
                        end_dt = datetime.fromtimestamp(end_timestamp)
                        min_part = int(remaining_time // 60)
                        sec_part = int(remaining_time % 60)
                        
                        print(f"\n    开始学习，预计需要 {min_part} 分钟 {sec_part} 秒... 预计结束时间：{end_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        try:
                            time.sleep(remaining_time)
                        except KeyboardInterrupt:
                            print("\n检测到退出信号，正在提交当前小节已观看时长...")
                            if current_section_info:
                                exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
                                watched_ms = int(
                                    (datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S:%f") -
                                     datetime.strptime(current_section_info['start_time'], "%Y-%m-%d %H:%M:%S:%f")).total_seconds() * 1000
                                )
                                exit_progress = current_section_info['start_progress'] + watched_ms
                                if exit_progress > current_section_info['main_resource_length']:
                                    exit_progress = current_section_info['main_resource_length']
                                result, upload_error = uploadStudyRecord.上传学习记录(
                                    current_section_info['section_id'],
                                    Authorization,
                                    deviceId,
                                    phoneModel,
                                    current_section_info['attachment_id'],
                                    current_section_info['start_progress'],
                                    exit_progress,
                                    current_section_info['start_time'],
                                    exit_time,
                                    current_section_info['uuid'],
                                    current_section_info['phoneMode'],
                                    DEBUG_MODE,
                                    apkVersion,
                                    terminalVersion,
                                    UserAgent
                                )
                                if upload_error:
                                    print(f"当前小节提交失败: {upload_error}")
                                else:
                                    print(f"当前小节已观看时长已提交: {exit_progress}ms")
                            print("请手动关闭程序窗口或按Ctrl+C再次退出。")
                            return
                        
                        # 生成结束时间
                        exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
                        
                        # 上传学习记录
                        result, upload_error = uploadStudyRecord.上传学习记录(
                            section['id'],
                            Authorization, 
                            deviceId, 
                            phoneModel,
                            section_detail['attachmentId'],
                            section['lastStudyNum'],
                            section['mainResourceLength'],
                            start_time,
                            exit_time,
                            uuid,
                            phoneMode,
                            DEBUG_MODE, 
                            apkVersion,
                            terminalVersion, 
                            UserAgent
                        )
                        
                        current_section_info = None  # 清除当前小节信息
                        
                        if upload_error:
                            print(f"    上传状态: {upload_error}")
                        else:
                            print(f"    上传状态: {result['message']}")
                            print(f"    开始时间: {result['start_time']}")
                            print(f"    结束时间: {result['exit_time']}")
                            print(f"    学习进度: {result['progress']}ms")
                            
                            # 视频观看完后，提交题目答案
                            for q in section_detail.get('questions', []):
                                question_id = q['id']
                                answer_value = q['systemAnswerValue']
                                if not question_id or not answer_value:
                                    print(f"    跳过无效题目: {q}")
                                    continue
                                    
                                delay = random.randint(1, 30)
                                print(f"    答题前随机延迟 {delay} 秒...")
                                time.sleep(delay)
                                print(f"    正在提交题目ID: {question_id}, 答案: {answer_value}")
                                
                                提交题目答案(
                                    question_id, 
                                    answer_value, 
                                    Authorization, 
                                    deviceId, 
                                    phoneModel,
                                    DEBUG_MODE, 
                                    apkVersion, 
                                    terminalVersion, 
                                    UserAgent
                                )
                        
                if total_sections > 0:
                    average_progress = total_progress / total_sections
                    print(f"\n课程总进度: {average_progress:.1f}%")


        else:
            # MODE 为 False 时的重新观看流程，支持本地化进度存储
            progress_file = "replay_progress.json"
            last_progress = None
            if os.path.exists(progress_file):
                with open(progress_file, "r", encoding="utf-8") as f:
                    last_progress = json.load(f)

            courses, error = queryMySelfCourseInfo.课程获取(Authorization, deviceId, phoneModel, apkVersion, terminalVersion, UserAgent)
            if error:
                print(f"获取课程信息失败：{error}")
                return
            print(f"获取课程信息成功：")
            print(f"共找到 {len(courses)} 个课程")

            finished = True
            found_resume = False
            for i, course in enumerate(courses, 1):
                print(f"\n课程 {i}:")
                print(f"课程ID: {course['packId']}")
                print(f"课程名称: {course['name']}")
                packId = course['packId']
                chapters, error = getInfo.章节获取(packId, Authorization, deviceId, phoneModel, apkVersion, terminalVersion, UserAgent)
                if error:
                    print(f"获取章节信息失败：{error}")
                    continue
                print(f"\n课程章节结构:")
                for chapter in chapters:
                    print(f"\n{chapter['chapter_name']} (ID: {chapter['chapter_id']})")
                    for section in chapter['sections']:
                        # 跳过未到达的断点
                        if last_progress and not found_resume:
                            if last_progress.get("course_id") == packId and last_progress.get("section_id") == section['id']:
                                found_resume = True
                            else:
                                continue

                        print(f"  - {section['name']}")
                        print(f"    小节ID: {section['id']}")
                        print(f"    视频时长: {section['mainResourceLength']/1000:.1f}秒")

                        # 获取小节详细信息
                        section_detail, detail_error = getSectionDetail.小节详情获取(
                            section['id'],
                            Authorization,
                            deviceId,
                            phoneModel,
                            apkVersion,
                            terminalVersion,
                            UserAgent
                        )
                        if detail_error:
                            print(f"    获取详情失败: {detail_error}")
                            continue

                        exit_progress = int(section_detail.get('exitProgress', 0))
                        main_resource_length = int(section['mainResourceLength'])
                        # 如果exitProgress等于视频长度，则重置为0
                        if exit_progress >= main_resource_length:
                            exit_progress = 0

                        print(f"    上次退出进度: {exit_progress}ms")
                        print(f"    需要学习时长: {main_resource_length}ms")

                        # 保存本地进度
                        with open(progress_file, "w", encoding="utf-8") as f:
                            json.dump({"course_id": packId, "section_id": section['id']}, f, ensure_ascii=False)

                        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
                        uuid = str(int(time.time() * 1000))
                        current_section_info = {
                            "section_id": section['id'],
                            "attachment_id": section_detail['attachmentId'],
                            "start_progress": exit_progress,
                            "main_resource_length": main_resource_length,
                            "start_time": start_time,
                            "uuid": uuid,
                            "phoneMode": phoneMode
                        }

                        remaining_time = (main_resource_length - exit_progress) / 1000
                        end_timestamp = time.time() + remaining_time
                        end_dt = datetime.fromtimestamp(end_timestamp)
                        min_part = int(remaining_time // 60)
                        sec_part = int(remaining_time % 60)
                        print(f"\n    开始重新观看，预计需要 {min_part} 分钟 {sec_part} 秒... 预计结束时间：{end_dt.strftime('%Y-%m-%d %H:%M:%S')}")

                        try:
                            time.sleep(remaining_time)
                        except KeyboardInterrupt:
                            print("\n检测到退出信号，正在提交当前小节已观看时长...")
                            if current_section_info:
                                exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
                                # 保证 start_time 也是三位毫秒精度
                                start_time_fixed = current_section_info['start_time'][:23] if len(current_section_info['start_time']) > 23 else current_section_info['start_time']
                                watched_ms = int(
                                    (datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S:%f") -
                                     datetime.strptime(start_time_fixed, "%Y-%m-%d %H:%M:%S:%f")).total_seconds() * 1000
                                )
                                exit_progress2 = current_section_info['start_progress'] + watched_ms
                                if exit_progress2 > current_section_info['main_resource_length']:
                                    exit_progress2 = current_section_info['main_resource_length']
                                result, upload_error = uploadStudyRecord.上传学习记录(
                                    current_section_info['section_id'],
                                    Authorization,
                                    deviceId,
                                    phoneModel,
                                    current_section_info['attachment_id'],
                                    current_section_info['start_progress'],
                                    exit_progress2,
                                    start_time_fixed,
                                    exit_time,
                                    current_section_info['uuid'],
                                    current_section_info['phoneMode'],
                                    DEBUG_MODE,
                                    apkVersion,
                                    terminalVersion,
                                    UserAgent
                                )
                                if upload_error:
                                    print(f"当前小节提交失败: {upload_error}")
                                else:
                                    print(f"当前小节已观看时长已提交: {exit_progress2}ms")
                            print("请手动关闭程序窗口或按Ctrl+C再次退出。")
                            return

                        exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
                        # 保证 start_time 也是三位毫秒精度
                        start_time_fixed = start_time[:23] if len(start_time) > 23 else start_time
                        result, upload_error = uploadStudyRecord.上传学习记录(
                            section['id'],
                            Authorization,
                            deviceId,
                            phoneModel,
                            section_detail['attachmentId'],
                            exit_progress,
                            main_resource_length,
                            start_time_fixed,
                            exit_time,
                            uuid,
                            phoneMode,
                            DEBUG_MODE,
                            apkVersion,
                            terminalVersion,
                            UserAgent
                        )
                        current_section_info = None
                        if upload_error:
                            print(f"    上传状态: {upload_error}")
                        else:
                            print(f"    上传状态: {result['message']}")
                            print(f"    开始时间: {result['start_time']}")
                            print(f"    结束时间: {result['exit_time']}")
                            print(f"    学习进度: {result['progress']}ms")
                        finished = False

            # 全部观看完后删除本地进度文件
            if os.path.exists(progress_file) and not finished:
                os.remove(progress_file)

    except Exception as e:
        print(f"发生异常: {e}")

if __name__ == "__main__":
    main()