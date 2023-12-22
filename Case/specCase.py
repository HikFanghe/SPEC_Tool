# -*- coding: utf-8 -*-
"""
@Auth ： Fanghe.Lin
@File ：specCase.py
@IDE ：PyCharm
@Time ： 2023/10/9 16:30
@Institution: Hikvision, China
"""
import re

from lib.mtd_com_fun import *

class AutoVivification(dict):
    """定义多级字典"""

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

class SpecTestCase(MtdComFun):

    def __init__(self):
        super().__init__()
        # 智能中英文对应
        self.Integdic = {
            "mixedTargetDetection": "混合目标",
            "smart": "周界智能",
            "facesnap": "人脸抓拍",
            "faceCapture": "人脸抓拍",
            "Face Capture": "人脸抓拍",
            "smartHVTDetection": "简易智能&&混行检测",
            "judicial": "司法",
            "roadDetection": "道路监控",
            "perimeterCapture": "周界抓拍",
            "vehicleDetection": "车辆检测",
            "hvtVehicleDetection": "混行检测",
            "close": "普通监控",
            "faceHumanModelingContrast": "混合目标比对",
            "cityManagement": "智慧城管监测",
            "teacherBehavior": "教师行为检测",
            "personQueueDetection": "人员排队检测",
            "verticalPeopleCounting": "垂直客流",
            "AIOpenPlatform": "AI开放平台",
            "safetyHelmet": "安全帽检测",
            "faceContrast": "人脸比对",
            "faceMonitor": "人脸布控",
            "vehicleMonitor": "车辆布控",
            "faceCounting": "人脸客流",
            "heelPDC": "倾斜客流",
            "personDensity": "人员密度",
            "personArming": "人员布控",
            "smokeDetectAlarm": "抽烟检测",
            "smokeDetection": "烟雾检测",
            "intelligentTraffic": "智能交通",
            "objectsThrownDetection": "高空抛物检测",
            "heatmap": "热度图",
            "smart": "Smart事件",
        }
        # PTZ功能
        self.parkactionCapDict = {
            "autoscan": "自动扫描",
            "framescan": "帧扫描",
            "randomscan": "随机扫描",
            "patrol": "巡检",
            "pattern": "花样扫描",
            "preset": "预置点扫描",
            "panoramascan": "全景扫描",
            "tiltscan": "垂直扫描",
            "combinedPath": "组合扫描",
            "sceneTrace": "场景巡航",
            "atuoscan": "区域扫描"
        }
        # 普通事件中英文对应
        self.EventCapDic = {"motionDetection": "移动侦测",
                            "VMD": "移动侦测",
                            "tamperDetection": "遮挡报警",
                            "Shelteralarm": "遮挡报警",
                            "audioDetection": "音频异常侦测",
                            "audioexception": "音频异常侦测",
                            "defocusDetection": "虚焦检测",
                            "defocus": "虚焦检测",
                            "sceneChangeDetection": "场景变更侦测",
                            "scenechangedetection": "场景变更侦测",
                            "faceDetection": "人脸侦测",
                           "facedetection": "人脸侦测",
                            }
        # 异常事件中英文对应
        self.ExceptionEventDic = {"diskfull":"硬盘满",
                               "diskerror":"硬盘错误",
                               "nicbroken":"网络断开",
                               "ipconflict":"IP地址冲突",
                               "illaccess":"非法访问",
                               "abnormalReboot":"异常重启",}
        # smart事件中英文对应
        self.smartDic = {
            "LineDetection": "越界侦测",
            "lineDetection": "越界侦测",
            "FieldDetection": "区域入侵侦测",
            "fieldDetection": "区域入侵侦测",
            "RegionEntrance": "进入区域侦测",
            "regionEntrance": "进入区域侦测",
            "RegionExiting": "离开区域侦测",
            "regionExiting": "离开区域侦测",
            "Loitering": "徘徊侦测",
            "loitering": "徘徊侦测",
            "Group": "人员聚集侦测",
            "group": "人员聚集侦测",
            "RapidMove": "快速运动侦测",
            "rapidMove": "快速运动侦测",
            "Parking": "停车侦测",
            "parking": "停车侦测",
            "UnattendedBaggage": "物品遗留侦测",
            "unattendedBaggage": "物品遗留侦测",
            "AttendedBaggage": "物品拿取侦测",
            "attendedBaggage": "物品拿取侦测",
        }

    # 深度学习框架
    def getDeepLearnFramework(self):
        if self.isOverseas:
            return "Caffe;PyTorch;TensorFlow;PaddlePaddle;ONNX"
        return "Caffe，PyTorch，TensorFlow"

    # 浏览器
    def getChrome(self):
        if not self.isOverseas:
            return "使用插件预览 Plug-in required live view: IE 10, IE 11\r\n无插件预览 Plug-in free live view:  Chrome 57.0+, Firefox 52.0+, Edge 89+, Safari 11+\r\n本地服务 Local service: Chrome 57.0+, Firefox 52.0+, Edge 89+"
        else:
            if self.deviceInfo['dev_type'] == 'IPD':
                return "Plug-in required live view: IE 10, IE 11\r\nPlug-in free live view:  Chrome 57.0+, Firefox 52.0+, Edge 89+, Safari 11+\r\nLocal service: Chrome 57.0+, Firefox 52.0+, Edge 89+"
            else:
                return 'Plug-in required live view: IE8+\r\nPlug-in free live view: Chrome 57.0+, Firefox 52.0+, Safari 11+\r\nLocal service: Chrome 41.0+, Firefox 30.0+'

        # if self.deviceInfo['dev_type'] == 'IPD':
        #     if self.isOverseas:
        #         return "Plug-in required live view: IE 10, IE 11\r\nPlug-in free live view:  Chrome 57.0+, Firefox 52.0+, Edge 89+, Safari 11+\r\nLocal service: Chrome 57.0+, Firefox 52.0+, Edge 89+"
        #     return "使用插件预览 Plug-in required live view: IE 10, IE 11\r\n无插件预览 Plug-in free live view:  Chrome 57.0+, Firefox 52.0+, Edge 89+, Safari 11+\r\n本地服务 Local service: Chrome 57.0+, Firefox 52.0+, Edge 89+"
        # else:
        #     if self.isOverseas:
        #         return 'Plug-in required live view: IE8+\r\nPlug-in free live view: Chrome 57.0+, Firefox 52.0+, Safari 11+\r\nLocal service: Chrome 41.0+, Firefox 30.0+'
        #     return '使用插件预览：IE8+，Chrome41.0~44，Firefox30.0~51，Safari8.0~11\r\n无插件预览：Chrome45.0+，Firefox52.0+\r\n使用本地服务预览：Chrome 57.0+，Firefox 52.0+'

    # 恢复出厂设置
    def getReset(self):
        if self.isOverseas:
            return "Support for RESET button, client or browser recovery"
        return "支持RESET按键，客户端或浏览器恢复"

    # 开放能力
    def getOpenCapability(self):
        # 开放能力
        if self.isOverseas:
            if self.AIOP_Version:
                tmp = self.AIOP_Version.split('.')
                ver = '.'.join(tmp[0:2]) if len(tmp) > 2 else self.AIOP_Version
                msg = f'HEOP {ver} OpendevSDK, Basic service, basic media capability, deep learning reasoning acceleration capability'
            else:
                msg = 'Basic service, basic media capability, deep learning reasoning acceleration capability'
        else:
            msg = "基础业务逻辑能力，基础媒体服务能力，深度学习推理加速能力\r\nBASE库：提供RTSP/ISAPI服务、HTTP代理服务、License授权服务、端口服务、日志服务等\r\nBSC库：提供多媒体视频服务和相应图像加速处理工具，包括获取YUV原始数据流、图像缩放、JPEG编解码、OSD叠加等功能，方便客户搭建差异化的智能处理框架\r\nHIKFLOW库：提供深度学习推理加速能力、常见图像处理加速能力，包括缩放，颜色空间转换等"
        return msg

    # 开放资源规格
    def getopenAIParms(self):
        # 支持中英文
        openAIUrl = '/ISAPI/Custom/OpenPlatform/resource'
        ret = self.get(openAIUrl)
        if "</resource>" not in ret:
            return "开放资源规格读取失败"
        try:
            deviceMemory = re.findall(r"<totalMemory>(.*?)</totalMemory>", ret)[0]
            deviceFlash = re.findall(r"<totalFlash>(.*?)</totalFlash>", ret)[0]
            deviceIntelligentMemory = re.findall(r"<totalIntelligentMemory>(.*?)</totalIntelligentMemory>", ret)[0]
            resMsg = f"系统内存：{deviceMemory} MB\r\n智能内存：{deviceIntelligentMemory} MB\r\nFlash/eMMC：{int(deviceFlash) // 1024} GB\r\n"
            resMsg_en = f"System Memory：{deviceMemory} MB\r\nSmart RAM：{deviceIntelligentMemory} MB\r\nFlash/eMMC：{int(deviceFlash) // 1024} GB\r\n"
            if self.isOverseas:
                return resMsg_en
            return resMsg
        except Exception as e:
            return f"获取能力异常，异常原因:{str(e)}"

    # 开发语言
    def getBuildLanguage(self):
        if not self.isOverseas:
            return "C,C++"
        else:
            return "C;C++;Go;Python"

    # Smart事件
    def getSmartCap(self, IntegSupportList):
        # 支持中英文输出
        ip = self.ip
        try:
            # 若有Smart智能，切换至Smart模式下再读取
            if 'smart' in IntegSupportList or 'Smart事件' in IntegSupportList:
                capFlag, capMsg = self.integ_channel_Intelligent_VCAResource_judeg_and_change(self.deviceInfo, vcaType='smart')
                if not (capMsg == True and capMsg == True):
                    msg = '设备存在smart智能，但切换为smart智能资源失败；该规格项在常规模式下直接读取smart事件，结果可能有误，请手动检查！'
                    self.VD_LOG_DEBUG(self.ip, msg)
                    self.trans_result.emit(2, msg, self.ip)

            ret = self.isapi_get('/ISAPI/Event/channels/capabilities',
                                 path=[".//ChannelEventCap/eventType"],
                                 type=["attrib"],
                                 attrib=['opt'])
            if not ret["success"]:
                msg = f"获取普通事件能力失败，失败原因:{ret['msg']}"
                self.VD_LOG_DEBUG(ip, msg)
                return msg
            SmartEventCapList = ret["data"][0][0].split(",")
            self.VD_LOG_DEBUG(ip, "EventCapList", SmartEventCapList, level='INFO')
            if SmartEventCapList == []:
                return "未读取到事件信息"
            if not self.isOverseas:
                # 中文设备输出中文
                resmsg = []
                # 判断Smart事件
                for i in SmartEventCapList:
                    if i in self.smartDic:
                        resmsg.append(self.smartDic[i])
                self.VD_LOG_DEBUG(ip, list(set(resmsg)), level='INFO')
                if resmsg != []:
                    return ",".join(list(set(resmsg)))
                else:
                    return "未读取到smart事件"
            else:
                # 海外设备输出英文
                resmsg = []
                # 判断Smart事件i
                for i in SmartEventCapList:
                    if i in self.smartDic:
                        resmsg.append(i)
                self.VD_LOG_DEBUG(ip, list(set(resmsg)), level='INFO')
                if resmsg != []:
                    return ",".join(list(set(resmsg)))
                else:
                    return "未读取到smart事件"

        except Exception as e:
            self.VD_LOG_DEBUG(ip, str(e))
            return "判断smart能力异常"

    # 最大分辨率
    def getMaxResolution(self):
        # 输出无需分中文英文
        chans_num = self.chans_num
        ip = self.ip
        MaxResolution_cap = 1
        max_Width = 1
        max_Height = 1
        # 2、通道能力循环
        for current_chan in range(1, chans_num + 1):
            try:
                # 2.1判断设备当前通道主码流能力
                mainStreamUrl = '/ISAPI/Streaming/channels'
                ret = self.get(mainStreamUrl)
                if "<id>%d01</id>" % current_chan not in ret:
                    msg = f"通道{current_chan}没有主码流!"
                    self.VD_LOG_DEBUG(ip, msg)
                    continue

                chanlCapUrl = '/ISAPI/Streaming/channels/%d01/capabilities' % current_chan
                cap = self.get(chanlCapUrl)
                if "</StreamingChannel>" not in cap:
                    msg = f"通道{current_chan}主码流获取视频参数能力协议执失败:{self.get_subStatusCode(cap)}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

                if '</Video>' not in cap:
                    msg = f"通道{current_chan}主码流不支持视频功能!"
                    self.VD_LOG_DEBUG(ip, msg)
                    continue

                if '</videoResolutionWidth>' not in cap:
                    msg = f"通道{current_chan}主码流不支持分辨率功能!"
                    self.VD_LOG_DEBUG(ip, msg)
                    continue

                # 2.2.获取当前通道分辨率能力集
                ret = self.isapi_get(chanlCapUrl,
                                     path=[
                                         ".//Video/videoResolutionWidth",
                                         ".//Video/videoResolutionHeight"
                                     ],
                                     type=["attrib", "attrib"],
                                     attrib=['opt', 'opt'])

                if not ret['success']:
                    msg = f"通道{current_chan}主码流获取视频分辨率能力集协议执行失败:{ret['msg']}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

                videoResolutionWidth, videoResolutionHeight = ret['data']
                videoResolutionWidth = videoResolutionWidth[0].split(",")
                videoResolutionHeight = videoResolutionHeight[0].split(",")

                if len(videoResolutionWidth) >= 1:
                    for i in range(len(videoResolutionWidth)):
                        if int(videoResolutionWidth[i]) * int(videoResolutionHeight[i]) > MaxResolution_cap:
                            MaxResolution_cap = int(videoResolutionWidth[i]) * int(videoResolutionHeight[i])
                            max_Width = videoResolutionWidth[i]
                            max_Height = videoResolutionHeight[i]

                else:
                    self.VD_LOG_DEBUG(ip, f"该设备通道{current_chan}主码流未读取到分辨率")
                    continue
            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                msg = f"通道{current_chan}获取能力异常，异常原因：{str(e)}"
                return msg
            return f"{max_Width} x {max_Height}"

    # 聚焦模式
    def getFocusMode(self):
        # 支持中英文输出
        chans_num = self.chans_num
        ip = self.ip
        ALL_FocusMode_dic = []
        try:
            for current_chan in range(1, chans_num + 1):
                chanlCapUrl = '/ISAPI/Image/channels/%d/capabilities' % current_chan
                cap = self.get(chanlCapUrl)
                if '</FocusConfiguration>' not in cap:
                    continue
                else:
                    # 2.2获取聚焦模式能力集
                    ret = self.isapi_get(chanlCapUrl, path=[".//FocusConfiguration/focusStyle"], type=["attrib"],
                                         attrib=['opt'])
                    FocusModeList = ret['data'][0][0].split(",")
                    for i in FocusModeList:
                        if i not in ALL_FocusMode_dic:
                            ALL_FocusMode_dic.append(i)

            if ALL_FocusMode_dic != []:
                if not self.isOverseas:
                    return "/".join(ALL_FocusMode_dic).replace("SEMIAUTOMATIC", "半自动").replace("AUTO",
                                                                                                  "自动").replace(
                        "MANUAL", "手动").replace("RAPIDFOCUS", "鹰式聚焦")
                else:
                    return "/".join(ALL_FocusMode_dic).replace("SEMIAUTOMATIC", "semi - auto").replace(
                        "AUTO", "Auto").replace("MANUAL", "manual").replace("RAPIDFOCUS", "rapid focus")
            else:
                return '不支持' if not self.isOverseas else 'No'
        except Exception as e:
            self.VD_LOG_DEBUG(ip, str(e))
            return f"设备获取聚焦模式能力异常，异常原因：{str(e)}"

    # PN制
    def getPNCap(self):
        # 支持中英文输出
        chans_num = self.chans_num
        ip = self.ip
        PN_dic = []
        try:
            for current_chan in range(1, chans_num + 1):
                chanlCapUrl = '/ISAPI/Image/channels/%d/capabilities' % current_chan
                cap = self.get(chanlCapUrl)
                if '</ImageChannel>' not in cap:
                    msg = f"通道{current_chan}获取图像参数能力协议执行失败:{self.get_subStatusCode(cap)}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

                if '</powerLineFrequency>' not in cap:
                    msg = f"通道{current_chan}不支持视频制式能力!"
                    self.VD_LOG_DEBUG(ip, msg)
                    continue

                ret = self.isapi_get(
                    chanlCapUrl,
                    path=[".//powerLineFrequency/powerLineFrequencyMode"],
                    type=["attrib"],
                    attrib=['opt'])
                if not ret['success']:
                    msg = f"通道{current_chan}获取视频制式能力集协议执行失败:{ret['msg']}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg
                PNcap = ret['data'][0][0].replace("50hz", "P制").replace("60hz", "N制").split(',')
                # PNList为"P制"或者"N制"或者"P制,N制"
                PN_dic += PNcap
            PN_dic = list(set(PN_dic))
            if len(PN_dic) >= 2:
                return 'PN制' if not self.isOverseas else 'PN制'
            else:
                return 'P制' if not self.isOverseas else 'P'

        except Exception as e:
            self.VD_LOG_DEBUG(ip, str(e))
            return f"设备获取PN制能力异常，异常原因：{str(e)}"

    # 断电记忆
    def getPowerOutMemory(self):
        # 支持中英文输出
        try:
            chanlCapUrl = '/ISAPI/PTZCtrl/channels/1/saveptzpoweroff'
            # "判断是否支持掉电记忆"
            cap = self.get(chanlCapUrl)
            if '</savePtzPoweroff>' in cap:
                return '支持' if not self.isOverseas else 'Yes'
            else:
                return '不支持' if not self.isOverseas else 'No'
        except Exception as e:
            self.VD_LOG_DEBUG(self.ip, str(e))
            return f"设备获取掉电记忆能力异常，异常原因：{str(e)}"

    # 预置点
    def getPTZPresetNum(self):
        # 支持中英文输出
        chans_num = self.chans_num
        ip = self.ip
        # 最大预置点个数
        PTZPreset_dic = 0
        # 2、通道能力循环
        try:
            for current_chan in range(1, chans_num + 1):

                # 2.1判断设备当前通道预置点能力
                chanlCapUrl = '/ISAPI/PTZCtrl/channels/%d/capabilities' % current_chan
                ret = self.get(chanlCapUrl)
                if "</PTZChanelCap>" not in ret:
                    msg = f"设备获取通道{current_chan}PTZ能力协议执行失败:{self.get_subStatusCode(ret)}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

                if "</maxPresetNum>" not in ret:
                    msg = f"设备通道{current_chan}不支持预置点设置功能!"
                    self.VD_LOG_DEBUG(ip, msg)
                    continue

                retstr = re.findall(r"<maxPresetNum>(.*?)</maxPresetNum>", ret)
                if retstr:
                    supportPresetNum = int(retstr[0])
                    if supportPresetNum > PTZPreset_dic:
                        PTZPreset_dic = supportPresetNum
                else:
                    msg = f"设备通道{current_chan}获取预置点个数失败!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

            if PTZPreset_dic != 0:
                return PTZPreset_dic
            else:
                return '不支持' if not self.isOverseas else 'No'

        except Exception as e:
            self.VD_LOG_DEBUG(ip, str(e))
            return f"设备获取通道预置点能力异常，异常原因：{str(e)}"

    # # 快门，即曝光时间
    # def getshutterCap(self):
    #     # 获取快门能力，如果有smart需要先切到smart
    #     # 不同情况下快门会变化，暂时返回默认情况下的快门数值
    #     chans_num = self.chans_num
    #     ip = self.ip
    #     # 是否关联
    #     isRelative = False
    #     # 所支持的通道
    #     isSupportChal = []
    #
    #     # 是否为开放HEOP
    #     isOpenHeop = 0
    #     ShutterLevelCap_min = 0
    #     ShutterLevelCap_max = 0
    #     for current_chan in range(1, chans_num + 1):
    #         try:
    #             # 2.1.智能资源切换Smart模式能力判断。
    #             capFlag, capMsg = self.channel_VCAResourse_cap_judge(current_chan, "smart")
    #             if capFlag:
    #                 # 设备智能资源之间是否存在关联
    #                 isRelative = capMsg[2]
    #                 if not isRelative and capMsg[1]:
    #                     isSupportChal.append(str(current_chan))
    #
    #                 if isRelative:
    #                     changeFlag, changeMsg = self.channel_Intelligent_VCAResource_change(self.deviceInfo,
    #                                                                                         [], "smart", isRelative,
    #                                                                                         isOpenHeop, 1)
    #                     if not changeFlag:
    #                         self.VD_LOG_DEBUG(ip, changeMsg)
    #                         self.VD_LOG_DEBUG(ip, changeMsg)
    #                 else:
    #                     changeFlag, changeMsg = self.channel_Intelligent_VCAResource_change(self.deviceInfo,
    #                                                                                         isSupportChal, "smart",
    #                                                                                         isRelative,
    #                                                                                         isOpenHeop, 1)
    #                     if not changeFlag:
    #                         self.VD_LOG_DEBUG(ip, changeMsg)
    #                         self.VD_LOG_DEBUG(ip, changeMsg)
    #
    #             ret = self.isapi_get('/ISAPI/Image/channels/%d/capabilities' % current_chan,
    #                                  path=[".//Shutter/ShutterLevel"],
    #                                  type=["attrib"],
    #                                  attrib=['opt'])
    #             if not ret["success"]:
    #                 msg = f"通道{current_chan}获取快门能力失败，失败原因:{ret['msg']}"
    #                 self.VD_LOG_DEBUG(ip, msg)
    #                 return msg
    #
    #             ShutterLevelCapList = ret["data"][0][0].split(",")
    #             self.VD_LOG_DEBUG(ip, "ShutterLevel ", ShutterLevelCapList)
    #             # if int(ShutterLevelCapList[-1]) > ShutterLevelCap_max:
    #             #     ShutterLevelCap_max = int(ShutterLevelCapList[-1])
    #             return f"{ShutterLevelCapList[0]}s~{ShutterLevelCapList[-1]}s"
    #
    #         except Exception as e:
    #             self.VD_LOG_DEBUG(ip, traceback.print_exc())
    #             msg = f"设备通道{current_chan}获取快门能力出现异常:{str(e)}!"
    #             return msg

    # 快门，即曝光时间
    def getShutterCap(self):
        res = self.getAllShutter()
        if isinstance(res, list):
            return f"{res[0]}s~{res[-1]}s"
        return res

    # 慢快门
    def getSlowShutterCap(self):
        if self.devType == 'IPC':
            res = self.getAllShutter()
            if isinstance(res, list):
                for i in res:
                    if float(eval(i)) > (1/25):
                        return '支持' if not self.isOverseas else 'Yes'
                return '不支持' if not self.isOverseas else 'No'
            return res
        elif self.devType == 'IPD':
            url = '/ISAPI/Image/channels/1/capabilities'
            res = self.get(url)
            if '<DSS>' in res:
                return '支持' if not self.isOverseas else 'Yes'
            else:
                return '不支持' if not self.isOverseas else 'No'
        return '慢快门功能测试失败!'


    # 普通事件
    def getEventCap(self):
        # 暂未支持中英文输出
        # 获取普通事件能力，
        # 目前支持：移动侦测，遮挡报警，报警输入，异常（网线断开，IP地址冲突，非法访问，硬盘满，硬盘错误，异常重启），人脸侦测，场景变更侦测，音频异常侦测，虚焦侦测，视频质量诊断
        ip = self.ip
        try:
            ret = self.isapi_get('/ISAPI/Event/channels/capabilities',
                                 path=[".//ChannelEventCap/eventType"],
                                 type=["attrib"],
                                 attrib=['opt'])
            if not ret["success"]:
                msg = f"获取普通事件能力失败，失败原因:{ret['msg']}"
                self.VD_LOG_DEBUG(ip, msg)
                return msg
            # 这个字典为视频质量诊断的全部能力，当前只判断是否存在视频质量诊断不需要详细列出，后续有需要可以详细列出
            viedoExceptionDic = {"luma": "亮度异常",
                                 "chroma": "图像偏色",
                                 "snow": "雪花干扰",
                                 "streak": "条纹干扰",
                                 "freeze": "画面冻结",
                                 "sigLose": "信号丢失",
                                 "clarity": "清晰度异常",
                                 "jitter": "画面抖动",
                                 "block": "视频遮挡",
                                 "flowers": "花屏",
                                 "noise": "噪点",
                                 "ghost": "异常光斑检测",
                                 "purple": "紫边",
                                 "ICR": "ICR异常检测",
                                 "protectiveFilm": "保护膜未撕"
                                 }

            EventCapList = ret["data"][0][0].split(",")
            self.VD_LOG_DEBUG(ip, "EventCapList ", EventCapList, level='INFO')
            # 总信息
            resmsg = []
            # 异常内容
            temp = []

            # 判断普通事件
            for i in EventCapList:
                if i in self.EventCapDic:
                    resmsg.append(self.EventCapDic[i])

                # 判断视频质量诊断能力
                if i in viedoExceptionDic:
                    resmsg.append("视频质量诊断")

                # 判断异常内容包含哪些
                if i in self.ExceptionEventDic:
                    temp.append(self.ExceptionEventDic[i])

            # 判断音频升降检测,一般来说陡升/陡降都是一起出现
            if "音频异常侦测" in resmsg:
                ret = self.get("/ISAPI/Smart/AudioDetection/channels")
                if "<soundIntensityMutation>" and "<SteepFall>" in ret:
                    resmsg.append("音频陡升/陡降侦测")
                elif "<soundIntensityMutation>" in ret:
                    resmsg.append("音频陡升侦测")
                elif "<SteepFall>" in ret:
                    resmsg.append("音频陡降侦测")

            # 判断报警输入输出
            ret = self.get("/ISAPI/System/IO/inputs")
            if "</IOInputPortList>" not in ret:
                return "设备获取报警输入能力协议执行失败"
            if 'id' in ret:
                resmsg.append("报警输入")

            # 为了显示美观，最后添加异常内容
            if temp != []:
                resmsg.append(f"异常({','.join(temp)})")
            # 将最终值去重返回
            self.VD_LOG_DEBUG(ip, list(set(resmsg)), level='INFO')

            return ",".join(list(set(resmsg)))

        except Exception as e:
            self.VD_LOG_DEBUG(ip, traceback.print_exc())
            msg = f"设备获取普通事件能力出现异常:{str(e)}!"
            return msg

    # 数字变倍
    def getImageZoomLimitRatio(self):
        # 无需区分中英文
        # 只要判断设备支持变倍限制，表示支持数字变倍和光学变倍，默认值为光学变倍，其他值为数字变倍
        chans_num = self.chans_num
        ip = self.ip
        # 2、通道能力循环
        maxImageZoom = 0
        for current_chan in range(1, chans_num + 1):
            try:
                # 2.1判断设备当前通道能力
                chanlCapUrl = '/ISAPI/Image/channels/%d/capabilities' % current_chan
                cap = self.get(chanlCapUrl)
                if '</ImageChannel>' not in cap:
                    msg = f"通道{current_chan}获取图像配置能力协议执行失败:{self.get_subStatusCode(cap)}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg
                if '</ZoomLimitRatio>' not in cap:
                    continue
                else:
                    ret = self.isapi_get(chanlCapUrl,
                                         path=[".//ZoomLimit/ZoomLimitRatio"],
                                         type=["attrib"],
                                         attrib=['opt'])
                    ZoomLimitList = [int(i) for i in ret["data"][0][0].split(",")]
                    if max(ZoomLimitList) > maxImageZoom:
                        maxImageZoom = max(ZoomLimitList)

            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                msg = f"通道{current_chan}获取图像变倍限制能力异常，异常原因：{str(e)}"
                return msg
        if maxImageZoom != 0:
            return f'{maxImageZoom}x'
        else:
            return "所有通道均未读取到图像变倍限制能力"

    # 音频压缩标准
    def getAudioCodeType(self):
        # 无需区分中英文
        ip = self.ip
        try:
            chanlCapUrl = '/ISAPI/System/TwoWayAudio/channels/1/capabilities'
            cap = self.get(chanlCapUrl)
            if "</TwoWayAudioChannel>" not in cap:
                msg = f"设备不支持音频编码能力或者获取音频编码能力协议执行失败!"
                self.VD_LOG_DEBUG(ip, msg)
                return msg

            ret = self.isapi_get(chanlCapUrl,
                                 path=[".//audioCompressionType"],
                                 type=["attrib"],
                                 attrib=['opt'])
            if not ret['success']:
                msg = f"获取音频编码能力集协议执行失败:{ret['msg']}!"
                self.VD_LOG_DEBUG(ip, msg)
                return msg

            ##获取音频编码能力集列表
            audioCapList = ret['data'][0][0].replace(",", "/").replace("AAC", "AAC-LC").replace("alaw","").replace("ulaw","")
            audioCapList = audioCapList.split('/')
            audioCapList = list(set(audioCapList))
            self.VD_LOG_DEBUG(ip, audioCapList, level='INFO')
            return '/'.join(audioCapList)

        except Exception as e:
            self.VD_LOG_DEBUG(ip, str(e))
            return f"获取音频编码能力异常，异常原因：{str(e)}"

    # 音频压缩码率
    def getAudioaudioBitRate(self):
        # 无需区分中英文
        chans_num = self.chans_num
        errMsg = ""
        fixRateDict = {"G.722.1": "16 Kbps(G.722.1)",
                       "G.711": "64 Kbps(G.711)",
                       "G.726": "16 Kbps(G.726)",
                       "PCM": "8~48 Kbps(PCM)",
                       "AAC-LC":"16~64 Kbps(AAC-LC)"
                       }
        for chan in range(1, chans_num + 1):
            try:
                audioCapList = self.getAudioCodeType()
                # 部分可配的音频压缩标准通过协议获取音频压缩码率范围(MP212, ACC)，其余不可配的直接写死
                url = f'/ISAPI/System/Audio/channels/{chan}/dynamicCap'
                ret = self.get(url)
                if '<AudioDscriptorList>' not in ret:
                    errMsg += f'通道{chan}音频压缩码率协议获取异常！'
                    print(errMsg)
                    continue

                pattern = '<AudioDscriptor>(.*?)</AudioDscriptor>'
                List = re.findall(pattern, ret, re.S)
                audioBitRateDict = AutoVivification()
                for Type in List:
                    Max = 0
                    Min = 100000
                    print(Type)
                    if 'audioBitRate' in Type:
                        audioBitRate = re.findall('<audioBitRate opt="(.*?)">', Type, re.S)
                        audioBitRateList = []
                        for rate in audioBitRate:
                            audioBitRateList += rate.split(',')
                        Max = max([int(i) for i in audioBitRateList])
                        Min = min([int(i) for i in audioBitRateList])
                        codeType = re.findall('<audioCompressionType>(.*?)</audioCompressionType>', Type, re.S)[0]
                        if audioBitRateDict.get(codeType, -1) == -1:
                            audioBitRateDict[codeType]['Max'] = Max
                            audioBitRateDict[codeType]['Min'] = Min
                        else:
                            audioBitRateDict[codeType]['Max'] = max(audioBitRateDict[codeType]['Max'], Max)
                            audioBitRateDict[codeType]['Min'] = min(audioBitRateDict[codeType]['Min'], min)


                tmp_list = audioCapList.split('/')
                for i in tmp_list:
                    if i in audioBitRateDict:
                        fixStr = f'{audioBitRateDict[i]["Min"]}~{audioBitRateDict[i]["Max"]} Kbps'
                        fixStr = fixStr + f'({i})'
                        audioCapList = audioCapList.replace(i, fixStr)
                    else:
                        fixStr = fixRateDict.get(i, '')
                        if fixStr != '':
                            audioCapList = audioCapList.replace(i, fixStr)

                if len(audioCapList) != 0:
                    return audioCapList
                # audioCapList = audioCapList.replace("G.722.1", "16 Kbps (G.722.1)").replace("G.711ulaw", "64 Kbps (G.711)") \
                #     .replace("G.711alaw/", "").replace("MP2L2", "32 ~ 192 Kbps (MP2L2)").replace("G.726", "16 Kbps (G.726)") \
                #     .replace("AAC", "16 ~ 64 Kbps (AAC)").replace("PCM", "8 ~ 48 Kbps (PCM)") \
                #     .replace("MP3", "8 ~ 320 Kbps (MP3)")
            except:
                errMsg += f'通道{chan}音频压缩码率协议获取异常！'
        return '未能获取音频压缩码率!'

    # 码率控制
    def getVideoCompressionCodingrate(self):
        # 区分中英文
        chans_num = self.chans_num
        ip = self.ip
        # 2、通道能力循环
        VideoCompressionCodingrateList = []
        for current_chan in range(1, chans_num + 1):
            try:
                # 2.1判断设备当前通道主码流能力
                mainStreamUrl = '/ISAPI/Streaming/channels'
                ret = self.get(mainStreamUrl)
                if "<id>%d01</id>" % current_chan not in ret:
                    msg = f"通道{current_chan}没有主码流!"
                    self.VD_LOG_DEBUG(ip, msg)
                    continue

                chanlCapUrl = '/ISAPI/Streaming/channels/%d01/capabilities' % current_chan
                cap = self.get(chanlCapUrl)
                if "</StreamingChannel>" not in cap:
                    msg = f"通道{current_chan}主码流获取视频参数能力协议执失败:{self.get_subStatusCode(cap)}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

                if '</Video>' not in cap:
                    msg = f"通道{current_chan}主码流不支持视频功能!"
                    self.VD_LOG_DEBUG(ip, msg)
                    continue

                if '</videoResolutionWidth>' not in cap:
                    msg = f"通道{current_chan}主码流不支持分辨率功能!"
                    self.VD_LOG_DEBUG(ip, msg)
                    continue

                # 2.2.获取当前通道码率能力集
                ret = self.isapi_get(chanlCapUrl,
                                     path=[
                                         ".//Video/videoQualityControlType"
                                     ],
                                     type=["attrib"],
                                     attrib=['opt'])

                if not ret['success']:
                    msg = f"通道{current_chan}主码流获取码率类型能力集协议执行失败:{ret['msg']}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

                videoQualityControlType = ret['data'][0][0].split(",")
                for i in videoQualityControlType:
                    if i not in VideoCompressionCodingrateList:
                        VideoCompressionCodingrateList.append(i)

            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                return f"通道{current_chan}获取能力异常，异常原因：{str(e)}"

        resMsg = ','.join(VideoCompressionCodingrateList)
        return resMsg.replace("CBR", "定码率").replace("VBR", "变码率") if not self.isOverseas else resMsg

    # 区域裁剪
    def getregionClip(self):
        # 区分中英文
        ip = self.ip
        # 1.设备区域裁剪能力判断
        deviceCapUrl = "/ISAPI/System/capabilities"
        deviceCap = self.get(deviceCapUrl)
        if "</DeviceCap>" not in deviceCap:
            msg = f"协议获取设备系统能力协议执行失败:{self.get_subStatusCode(deviceCap)}!"
            self.VD_LOG_DEBUG(ip, msg)
            return msg

        if "</regionClip>" not in deviceCap:
            msg = "不支持"
            self.VD_LOG_DEBUG(ip, msg)
            return '不支持' if not self.isOverseas else 'No'
        return '支持' if not self.isOverseas else 'Yes'

    # 视频压缩码率
    def getvbrUpperCap(self):
        # 无需区分中英文
        chans_num = self.chans_num
        ip = self.ip
        # 2、通道能力循环
        max_vbrUpper = 0
        for current_chan in range(1, chans_num + 1):
            try:
                # 2.1判断设备当前通道主码流能力
                chanlCapUrl = '/ISAPI/Streaming/channels/%d01/capabilities' % current_chan
                cap = self.get(chanlCapUrl)
                if "</StreamingChannel>" not in cap:
                    msg = f"通道{current_chan}主码流获取视频参数能力协议执失败:{self.get_subStatusCode(cap)}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

                ret = self.isapi_get(chanlCapUrl,
                                     path=[".//id"],
                                     type=["attrib"],
                                     attrib=['opt'])
                if not ret['success']:
                    msg = f"获取码流数量协议执行失败:{ret['msg']}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg
                stream = ret['data'][0][0].split(",")
                if stream == []:
                    stream = [1]
                else:
                    stream = [int(i) for i in stream]
                for i in stream:
                    capurl = f"/ISAPI/Streaming/channels/{current_chan}0{i}/capabilities"
                    ret = self.isapi_get(capurl,
                                         path=[".//Video/constantBitRate"],
                                         type=["attrib"],
                                         attrib=['max'])
                    if not ret['success']:
                        msg = f"获取视频压缩码率集协议执行失败:{ret['msg']}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        return msg
                    if int(ret["data"][0][0]) > max_vbrUpper:
                        max_vbrUpper = int(ret["data"][0][0])

            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                return f"通道{current_chan}获取视频压缩码率能力异常，异常原因：{str(e)}"

        if max_vbrUpper != 0:
            return f"32 Kbps~{max_vbrUpper // 1024} Mbps"
        else:
            return "未读取到视频压缩码率"

    # 视频压缩标准
    def getVideoCodec(self):
        # 无需区分中英文
        chans_num = self.chans_num
        ip = self.ip
        # 2、通道能力循环
        resmsg = ""
        first_stream = []
        second_stream = []
        third_stream = []
        four_stream = []
        five_stream = []
        for current_chan in range(1, chans_num + 1):
            try:
                # 2.1判断设备当前通道主码流能力
                chanlCapUrl = '/ISAPI/Streaming/channels/%d01/capabilities' % current_chan
                cap = self.get(chanlCapUrl)
                if "</StreamingChannel>" not in cap:
                    msg = f"通道{current_chan}主码流获取视频参数能力协议执失败:{self.get_subStatusCode(cap)}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

                ret = self.isapi_get(chanlCapUrl,
                                     path=[".//id"],
                                     type=["attrib"],
                                     attrib=['opt'])
                if not ret['success']:
                    msg = f"获取码流数量协议执行失败:{ret['msg']}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg
                stream = ret['data'][0][0].split(",")
                if stream == []:
                    stream = [1]
                else:
                    stream = [int(i) for i in stream]
                for i in stream:
                    capurl = f"/ISAPI/Streaming/channels/{current_chan}0{i}/capabilities"
                    ret = self.isapi_get(capurl,
                                         path=[".//Video/videoCodecType"],
                                         type=["attrib"],
                                         attrib=['opt'])
                    if not ret['success']:
                        msg = f"获取视频压缩标准集协议执行失败:{ret['msg']}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        return msg
                    caplist = ret["data"][0][0].split(",")
                    if i == 1:
                        for j in caplist:
                            if j not in first_stream:
                                first_stream.append(j)
                        # 判断smart编码
                        smartUrl = '/ISAPI/Streaming/channels/%d01' % current_chan
                        cap = self.get(smartUrl)
                        if '</SmartCodec>' not in cap:
                            msg = "通道%d主码流不支持Smart视频编码功能!" % current_chan
                            print(msg)
                            continue
                        if 'H.264' in first_stream:
                            first_stream.append('Smart264')
                        if 'H.265' in first_stream:
                            first_stream.append('Smart265')

                    if i == 2:
                        for j in caplist:
                            if j not in second_stream:
                                second_stream.append(j)
                    if i == 3:
                        for j in caplist:
                            if j not in third_stream:
                                third_stream.append(j)
                    if i == 4:
                        for j in caplist:
                            if j not in four_stream:
                                four_stream.append(j)
                    if i == 5:
                        for j in caplist:
                            if j not in five_stream:
                                five_stream.append(j)

            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                return f"通道{current_chan}获取视频压缩标准能力异常，异常原因：{str(e)}"
        if first_stream != []:
            resmsg += f"主码流：{'/'.join(first_stream)}\r\n"
        if second_stream != []:
            resmsg += f"子码流：{'/'.join(second_stream)}\r\n"
        if third_stream != []:
            resmsg += f"第三码流：{'/'.join(third_stream)}\r\n"
        if four_stream != []:
            resmsg += f"第四码流：{'/'.join(four_stream)}\r\n"
        if five_stream != []:
            resmsg += f"第五码流：{'/'.join(five_stream)}\r\n"

        if first_stream == second_stream == third_stream == four_stream == five_stream == []:
            return "未读取到视频压缩标准"
        if self.isOverseas:
            resmsg = resmsg.replace('主码流', 'Main stream').replace('子码流', 'Sub-stream').replace(
                '第三码流', 'Third stream').replace('第四码流', 'Fourth stream').replace('第五码流', 'Fifth stream')
        return resmsg

    # 水尺识别
    def getIntelwatergauge(self, IntegSupportList):
        # 区分中英文
        if isinstance(IntegSupportList, list):
            if '水尺识别' in IntegSupportList:
                return "支持" if not self.isOverseas else 'Yes'
            else:
                resMsg = ",".join([self.Integdic.get(item, "") for item in list(set(IntegSupportList))])
                if "水尺识别" in resMsg:
                    return '支持' if not self.isOverseas else 'Yes'
                else:
                    return '不支持' if not self.isOverseas else 'No'
        elif isinstance(IntegSupportList, str):
            return IntegSupportList

    # 3D定位
    def getPTZPosition3D(self):
        # 支持中英文
        chans_num = self.chans_num
        ip = self.ip
        # 2、通道能力循环
        for current_chan in range(1, chans_num + 1):
            try:
                # 2.1判断设备当前通道3D定位能力
                chanlCapUrl = '/ISAPI/PTZCtrl/channels/%d/capabilities' % current_chan
                ret = self.get(chanlCapUrl)
                if "/PTZChanelCap" not in ret:
                    msg = f'通道{current_chan}获取PTZ能力协议执行失败:{ret["msg"]}!'
                    return msg
                if "true</isSupportPosition3D>" in ret:
                    return '支持' if not self.isOverseas else 'Yes'
            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                return f"通道{current_chan}获取设备PTZ能力异常，异常原因：{str(e)}"
        return '不支持' if not self.isOverseas else 'No'

    # 环境噪声过滤
    def getAudioNoiserCap(self):
        # 支持中英文
        chans_num = self.chans_num
        ip = self.ip
        # 2、通道能力循环
        for current_chan in range(1, chans_num + 1):
            try:
                audioUrl = '/ISAPI/System/TwoWayAudio/channels/%s' % current_chan
                audioDefaultData = self.get(audioUrl)
                if '</TwoWayAudioChannel>' not in audioDefaultData:
                    msg = f"通道{current_chan}获取音频默认参数协议执行失败:{self.get_subStatusCode(audioDefaultData)}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg
                if '</noisereduce>' in audioDefaultData:
                    return '支持' if not self.isOverseas else 'Yes'

            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                return f"通道{current_chan}获取环境噪声过滤能力异常，异常原因：{str(e)}"
        return '不支持' if not self.isOverseas else 'No'

    # 韦根
    def getWiegand(self):
        # 支持中英文
        chanlCapUrl = '/ISAPI/System/Wiegand/1/capabilities?format=json'
        cap = self.get(chanlCapUrl)
        if "WiegandCap" in cap:
            return '支持' if not self.isOverseas else '1 Wiegand'
        else:
            return '不支持' if not self.isOverseas else 'No'

    # 网页客户端语言
    def getWebLanguage(self):
        # 支持中英文
        Languagesdic = {"简体中文": "Simplified Chinese",
                        "繁体中文": "Traditional Chinese",
                        "英文": "English",
                        "俄语": "Russian",
                        "爱沙尼亚语": "Estonian",
                        "保加利亚语": "Bulgarian",
                        "匈牙利语": "Hungarian",
                        "希腊语": "Greek",
                        "德语": "German",
                        "意大利语": "Italian",
                        "捷克语": "Czech",
                        "斯洛伐克语": "Slovak",
                        "法语": "France",
                        "波兰语": "Polish",
                        "荷兰语": "Dutch",
                        "葡萄牙语": "Portuguese",
                        "西班牙语": "Spanish",
                        "罗马尼亚语": "Romanian",
                        "丹麦语": "Danish",
                        "瑞典语": "Swedish",
                        "挪威语": "Norwegian",
                        "芬兰语": "Finnish",
                        "克罗地亚语": "Croatian",
                        "斯洛文尼亚语": "Slovenian",
                        "塞尔维亚语": "Serbian",
                        "土耳其语": "Turkish",
                        "韩语": "Korean",
                        "繁体中文": "Traditional Chinese",
                        "泰语": "Thai",
                        "越南语": "Vietnamese",
                        "日语": "Japanese",
                        "拉脱维亚语": "Latvian",
                        "立陶宛语": "Lithuanian",
                        "巴西葡萄牙语": "Portuguese-Brasil",
                        "乌克兰语": "Ukrainian"
                        }
        EnLanguagesdic = {"简体中文": "Simplified Chinese",
                        "繁体中文": "Traditional Chinese",
                        "英文": "English",
                        "俄语": "Russian",
                        "爱沙尼亚语": "Estonian",
                        "保加利亚语": "Bulgarian",
                        "匈牙利语": "Hungarian",
                        "希腊语": "Greek",
                        "德语": "German",
                        "意大利语": "Italian",
                        "捷克语": "Czech",
                        "斯洛伐克语": "Slovak",
                        "法语": "French",
                        "波兰语": "Polish",
                        "荷兰语": "Dutch",
                        "葡萄牙语": "Portuguese",
                        "西班牙语": "Spanish",
                        "罗马尼亚语": "Romanian",
                        "丹麦语": "Danish",
                        "瑞典语": "Swedish",
                        "挪威语": "Norwegian",
                        "芬兰语": "Finnish",
                        "克罗地亚语": "Croatian",
                        "斯洛文尼亚语": "Slovenian",
                        "塞尔维亚语": "Serbian",
                        "土耳其语": "Turkish",
                        "韩语": "Korean",
                        "繁体中文": "Traditional Chinese",
                        "泰语": "Thai",
                        "越南语": "Vietnamese",
                        "日语": "Japanese",
                        "拉脱维亚语": "Latvian",
                        "立陶宛语": "Lithuanian",
                        "巴西葡萄牙语": "Portuguese (Brazil)",
                        "乌克兰语": "Ukrainian"
                        }

        webdic = {
            "中文": "简体中文",
            "繁體中文": "繁体中文",
            "English": "英文",
            "Русский": "俄语",
            "Eesti": "爱沙尼亚语",
            "Български": "保加利亚语",
            "Magyar": "匈牙利语",
            "Ελληνικά": "希腊语",
            "Deutsch": "德语",
            "Italiano": "意大利语",
            "Český": "捷克语",
            "Čeština": "捷克语",
            "Slovensko": "斯洛伐克语",
            "Slovenčina": "斯洛伐克语",
            "Français": "法语",
            "Polski": "波兰语",
            "Nederlands": "荷兰语",
            "Português": "葡萄牙语",
            "Español": "西班牙语",
            "Român": "罗马尼亚语",
            "Română": "罗马尼亚语",
            "Dansk": "丹麦语",
            "Svenska": "瑞典语",
            "Norsk": "挪威语",
            "Suomi": "芬兰语",
            "Hrvatski": "克罗地亚语",
            "Slovenščina": "斯洛文尼亚语",
            "Srpski": "塞尔维亚语",
            "Türkçe": "土耳其语",
            "한국어": "韩语",
            "繁体中文": "繁体中文",
            "ภาษาไทย": "泰语",
            "Tiếng Việt": "越南语",
            "日本語": "日语",
            "Latvijas": "拉脱维亚语",
            "Latviešu": "拉脱维亚语",
            "lietuviešu": "立陶宛语",
            "Lietuvių": "立陶宛语",
            "Português(Brasil)": "巴西葡萄牙语",
            "Portuguese(Brazil)": "巴西葡萄牙语",
            "Українська": "乌克兰语"
        }
        ip = self.ip

        url_list = ['/doc/assert/Languages.json', '/doc/i18n/Languages.json?']
        for url in url_list:
            cap = self.get(url)
            if "Languages" not in cap:
                return "未获取到网页客户端语言"
            else:
                break
        cap = json.loads(cap)
        if isinstance(cap, dict):
            langlist = cap["Languages"]
        else:
            return '获取网页客户端语言出错，请手动校验并联系工具维护人员！'

        if not self.isOverseas:
            res = ""
            for i in range(len(langlist)):
                if langlist[i]["name"] in webdic:
                    res += f",{i}_{langlist[i]['name']}({Languagesdic[webdic[langlist[i]['name']]]}-{webdic[langlist[i]['name']]})"
                else:
                    res += f",{i}_{langlist[i]['name']}"
            res = res[1:] if len(res) > 1 else res
            return res
        else:
            res = ""
            for i in range(len(langlist)):
                if langlist[i]["name"] in webdic:
                    res += f",{EnLanguagesdic[webdic[langlist[i]['name']]]}"
                else:
                    res += f",{langlist[i]['name']}"
            res = res[1:] if len(res) > 1 else res
            res = f"{len(langlist)} languages:" + res
            return res



    # 防破坏报警
    def getvandalProofAlarm(self):
        # 支持中英文
        chanlCapUrl = '/ISAPI/Compass/channels/1/vandalProofAlarm'
        cap = self.get(chanlCapUrl)
        if "</VandalProofAlarm>" in cap:
            return '支持' if not self.isOverseas else 'Yes'
        else:
            return '不支持' if not self.isOverseas else 'No'

    # 解码模式
    def getDECODEMODE(self):
        # 支持中英文
        chanlCapUrl = '/ISAPI/PTZCtrl/channels/1/capabilities'
        cap = self.get(chanlCapUrl)
        if "</PTZChanelCap>" in cap:
            return "获取解码模式协议执行失败"
        if "</flowCtrl>" in cap:
            ret = self.isapi_get(chanlCapUrl,
                                 path=[".//PTZRs485Para/flowCtrl"],
                                 type=["attrib"],
                                 attrib=['opt'])
            if not ret['success']:
                msg = f"获取解码模式协议执行失败:{ret['msg']}!"
                self.VD_LOG_DEBUG(self.ip, msg)
                return msg
            caplist = ret["data"][0][0].split(",")
            res = ""
            if "software" in caplist:
                if "hardware" in caplist:
                    return '支持硬解和软解' if not self.isOverseas else 'Support hardware decoding and software decoding'
                else:
                    return '只支持软解' if not self.isOverseas else 'Support software decoding'
        else:
            return '不支持' if not self.isOverseas else 'No'

    # 在线升级
    def getupgradeFlag(self):
        # 支持中英文
        chanlCapUrl = '/ISAPI/System/upgradeFlag'
        cap = self.get(chanlCapUrl)
        if "</upgradeFlag>" in cap:
            return '支持' if not self.isOverseas else 'Yes'
        else:
            return '不支持' if not self.isOverseas else 'No'

    # 云台旋转
    def getPTRZ(self):
        # 支持中英文
        chanlCapUrl = '/ISAPI/PTZCtrl/channels/1/capabilities'
        cap = self.get(chanlCapUrl)
        if "</PTZChanelCap>" in cap:
            return '支持' if not self.isOverseas else 'Yes'
        else:
            return '不支持' if not self.isOverseas else 'No'

    # H.264编码类型
    def getH264(self):
        # 支持中英文
        chans_num = self.chans_num
        ip = self.ip
        resmsg = []
        flag = 0
        codeDict = {"Baseline": "BaseLine",
                    "Main": "Main",
                    "High": "High"}
        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道主码流能力
                    chanlCapUrl = f'/ISAPI/Streaming/channels/{current_chan}01/capabilities'
                    cap = self.get(chanlCapUrl)
                    if "</StreamingChannel>" not in cap:
                        msg = f"通道{current_chan}主码流获取视频参数能力协议执失败:{self.get_subStatusCode(cap)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        return msg
                    ret = self.isapi_get(chanlCapUrl,
                                         path=[".//id"],
                                         type=["attrib"],
                                         attrib=['opt'])
                    if not ret['success']:
                        msg = f"获取码流信息协议执行失败:{ret['msg']}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        return msg
                    stream = ret['data'][0][0].split(",")
                    if stream == []:
                        stream = [1]
                    else:
                        stream = [int(i) for i in stream]
                    cap = []
                    linshicap = []
                    # 遍历所有码流，取所有码流并集
                    for i in stream:
                        capurl = f"/ISAPI/Streaming/channels/{current_chan}0{i}/capabilities"
                        ret = self.isapi_get(capurl,
                                             path=[".//Video/H264Profile"],
                                             type=["attrib"],
                                             attrib=['opt'])
                        if not ret['success']:
                            msg = f"获取H264能力协议执行失败:{ret['msg']}!"
                            self.VD_LOG_DEBUG(ip, msg)
                            return msg
                        h264_cap = ret["data"][0][0].split(",")
                        for j in h264_cap:
                            if j not in cap:
                                cap.append(codeDict[j])
                        if linshicap == []:
                            linshicap = cap
                        if set(linshicap) != set(cap):
                            flag = 1
                    resmsg += cap

                except Exception as e:
                    self.VD_LOG_DEBUG(ip, str(e))
                    return f"通道{current_chan}获取H264能力能力异常，异常原因：{str(e)}"
        except Exception as e:
            self.VD_LOG_DEBUG(ip, str(e))
            return f"设备获取H264能力能力异常，异常原因：{str(e)}"
        finally:
            res = ""
            resmsg = list(set(resmsg))
            if flag == 0:
                resdemo = [str(i + " Profile") for i in resmsg]
                return ",".join(resdemo)
            else:
                for i in range(len(resmsg)):
                    resdemo = [str(i + " Profile") for i in resmsg]
                    res += f"通道{i + 1}：{'/'.join(resdemo)}\r\n"
                return res

    # H.265编码类型
    def getH265(self):
        # 支持中英文
        chans_num = self.chans_num
        ip = self.ip
        resmsg = []
        flag = 0
        for current_chan in range(1, chans_num + 1):
            try:
                # 2.1判断设备当前通道主码流能力
                chanlCapUrl = f'/ISAPI/Streaming/channels/{current_chan}01/capabilities'
                cap = self.get(chanlCapUrl)
                if "</StreamingChannel>" not in cap:
                    msg = f"通道{current_chan}主码流获取视频参数能力协议执失败:{self.get_subStatusCode(cap)}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg
                ret = self.isapi_get(chanlCapUrl,
                                     path=[".//id"],
                                     type=["attrib"],
                                     attrib=['opt'])
                if not ret['success']:
                    msg = f"获取码流信息协议执行失败:{ret['msg']}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg

                stream = ret['data'][0][0].split(",")
                if stream == []:
                    stream = [1]
                else:
                    stream = [int(i) for i in stream]
                cap = []
                linshicap = []
                # 遍历所有码流，取所有码流并集
                for i in stream:
                    capurl = f"/ISAPI/Streaming/channels/{current_chan}0{i}/capabilities"
                    ret = self.isapi_get(capurl,
                                         path=[".//Video/H265Profile"],
                                         type=["attrib"],
                                         attrib=['opt'])
                    if not ret['success']:
                        msg = f"获取H265能力协议执行失败:{ret['msg']}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        return msg
                    h265_cap = ret["data"][0][0].split(",")
                    for j in h265_cap:
                        if j not in cap:
                            cap.append(j)
                    if linshicap == []:
                        linshicap = cap
                    if set(linshicap) != set(cap):
                        flag = 1
                resmsg.append(cap)

            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                return f"通道{current_chan}获取H265能力能力异常，异常原因：{str(e)}"
        res = ""
        if flag == 0:
            resdemo = [str(i + " Profile") for i in resmsg[0]]
            return ",".join(resdemo)
        else:
            for i in range(len(resmsg)):
                resdemo = [str(i + " Profile") for i in resmsg[i]]
                res += f"通道{i + 1}：{'/'.join(resdemo)}\r\n"
            return res

    # 同时预览路数
    def getSecurityPreviewNum(self):
        # 支持中英文
        ip = self.ip
        try:
            # 获取预览连接数能力
            chanlCapUrl = '/ISAPI/Security/previewLinkNum/capabilities'
            Cap = self.get(chanlCapUrl)
            if "</maxLinkNum>" not in Cap:
                msg = f"设备获取最大预览连接数协议执行失败:{self.get_subStatusCode(Cap)}!" + "请自行确认"
                self.VD_LOG_DEBUG(ip, msg)
                return msg
            ret = self.isapi_get(chanlCapUrl, path=["/PreviewLinkNum/maxLinkNum"], type=["attrib"], attrib=["max"])
            if not ret["success"]:
                msg = f"设备获取最大预览连接数协议执行失败:{self.get_subStatusCode(Cap)}!" + "请自行确认"
                self.VD_LOG_DEBUG(ip, msg)
                return msg
            maxNum = int(ret["data"][0][0])
            resMsg = f"最多{maxNum}路"
            resMsg_en = f"max support {maxNum}"
            self.VD_LOG_DEBUG(ip, resMsg)
            return resMsg if not self.isOverseas else resMsg_en
        except Exception as e:
            self.VD_LOG_DEBUG(ip, str(e))
            return PY_RUN_WRONG, f"获取设备协议接口能力异常，异常原因为：{str(e)}"

    # 用户管理
    def getSystemUserCap(self):
        '''用户管理
            不区分中英文，SPEC数据库未给出'''
        ip = self.ip
        try:
            contentMgmtCapUrl = '/ISAPI/Security/capabilities'
            ret = self.isapi_get(contentMgmtCapUrl, path=[".//supportUserNums"], type=["value"])
            if not ret["success"]:
                msg = f"设备获取最大用户数协议执行失败!"
                self.VD_LOG_DEBUG(ip, msg)
                return msg
            userNum = ret["data"][0][0]
            resMsg = f"最多{userNum}个用户，可分3级用户权限管理：管理员，操作员，普通用户"
            return resMsg
        except Exception as e:
            self.VD_LOG_DEBUG(ip, e)
            return f"设备获取用户管理能力异常，异常原因为：{str(e)}"

    # 其他功能
    def getCommonFunctions(self):
        '''其他功能
        支持区分中英文'''

        ip = self.ip
        chans_num = self.chans_num
        resMsg = {'一键恢复','防闪烁','心跳','flash日志','邮箱重置密码','像素计算器'} if not self.isOverseas else {
            'one-key reset', 'Anti-flicker', 'heartbeat', 'flash log', 'password reset via email', 'pixel counter'}
        errMsg = ''
        try:
            try:
                # 获取三码流，镜像，视频遮盖
                for current_chan in range(1, chans_num + 1):
                    # 三码流
                    chanlCapUrl = f'/ISAPI/Streaming/channels/{current_chan}01/capabilities'
                    cap = self.get(chanlCapUrl)
                    if "</StreamingChannel>" not in cap:
                        msg = f"通道{current_chan}主码流获取视频参数能力协议执失败:{self.get_subStatusCode(cap)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    ret = self.isapi_get(chanlCapUrl,
                                         path=[".//id"],
                                         type=["attrib"],
                                         attrib=['opt'])
                    if not ret['success']:
                        msg = f"通道{current_chan}获取码流信息协议执行失败:{ret['msg']}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    stream = ret['data'][0][0].split(",")
                    if stream == []:
                        stream = [1]
                    else:
                        stream = [int(i) for i in stream]
                    if len(stream) == 3:
                        if not self.isOverseas:
                            resMsg.add("三码流")
                        else:
                            resMsg.add("third stream")

                    # 镜像
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/capabilities'
                    cap = self.get(chanlCapUrl)
                    if "</ImageChannel>" not in cap:
                        msg = f"通道{current_chan}获取图像能力协议执失败:{self.get_subStatusCode(cap)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    if "</ImageFlip>" in cap:
                        if not self.isOverseas:
                            resMsg.add("镜像")
                        else:
                            resMsg.add("mirror")


                    # 视频遮盖
                    chanlCapUrl = f'/ISAPI/System/Video/inputs/channels/{current_chan}/privacyMask'
                    cap = self.get(chanlCapUrl)
                    if 'notSupport' in cap:
                        continue

                    if "</PrivacyMask>" not in cap:
                        msg = f"通道{current_chan}获取视频遮盖能力协议执失败:{self.get_subStatusCode(cap)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    if "</PrivacyMask>" in cap:
                        if not self.isOverseas:
                            resMsg.add("视频遮盖")
                        else:
                            resMsg.add("privacy mask")
            except Exception as e:
                msg = f"通道{current_chan}获取【其他功能】出错，异常原因：{str(e)}"
                self.VD_LOG_DEBUG(ip, msg)
                errMsg += msg
        except Exception as e:
            msg = f"通道获取【其他功能】出错，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if errMsg == '':
                return ','.join(resMsg)
            else:
                return ','.join(resMsg.add(errMsg))

    # 低功耗协议
    def getlowpower(self):
        resMsg = []
        try:
            # 获取ISUP5.0/萤石/国网B接口/I1规约/南网协议
            # ISUP5.0
            isupUrl = f'/ISAPI/System/Network/Ehome/capabilities'
            cap = self.get(isupUrl)
            if "</Ehome>" in cap:
                resMsg.append("ISUP5.0")
            # 萤石
            EZVIZUrl = f'/ISAPI/System/Network/EZVIZ/capabilities'
            cap = self.get(EZVIZUrl)
            if "</EZVIZ>" in cap:
                resMsg.append("萤石")
            # 国网B接口
            GRIDUrl = f'/ISAPI/System/Network/GRID/capabilities'
            cap = self.get(GRIDUrl)
            if "</GRIDServerCap>" in cap:
                resMsg.append("国网B接口")
            # 获取I1规约服务接入能力
            l1Url = f'/ISAPI/System/Network/transmissionI1Server/capabilities?format=json'
            cap = self.get(l1Url)
            if "TransmissionI1ServerCap" in cap:
                resMsg.append("I1规约")
            # 南网协议
            SouthernPowerUrl = f'/ISAPI/System/Network/southernPowerGridServer/capabilities?format=json'
            cap = self.get(SouthernPowerUrl)
            if "SouthernPowerGridServerCap" in cap:
                resMsg.append("南网协议")
            return "/".join(resMsg)
        except Exception as e:
            self.VD_LOG_DEBUG(self.ip, e)
            return f"设备获取用户管理能力异常，异常原因为：{str(e)}"

    # 主码流帧率分辨率
    def getsmainFrameAndColution(self):
        '''不区分中英文'''
        all_channel_stream_flag = self.all_channel_stream_flag
        all_channel_stream_msg = self.all_channel_stream_msg
        if not all_channel_stream_flag:
            return f"设备{self.ip}获取设备全部通道码流分辨率和帧率失败"
        else:
            resmsg = ""
            if len(all_channel_stream_msg) == 1:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        msg += f"{j}:{all_channel_stream_msg[i][j][0]}\r\n"
                    resmsg += f"{msg}"
                return re.sub('hz', ' Hz', resmsg)
            else:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        msg += f"{j}:{all_channel_stream_msg[i][j][0]}\r\n"
                    resmsg += f"通道{i+1}：\r\n{msg}"
                return re.sub('hz', ' Hz', resmsg)

    # 子码流帧率分辨率
    def getsubFrameAndColution(self):
        '''不区分中英文'''
        all_channel_stream_flag = self.all_channel_stream_flag
        all_channel_stream_msg = self.all_channel_stream_msg
        if not all_channel_stream_flag:
            return f"设备{self.ip}获取设备全部通道码流分辨率和帧率失败"
        else:
            resmsg = ""
            if len(all_channel_stream_msg) == 1:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        if len(all_channel_stream_msg[i][j]) >= 2:
                            msg += f"{j}:{all_channel_stream_msg[i][j][1]}\r\n"
                        else:
                            msg += f"通道{i+1}无子码流\r\n"
                    resmsg += f"{msg}"
                return re.sub('hz', ' Hz', resmsg)
            else:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        if len(all_channel_stream_msg[i][j]) >= 2:
                            msg += f"{j}:{all_channel_stream_msg[i][j][1]}\r\n"
                        else:
                            msg += f"通道{i+1}无子码流\r\n"
                    resmsg += f"通道{i + 1}：\r\n{msg}"
                return re.sub('hz', ' Hz', resmsg)

    # 第三码流帧率分辨率
    def getthirdFrameAndColution(self):
        '''不区分中英文'''
        all_channel_stream_flag = self.all_channel_stream_flag
        all_channel_stream_msg = self.all_channel_stream_msg
        if not all_channel_stream_flag:
            return f"设备{self.ip}获取设备全部通道码流分辨率和帧率失败"
        else:
            resmsg = ""
            if len(all_channel_stream_msg) == 1:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        if len(all_channel_stream_msg[i][j]) >= 3:
                            msg += f"{j}:{all_channel_stream_msg[i][j][2]}\r\n"
                        else:
                            msg += f"通道{i+1}无三码流\r\n"
                    resmsg += f"{msg}"
                return re.sub('hz', ' Hz', resmsg)
            else:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        if len(all_channel_stream_msg[i][j]) >= 3:
                            msg += f"{j}:{all_channel_stream_msg[i][j][2]}\r\n"
                        else:
                            msg += f"通道{i+1}无三码流\r\n"
                    resmsg += f"通道{i + 1}：\r\n{msg}"
                return re.sub('hz', ' Hz', resmsg)

    # 第四码流帧率分辨率
    def getfourFrameAndColution(self):
        '''不区分中英文'''
        all_channel_stream_flag = self.all_channel_stream_flag
        all_channel_stream_msg = self.all_channel_stream_msg
        if not all_channel_stream_flag:
            return f"设备{self.ip}获取设备全部通道码流分辨率和帧率失败"
        else:
            resmsg = ""
            if len(all_channel_stream_msg) == 1:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        if len(all_channel_stream_msg[i][j]) >= 4:
                            msg += f"{j}:{all_channel_stream_msg[i][j][3]}\r\n"
                        else:
                            msg += f"通道{i+1}无第四码流\r\n"
                    resmsg += f"{msg}"
                return re.sub('hz', ' Hz', resmsg)
            else:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        if len(all_channel_stream_msg[i][j]) >= 4:
                            msg += f"{j}:{all_channel_stream_msg[i][j][3]}\r\n"
                        else:
                            msg += f"通道{i+1}无第四码流\r\n"
                    resmsg += f"通道{i + 1}：\r\n{msg}"
                return re.sub('hz', ' Hz', resmsg)

    # 第五码流帧率分辨率
    def getFiveFrameAndColution(self):
        '''不区分中英文'''
        all_channel_stream_flag = self.all_channel_stream_flag
        all_channel_stream_msg = self.all_channel_stream_msg
        if not all_channel_stream_flag:
            return f"设备{self.ip}获取设备全部通道码流分辨率和帧率失败"
        else:
            resmsg = ""
            if len(all_channel_stream_msg) == 1:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        if len(all_channel_stream_msg[i][j]) >= 5:
                            msg += f"{j}:{all_channel_stream_msg[i][j][4]}\r\n"
                        else:
                            msg += f"通道{i+1}无第五码流\r\n"
                    resmsg += f"{msg}"
                return re.sub('hz', ' Hz', resmsg)
            else:
                for i in range(len(all_channel_stream_msg)):
                    msg = ""
                    for j in all_channel_stream_msg[i]:
                        if len(all_channel_stream_msg[i][j]) >= 5:
                            msg += f"{j}:{all_channel_stream_msg[i][j][4]}\r\n"
                        else:
                            msg += f"通道{i+1}无第五码流\r\n"
                    resmsg += f"通道{i + 1}：\r\n{msg}"
                return re.sub('hz', ' Hz', resmsg)

    # 海外ANPR车牌
    def getANPR(self):
        if "ANPR" in self.IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 车辆抓拍
    def getVehicleCapture(self):
        IntegSupportList = self.IntegSupportList
        if "hmsModelingContrast" in IntegSupportList or "roadDetection" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 岗位值守检测
    def getDismissionSleeping(self):
        IntegSupportList = self.IntegSupportList
        if "Dismission/Sleeping" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 高空抛物检测
    def getobjectsThrownDetection(self):
        IntegSupportList = self.IntegSupportList
        if "objectsThrownDetection" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 工服检测
    def getWorkingClothesDetection(self):
        IntegSupportList = self.IntegSupportList
        if "WorkingClothesDetection" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 垃圾检测
    def getGarbageDetection(self):
        IntegSupportList = self.IntegSupportList
        if "GarbageDetection" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 明厨亮灶
    def getKitchenHygieneDetection(self):
        IntegSupportList = self.IntegSupportList
        if "KitchenHygieneDetection" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 室内消防通道占用
    def getIndoorFirePassageDetection(self):
        IntegSupportList = self.IntegSupportList
        if "IndoorFirePassageDetection" in IntegSupportList:
            return '支持杂物检测' if not self.isOverseas else 'Yes'
        else:
            return '不支持' if not self.isOverseas else 'No'

    # 智慧城管
    def getcityManagement(self):
        IntegSupportList = self.IntegSupportList
        if "cityManagement" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 月台管理
    def getHPPeopleDetection(self):
        IntegSupportList = self.IntegSupportList
        if "HPPeopleDetection" in IntegSupportList or "HPVehicleDoorDetection" in IntegSupportList or "HPVehicleLoadingRate" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 热度图
    def getheatmap(self):
        IntegSupportList = self.IntegSupportList
        if "heatmap" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 全抓拍
    def getmixedTargetAllCapture(self):
        IntegSupportList = self.IntegSupportList
        if "mixedTargetAllCapture" in IntegSupportList:
            return '支持' if not self.isOverseas else 'Yes'
        else:
            return '不支持' if not self.isOverseas else 'No'

    # 车位管理
    def getPackingSpaceRecognition(self):
        IntegSupportList = self.IntegSupportList
        if "PackingSpaceRecognition" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 客流统计
    def getcameraGroupPeopleCounting(self):
        IntegSupportList = self.IntegSupportList
        if "cameraGroupPeopleCounting" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 人员密度
    def getPersonDensityDetection(self):
        IntegSupportList = self.IntegSupportList
        if "personDensityDetection" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 人数统计
    def getframesPeopleCounting(self):
        IntegSupportList = self.IntegSupportList
        if "framesPeopleCounting" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 智慧课堂
    def getSmartTeacherAndStudentBehavior(self):
        IntegSupportList = self.IntegSupportList
        if "studentBehavior" in IntegSupportList or "teacherBehavior" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # "SVC"
    def getSVC(self):
        # 支持中英文
        chans_num = self.chans_num
        ip = self.ip
        # 2、通道能力循环,获取码流数量
        resmsg = []
        for current_chan in range(1, chans_num + 1):
            try:
                streamUrl = f'/ISAPI/Streaming/channels/{current_chan}01/capabilities'
                ret = self.isapi_get(streamUrl,
                                     path=[".//id"],
                                     type=["attrib"],
                                     attrib=['opt'])
                if not ret['success']:
                    msg = f"获取通道码流能力执行失败:{ret['msg']}!"
                    self.VD_LOG_DEBUG(ip, msg)
                    return msg
                streamlist = ret['data'][0][0].split(",")
                if streamlist == []:
                    streamlist = [1]
                else:
                    streamlist = [int(x) for x in streamlist]
                self.VD_LOG_DEBUG(ip, streamlist)
                # 遍历码流，获取h264，h265能力
                for stream in streamlist:
                    capurl = f'/ISAPI/Streaming/channels/{current_chan}0{stream}/capabilities'
                    capret = self.isapi_get(capurl,
                                         path=[".//Video//videoCodecType"],
                                         type=["attrib"],
                                         attrib=['opt'])
                    if not capret['success']:
                        msg = f"获取解码能力执行失败:{capret['msg']}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        return msg
                    videoCodecTypeList = capret['data'][0][0].split(",")
                    if videoCodecTypeList == []:
                        continue
                    weithret = self.get(capurl)
                    if "</SVC>" in weithret:
                        return '支持' if not self.isOverseas else 'Yes'
                    # 不管什么解码能力协议中均存在SVC，携带SVC能力下发也是成功的，自动化无法判断界面，因此智能输出支持/不支持
                    # weithret = str(weithret)
                    # videoResolutionWidth = re.findall('>(.*?)</videoResolutionWidth>', weithret)[0]
                    # videoResolutionHeight = re.findall('>(.*?)</videoResolutionHeight>', weithret)[0]
                    # videoQualityControlType = re.findall('>(.*?)</videoQualityControlType>', weithret)[0]
                    # maxFrameRate = re.findall('>(.*?)</maxFrameRate>', weithret)[0]
                    # # 修改编码能力，查看是否支持SVC
                    # for videoCodecType in videoCodecTypeList:
                    #     changeurl = f"/ISAPI/Streaming/channels/{current_chan}0{stream}"
                    #     data = f'"1.0" encoding="UTF-8"?><StreamingChannel xmlns="http://www.hikvision.com/ver20/XMLSchema" version="2.0"><Video xmlns=""><videoCodecType>{videoCodecType}</videoCodecType><videoResolutionWidth>{videoResolutionWidth}</videoResolutionWidth><videoResolutionHeight>{videoResolutionHeight}</videoResolutionHeight><videoQualityControlType>{videoQualityControlType}</videoQualityControlType><maxFrameRate>{maxFrameRate}</maxFrameRate></Video></StreamingChannel>'
                    #     change_ret = self.put(changeurl, data)
                    #     if "OK" not in change_ret:
                    #         continue
                    #     time.sleep(0.5)
                    #     svcdata = f'"1.0" encoding="UTF-8"?><StreamingChannel xmlns="http://www.hikvision.com/ver20/XMLSchema" version="2.0"><Video xmlns=""><videoCodecType>{videoCodecType}</videoCodecType><videoResolutionWidth>{videoResolutionWidth}</videoResolutionWidth><videoResolutionHeight>{videoResolutionHeight}</videoResolutionHeight><videoQualityControlType>{videoQualityControlType}</videoQualityControlType><maxFrameRate>{maxFrameRate}</maxFrameRate><SVC><enabled>true</enabled><SVCMode>manual</SVCMode></SVC></Video></StreamingChannel>'
                    #     svc_ret = self.put(changeurl, svcdata)
                    #     if "OK" in svc_ret:
                    #         resmsg.append(f"{videoCodecType}支持")
                    #     time.sleep(0.5)

            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                return f"通道{current_chan}获取环境噪声过滤能力异常，异常原因：{str(e)}"
        resmsg = list(set(resmsg))
        if resmsg == []:
            return '不支持' if not self.isOverseas else 'No'

    # 人脸抓拍
    def getIntelfacesnap(self, IntegSupportList):
        '''
        判断人脸抓拍能力

        :params: 智能资源能力集 -> list
        :return: 支持/不支持/错误信息 -> str
        '''
        if isinstance(IntegSupportList, list):
            if '人脸抓拍' in IntegSupportList:
                return "支持" if not self.isOverseas else 'Yes'
            else:
                resMsg = ",".join([self.Integdic.get(item, "") for item in list(set(IntegSupportList))])
                if "人脸抓拍" in resMsg:
                    return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
                else:
                    return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

        elif isinstance(IntegSupportList, str):
            return IntegSupportList

    # 道路监控
    def getIntelRoadDetection(self, IntegSupportList):
        '''
                判断道路监控能力

                :params: 智能资源能力集 -> list
                :return: 支持/不支持/错误信息 -> str
        '''
        if isinstance(IntegSupportList, list):
            if '道路监控' in IntegSupportList:
                return "支持" if not self.isOverseas else 'yes'
            else:
                resMsg = ",".join([self.Integdic.get(item, "") for item in list(set(IntegSupportList))])
                if "道路监控" in resMsg:
                    return '支持' if not self.isOverseas else 'yes'
                else:
                    return '不支持' if not self.isOverseas else 'No'
        elif isinstance(IntegSupportList, str):
            return IntegSupportList

    # 比例变倍
    def getPTZproportionalpanCap(self):
        '''
                判断比例变倍

                :param: 设备信息
                :return:
        '''
        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        # 2、通道能力循环
        try:
            for current_chan in range(1, chans_num + 1):
                try:
                # 2.1判断设备当前通道图像参数切换能力
                    chanlCapUrl = '/ISAPI/Image/channels/%d/capabilities' % current_chan
                    ret = self.get(chanlCapUrl)
                    if "</ImageChannel>" not in ret:
                        msg = f'通道{current_chan}获取比例变倍协议执行失败:{self.get_subStatusCode(ret)}!'
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    if "</proportionalpan>" not in ret:
                        msg = f"设备通道{current_chan}不支持比例变倍功能!"
                        self.VD_LOG_DEBUG(ip, msg)
                        resList.append('不支持')
                    else:
                        resList.append('支持')
                except Exception as e:
                    msg =  f"通道{current_chan}获取设备比例变倍功能更异常，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取设备比例变倍功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                if '支持' in resList:
                    return '支持' if not self.isOverseas else 'Yes'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg

    # 预置点视频冻结
    def getPTZImageFreeze(self):
        '''获取设备预置点视频冻结能力'''

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        # 球机适用判断
        if self.devType != 'IPD':
            msg = "该设备类型不是IPD设备，此测试用例不适用!"
            self.VD_LOG_DEBUG(ip, msg, level='INFO')
            return '不支持' if not self.isOverseas else 'No'

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/imageFreeze'
                    ret = self.get(chanlCapUrl)
                    if "/ImageFreeze" not in ret:
                        resList.append("不支持")
                    else:
                        resList.append("支持")
                except Exception as e:
                    msg = f"通道{current_chan}获取预置点冻结功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取预置点冻结功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                if '支持' in resList:
                    return '支持' if not self.isOverseas else 'Yes'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg

    # 花样扫描
    def getPTZPatternNum(self):
        '''获取设备花样扫描能力
            支持中英文区分'''

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        # 球机适用判断
        if self.devType != 'IPD':
            msg = "该设备类型不是IPD设备，此测试用例不适用!"
            self.VD_LOG_DEBUG(ip, msg, level='INFO')
            return '不支持' if not self.isOverseas else 'No'

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    chanlCapUrl = f'/ISAPI/PTZCtrl/channels/{current_chan}/capabilities'
                    ret = self.get(chanlCapUrl)
                    if "</PTZChanelCap>" not in ret:
                        msg = f"设备获取通道{current_chan}PTZ能力协议执行失败:{self.get_subStatusCode(ret)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    if "</maxPatternNum>" not in ret:
                        msg = f"设备通道{current_chan}不支持花样扫描功能!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    retstr = re.findall(r"<maxPatternNum>(.*?)</maxPatternNum>", ret)
                    if retstr:
                        resList.append(int(retstr[0]))
                    else:
                        msg = f"设备通道{current_chan}获取花样扫描条数失败!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                except Exception as e:
                    msg = f"通道{current_chan}获取获取花样扫描条数失败，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取花样扫描条数失败，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                Max = max(resList)
                if Max > 0:
                    return str(Max) + '条' if not self.isOverseas else str(Max) + ' pattern scans'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg

    # 守望功能
    def getPTZparkactionCap(self):
        '''获取云台守望能力
            支持中英文设备区分'''

        parkactionCapDict = {
            "autoscan": "自动扫描",
            "framescan": "帧扫描",
            "randomscan": "随机扫描",
            "patrol": "巡航扫描",
            "pattern": "花样扫描",
            "preset": "预置点",
            "panoramascan": "全景扫描",
            "tiltscan": "垂直扫描",
            "combinedPath": "组合扫描",
            "sceneTrace": "场景巡航",
            "atuoscan": "区域扫描"
        }

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        # 球机适用判断
        if self.devType != 'IPD':
            msg = "该设备类型不是IPD设备，此测试用例不适用!"
            self.VD_LOG_DEBUG(ip, msg)
            return '不支持' if not self.isOverseas else 'notSupport'

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道守望能力
                    chanlCapUrl = f'/ISAPI/PTZCtrl/channels/{current_chan}/parkaction/capabilities'
                    ret = self.isapi_get(chanlCapUrl, path=[".//Action/ActionType"], type=["attrib"],
                                                attrib=["opt"])
                    if not ret["success"]:
                        msg = f'通道{current_chan}获取守望能力协议执行失败:{ret["msg"]}!'
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    ActionTypeList = ret["data"][0][0].split(",")
                    for i in ActionTypeList:
                        if i not in resList:
                            resList.append(i)
                except Exception as e:
                    msg = f"通道{current_chan}获取获取守望功能能力集失败，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取守望功能能力集失败，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                resList = [parkactionCapDict[item] for item in resList] if not self.isOverseas else resList
                return ','.join(resList)
            else:
                return errMsg

    # 巡航扫描
    def getPTZPatrolNum(self):
        '''获取设备巡航扫描能力
            支持区分中英文设备'''
        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        # 球机适用判断
        if self.devType != 'IPD':
            msg = "该设备类型不是IPD设备，此测试用例不适用!"
            self.VD_LOG_DEBUG(ip, msg)
            return '不支持' if not self.isOverseas else 'No'

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    chanlCapUrl = f'/ISAPI/PTZCtrl/channels/{current_chan}/capabilities'
                    ret = self.get(chanlCapUrl)
                    if "</PTZChanelCap>" not in ret:
                        msg = f"设备获取通道{current_chan}PTZ能力协议执行失败:{self.get_subStatusCode(ret)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    if "</maxPatrolNum>" not in ret:
                        msg = f"设备通道{current_chan}不支持巡航扫描功能!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    retstr = re.findall(r"<maxPatrolNum>(.*?)</maxPatrolNum>", ret)
                    if retstr:
                        resList.append(int(retstr[0]))
                    else:
                        msg = f"设备通道{current_chan}获取巡航扫描条数失败!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                except Exception as e:
                    msg = f"通道{current_chan}获取获取巡航扫描条数失败，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取巡航扫描条数失败，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                Max = max(resList)
                if Max > 0:
                    return str(Max) + '条' if not self.isOverseas else str(Max) + ' patrols'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg


    # 方位角信息显示
    def getPTZOSDDisplay(self):
        '''获取设备方位角信息能力
            支持中英文区分'''
        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        # 球机适用判断
        if self.devType != 'IPD':
            msg = "该设备类型不是IPD设备，此测试用例不适用!"
            self.VD_LOG_DEBUG(ip, msg, level='INFO')
            return '不支持' if not self.isOverseas else 'No'

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    chanlCapUrl = f'/ISAPI/PTZCtrl/channels/{current_chan}/PTZOSDDisplay'
                    ret = self.get(chanlCapUrl)
                    if "</azimuth>" not in ret:
                        resList.append("不支持")
                    else:
                        resList.append("支持")
                except Exception as e:
                    msg = f"通道{current_chan}获取方位角信息显示功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取方位角信息显示功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                if '支持' in resList:
                    return '支持' if not self.isOverseas else 'Yes'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg


    # 定时任务
    def getPTZTimeTaskList(self):
        '''获取设备定时任务能力
            支持中英文设备区分'''

        TimeTaskCapDict = {
            "disable": "关闭",
            "autoscan": "自动扫描",
            "framescan": "帧扫描",
            "randomscan": "随机扫描",
            "patrol": "巡航扫描",
            "pattern": "花样扫描",
            "preset": "预置点",
            "panoramascan": "全景扫描",
            "tiltscan": "垂直扫描",
            "combinedPath": "组合扫描",
            "sceneTrace": "场景巡航",
            "atuoscan": "区域扫描",
            "periodreboot": "球机重启",
            "periodadjust": "球机校验",
            "auxoutput": "辅助输出",
            "focus": "focus",
            "oneTimePatrol": "oneTimePatrol",
        }

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        # 球机适用判断
        if self.devType != 'IPD':
            msg = "该设备类型不是IPD设备，此测试用例不适用!"
            self.VD_LOG_DEBUG(ip, msg, level='INFO')
            return '不支持' if not self.isOverseas else 'notSupport'

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道PTZ能力
                    chanlCapUrl = f'/ISAPI/PTZCtrl/channels/{current_chan}/capabilities'
                    ret = self.get(chanlCapUrl)
                    if "</PTZChanelCap>" not in ret:
                        msg = f"设备获取通道{current_chan}PTZ能力协议执行失败:{self.get_subStatusCode(ret)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    if "</TimeTaskList>" not in ret:
                        msg = f"设备通道{current_chan}不支持定时任务功能!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    # ret = self.isapi_get(chanlCapUrl, path=[".//Action/ActionType"], type=["attrib"],
                    #                             attrib=["opt"])
                    ret = self.isapi_get(chanlCapUrl, path=[".//Task/TaskType"], type=["attrib"],
                                         attrib=["opt"])
                    if not ret["success"]:
                        msg = f'通道{current_chan}获取定时任务能力协议执行失败:{ret["msg"]}!'
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    TimeTypeList = ret["data"][0][0].split(",")
                    for i in TimeTypeList:
                        if i == 'disable':
                            continue
                        if i not in resList:
                            resList.append(i)
                except Exception as e:
                    msg = f"通道{current_chan}获取获取定时任务能力集失败，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取定时任务能力集失败，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                resList = [TimeTaskCapDict[item] if item in TimeTaskCapDict else item for item in resList] if not self.isOverseas else resList
                return ','.join(resList)
            else:
                return errMsg


    # ROI
    def getVideoROICap(self):
        '''
            获取设备ROI能力，不区分通道
            :return: 具备【最多个ROI区域】的码流信息
        '''
        streamTypeStr = {
            1: '主码流',
            2: '子码流',
            3: '三码流',
            4: '四码流',
            5: '五码流',
            6: '六码流'
        }

        chalNum = self.deviceInfo["chalNum"]
        ip = self.deviceInfo["IP"]
        errMsg = ""
        Max_ROI = 0 # 最大ROI数量
        supportList = set() # 支持最大码流数的通道数

        try:
            # 1.通道循环，判断是否有普通监控，有则切换
            for current_chan in range(1, chalNum + 1):
                changeFlag, changeMsg = self.integ_channel_Intelligent_VCAResource_judeg_and_change(
                    deviceInfo=self.deviceInfo,
                    channel=current_chan,
                    vcaType='close',
                    isReturnErr=False,
                    sleepTime=5)
                if not changeFlag:
                    msg = f"由于部分设备三码流需要在普通监控智能下才有，所以在判断普通监控智能能力和切换时出现错误:{changeMsg}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
                    continue

            # 2.获取设备所有码流
            StreamUrl = '/ISAPI/Streaming/channels'
            ret = self.get(StreamUrl)
            if "</StreamingChannelList>" not in ret:
                msg = f"获取设备所有视频码流配置协议执行失败:{self.get_subStatusCode(ret)}!"
                self.VD_LOG_DEBUG(ip, msg)
                errMsg = msg
                return
            streamList = re.findall("<id>(.*?)</id>", ret, re.S)
            if not isinstance(streamList, list) or len(streamList) == 0:
                msg = "获取设备所有视频码流id失败!"
                self.VD_LOG_DEBUG(ip, msg)
                errMsg = msg
                return
            chalStreamNumMax = max([int(i.split('0')[1]) for i in streamList])

            # 3.码流循环
            for stream in streamList:
                # 3.1获取码流号
                errMsg = ""
                streamNum = stream.split("0")[0]
                streamId = stream.split("0")[1]
                try:
                    ret = self.isapi_get(f"/ISAPI/Smart/ROI/channels/{stream}/capabilities",
                                         path=[".//ROIRegionList"],
                                         type=["attrib"],
                                         attrib=['size'])
                    if not ret["success"]:
                        if 'notSupport' in ret['msg']:
                            continue
                        msg = f"通道{streamNum}{streamTypeStr[int(streamId)]}获取ROI的区域能力失败，失败原因:{ret['msg']},暂不支持ROI"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    ROIRegionNum = int(ret["data"][0][0])
                    if ROIRegionNum > Max_ROI:
                        Max_ROI = ROIRegionNum
                        supportList.clear()
                        supportList.add(stream) # 看这里要不直接索引字典变中文
                    elif Max_ROI == ROIRegionNum:
                        supportList.add(stream)
                    else:
                        continue
                except Exception as e:
                    # 报错
                    msg = f"通道{current_chan}获取ROI功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            # 报错
            msg = f"设备获取ROI功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            # 4.处理返回结果
            if len(supportList) == 0:
                if errMsg == '':
                    return '设备不支持ROI功能'
                else:
                    return errMsg
            else:
                curStream = [stream.split('0')[1] for stream in supportList]
                curStream_2 = list(set(curStream))
                curStream_2.sort(key = curStream.index) # 去重 set后词语顺序随机, 将元素顺序变为原始顺序
                if len(curStream_2) == chalStreamNumMax:
                    return f'支持每路码流分别设置{Max_ROI}个固定区域'
                elif len(curStream_2) == 1:
                    return f'支持{streamTypeStr[int(curStream[0])]}设置{Max_ROI}个固定区域'
                else:
                    tmp = ''.join([re.sub('码流', '', streamTypeStr[int(i)]) for i in curStream_2])
                    return f'支持{tmp}码流分别设置{Max_ROI}个固定区域'

    # 透雾
    def getImageDehaze(self):
        '''透雾是否支持
           支持中英文设备区分'''

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        errMsg = ''
        resList = []

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道能力
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/capabilities'
                    cap = self.get(chanlCapUrl)
                    if '</ImageChannel>' not in cap:
                        msg = f"通道{current_chan}获取图像参数能力协议执行失败:{self.get_subStatusCode(cap)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    if '</Dehaze>' in cap:
                        resList.append("支持")
                    else:
                        resList.append("不支持")

                except Exception as e:
                    msg = f"通道{current_chan}获取图像-透雾功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取图像-透雾功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                if '支持' in resList:
                    return '支持' if not self.isOverseas else 'Digital Defog'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg

    # 图像增强
    def getImageStrong(self):
        '''图像增强是否支持'''

        ImageStrongDic = {
            "BLC": "背光补偿",
            "HLC": "强光抑制",
            "EIS": "电子防抖",
            "NoiseReduce": "3D数字降噪",
            "Dehaze": "透雾",
            "LensDistortionCorrection": "畸变矫正",
            "corridor": "旋转"

        }

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = set()
        errMsg = ''
        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道能力
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/capabilities'
                    cap = self.get(chanlCapUrl)
                    if '</ImageChannel>' not in cap:
                        msg = f"通道{current_chan}获取图像参数能力协议执行失败:{self.get_subStatusCode(cap)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    if '</HLC>' in cap:
                        resList.add('HLC')

                    if '</BLC>' in cap:
                        resList.add('BLC')

                    if '</EIS>' in cap:
                        resList.add('EIS')

                    if '</NoiseReduce>' in cap:
                        resList.add('NoiseReduce')

                    # 2023.11.29根据于阳工最新的数据库，透雾单独写一个参数项
                    # if '</Dehaze>' in cap:
                    #     resList.add('Dehaze')

                    if '</LensDistortionCorrection>' in cap:
                        resList.add('LensDistortionCorrection')

                    if '</corridor>' in cap:
                        resList.add('corridor')
                except Exception as e:
                    msg = f"通道{current_chan}获取获取图像增强能力集失败，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取图像增强能力集失败，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                resList = [ImageStrongDic[item] for item in resList] if not self.isOverseas else resList
                return ','.join(resList)
            else:
                return errMsg

    # 图像参数切换
    def getImagedisplayParamSwitch(self):
        '''图像参数切换能力是否支持
            支持区分中英文'''

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        errMsg = ''
        resList = []

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道图像参数切换能力
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/displayParamSwitch'
                    cap = self.get(chanlCapUrl)
                    if '</DisplayParamSwitch>' not in cap:
                        msg = f"通道{current_chan}不支持图像参数切换功能!"
                        self.VD_LOG_DEBUG(ip, msg)
                        resList.append("不支持")
                    else:
                        resList.append("支持")
                except Exception as e:
                    msg = f"通道{current_chan}获取图像参数功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取图像参数切换功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                if '支持' in resList:
                    return '支持' if not self.isOverseas else 'Yes'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg

    # 图像设置
    def getimageCap(self):
        '''获取图像设置能力'''

        imageDic = {
            "saturationLevel": "饱和度",
            "contrastLevel": "对比度",
            "brightnessLevel": "亮度",
            "SharpnessLevel": "锐度",
            "WhiteBalance": "白平衡",
            "WDR": "宽动态",
            "AGC": "AGC",
            "corridor": "走廊模式（旋转模式）",
            "ImageFlip": "镜像",
        }

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = set()
        errMsg = ''

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/capabilities'
                    cap = self.get(chanlCapUrl)
                    if '</ImageChannel>' not in cap:
                        msg = f"通道{current_chan}获取图像参数能力协议执行失败:{self.get_subStatusCode(cap)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    # 饱和度
                    if 'saturationLevel' in cap:
                        resList.add("saturationLevel")

                    # 对比度
                    if 'contrastLevel' in cap:
                        resList.add("contrastLevel")

                    # 亮度
                    if 'brightnessLevel' in cap:
                        resList.add("brightnessLevel")

                    # 锐度
                    if 'SharpnessLevel' in cap:
                        resList.add("SharpnessLevel")

                    # 白平衡
                    if 'WhiteBalance' in cap:
                        resList.add("WhiteBalance")

                    # 宽动态
                    if 'WDR' in cap:
                        resList.add("WDR")

                    # 镜像
                    if '</ImageFlip>' in cap:
                        resList.add("ImageFlip")

                    # 旋转模式
                    if '</corridor>' in cap:
                        resList.add('corridor')

                    # 判断增益，需要先切换到日夜切换白天或者夜晚模式 GainLevel
                    if 'IrcutFilterType' in cap:
                        # 切换白天
                        IrcutFilterUrl = f'/ISAPI/Image/channels/{current_chan}/ircutFilter'
                        ret = self.get(IrcutFilterUrl)
                        if "</IrcutFilter>" not in ret:
                            msg = f'通道{current_chan}配置日夜切换模式为白天，前获取当前配置的协议执行失败:{self.get_subStatusCode(ret)}!'
                            errMsg += msg
                            self.VD_LOG_DEBUG(ip, msg)
                            continue
                        if "</nightToDayFilterLevel>" not in ret:
                            IRCUTFILTER_STRUCT = f"""
                            <?xml version="1.0" encoding="UTF-8"?>
                            <IrcutFilter version="2.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
                            <IrcutFilterType>day</IrcutFilterType>
                            <Schedule>
                            <scheduleType>day</scheduleType>
                            <TimeRange>
                            <beginTime>07:00:00</beginTime>
                            <endTime>18:00:00</endTime>
                            </TimeRange>
                            </Schedule>
                            </IrcutFilter>
                            """
                        else:
                            IRCUTFILTER_STRUCT = f"""
                            <?xml version="1.0" encoding="UTF-8"?>
                            <IrcutFilter version="2.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
                            <IrcutFilterType>day</IrcutFilterType>
                            <nightToDayFilterLevel>4</nightToDayFilterLevel>
                            <nightToDayFilterTime>5</nightToDayFilterTime>
                            <Schedule>
                            <scheduleType>day</scheduleType>
                            <TimeRange>
                            <beginTime>07:00:00</beginTime>
                            <endTime>18:00:00</endTime>
                            </TimeRange>
                            </Schedule>
                            </IrcutFilter>
                            """
                        ret = self.put(IrcutFilterUrl, IRCUTFILTER_STRUCT)

                        if 'OK' not in ret:
                            msg = f'通道{current_chan}配置日夜切换模式为白天协议执行失败:{self.get_subStatusCode(ret)}!'
                            errMsg += msg
                            self.VD_LOG_DEBUG(ip, msg)
                            continue

                        time.sleep(1)

                        # 重新获取
                        cap = self.get(chanlCapUrl)
                        if 'Gain' in cap:
                            resList.add("AGC")

                except Exception as e:
                    msg = f"通道{current_chan}获取图像设置功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取图像设置功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                resList = [imageDic[item] if item in imageDic else item for item in resList] if not self.isOverseas else resList
                return ','.join(resList)
            else:
                return errMsg

    # 图像防抖
    def getEIS_OIS(self):
        '''
        图像防抖
        支持中英文设备区分
        '''

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = set()
        errMsg = ''

        cnDict = {'EIS': '电子防抖', 'OIS': '光学防抖'}

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道能力
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/capabilities'
                    # "判断是否支持图像防抖"
                    cap = self.get(chanlCapUrl)

                    # 光学防抖
                    if '</OIS>' in cap:
                        resList.add('OIS')
                        # resList.add('光学防抖')

                    # 电子防抖
                    if '</EIS>' in cap:
                        resList.add('EIS')
                        # resList.add('电子防抖')

                except Exception as e:
                    msg = f"通道{current_chan}获取图像防抖功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取图像防抖功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            resList = list(set(resList))
            if len(resList) > 0:
                if self.isOverseas:
                    return '/'.join(resList)
                else:
                    return '/'.join([cnDict[i] for i in resList])
            else:
                if errMsg == '':
                    return '不支持' if not self.isOverseas else 'No'
                else:
                    return errMsg

    # 图片叠加
    def getImagOverlaye(self):
        '''图片叠加是否支持'''
        # 定义多级字典
        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        errMsg = ''
        resList = []

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道能力
                    chanlCapUrl = f'/ISAPI/System/Video/inputs/channels/{current_chan}/image'
                    cap = self.get(chanlCapUrl)
                    if '</ImageOverlay>' not in cap:
                        resList.append("不支持")
                    else:
                        resList.append("支持")
                except Exception as e:
                    msg = f"通道{current_chan}获取图片叠加功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取图片叠加功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                if '支持' in resList:
                    return '支持128 × 128 24位BMP图像叠加，可选择区域' if not self.isOverseas else 'Yes'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg

    # 日夜转换模式
    def getImageircutFilter(self):
        '''日夜模式切换是否支持
            支持区分中英文设备'''

        ircutFilterDic = {
            "day": "白天",
            "night": "夜晚",
            "auto": "自动",
            "schedule": "定时切换",
            "eventTrigger": "报警触发",
            "videoAuto": "视频自动",
            "darkFighterX": "黑光",
            "darkFighterXAuto": "黑光自动",
            "darkFighterXSchedule": "黑光定时",
            "colorVuAuto": "全彩自动"
        }

        ircutFilterEnDic = {
            "day": "Day",
            "night": "Night",
            "auto": "Auto",
            "schedule": "Schedule",
            "eventTrigger": "Alarm Trigger",
            "videoAuto": "Video Trigger",
            "darkFighterX": "Dark Fighter X",
            "darkFighterXAuto": "Dark Fighter X Auto",
            "darkFighterXSchedule": "Dark Fighter X Schedule",
            "colorVuAuto": "colorVuAuto"
        }

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道能力
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/capabilities'
                    cap = self.get(chanlCapUrl)
                    if '</ImageChannel>' not in cap:
                        msg = f"通道{current_chan}获取图像参数能力协议执行失败:{self.get_subStatusCode(cap)}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    if '</IrcutFilter>' not in cap:
                        msg = f"通道{current_chan}不支持日夜切换功能!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    # 2.2获取日夜切换模式能力集
                    ret = self.isapi_get(chanlCapUrl,
                                                path=[".//IrcutFilter/IrcutFilterType"],
                                                type=["attrib"],
                                                attrib=['opt'])

                    if not ret['success']:
                        msg = f"通道{current_chan}获取日夜切换模式能力集协议执行失败:{ret['msg']}!"
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    ##需要配置的场景模式定义列表
                    IrcutFilterTypeList = ret['data'][0][0].split(',')
                    resList += IrcutFilterTypeList
                except Exception as e:
                    msg = f"通道{current_chan}获取日夜切换能力集失败，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取日夜切换能力集，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                resList = list(set(resList))
                if not self.isOverseas:
                    resList = [ircutFilterDic[item] if item in ircutFilterDic else item for item in resList]
                else:
                    resList = [ircutFilterEnDic[item] if item in ircutFilterEnDic else item for item in resList]
                return ','.join(resList)
            else:
                if errMsg == '':
                    return '不支持' if not self.isOverseas else 'No'
                return errMsg


    # 区域曝光
    def getImageRegionalExposure(self):
        '''设备区域曝光能力
            支持区分中英文'''

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道图像参数切换能力
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/imageCap'
                    ret = self.get(chanlCapUrl)
                    if "</ImageCap>" not in ret:
                        msg = f'通道{current_chan}获取图像参数能力协议执行失败:{ret["msg"]}!'
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    if "true</isSupportRegionalExposure>" in ret:
                        resList.append("支持")
                    else:
                        resList.append("不支持")
                except Exception as e:
                    msg = f"通道{current_chan}获取区域曝光功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取区域曝光功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                if '支持' in resList:
                    return '支持' if not self.isOverseas else 'Yes'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg

    # 区域聚焦
    def getImageRegionalFocus(self):
        '''设备区域聚焦能力
            支持区分中英文'''

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    # 2.1判断设备当前通道图像参数切换能力
                    chanlCapUrl = f'/ISAPI/Image/channels/{current_chan}/imageCap'
                    ret = self.get(chanlCapUrl)
                    if "</ImageCap>" not in ret:
                        msg = f'通道{current_chan}获取图像参数能力协议执行失败:{ret["msg"]}!'
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue
                    if "true</isSupportRegionalFocus>" in ret:
                        resList.append("支持")
                    else:
                        resList.append("不支持")
                except Exception as e:
                    msg = f"通道{current_chan}获取区域聚焦功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取区域聚焦功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                if '支持' in resList:
                    return '支持' if not self.isOverseas else 'Yes'
                else:
                    return '不支持' if not self.isOverseas else 'No'
            else:
                return errMsg

    # 隐私保护
    def getPrivacyMaskCap(self):
        '''获取隐私保护能力集
            暂不支持中英文区分'''

        regionTypeDict = {'rectangle': '矩形',
                          'polygon': '多边形'}

        chanTypeDict = {1: '细节',
                        2: '全景',
                        3: '全景',
                        4: '全景',
                        5: '全景',}

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        errMsg = ''
        resList = []

        try:
            for current_chan in range(1, chans_num + 1):
                try:
                    chanlCapUrl = f'/ISAPI/System/Video/inputs/channels/{current_chan}/privacyMask/privacyMaskCap'
                    capRet = self.get(chanlCapUrl)
                    if 'notSupport' in capRet or '<statusCode>4</statusCode>' in capRet:
                        errMsg = '不支持'
                        continue

                    ret = self.isapi_get(chanlCapUrl, path=[".//privacyMaskRegionListNum", ".//supportRegionType", ".//maskTypeDscriptor", ".//videoPrivacyType"],
                                                      type=["attrib", "value", "attrib","value"],
                                                      attrib=["opt", "value", "opt","value"])
                    # 只有一个节点没获取到，ret['success']也为False，因此增加条件判断
                    if not ret['success'] and (len(ret['msg'].split(',')) == len(ret['data'])):
                    # if not ret['success']:
                        msg = f'通道{current_chan}获取隐私遮蔽协议执行失败:{ret["msg"]}!'
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        continue

                    # privacyCover为视频遮盖，privacyMask为隐私遮蔽
                    if ret['data'][3][0] == 'privacyCover':
                        errMsg = '仅支持视频遮盖'
                        continue

                    # 获取隐私区域配置数量
                    regionNumUrl = f'/ISAPI/System/Video/inputs/channels/{current_chan}/privacyMask/'
                    regionRet = self.isapi_get(regionNumUrl, path=[".//PrivacyMaskRegionList"],
                                                       type=["attrib"],
                                                       attrib=["size"])
                    if not regionRet['success']:
                        msg = f'通道{current_chan}获取隐私遮蔽区域配置协议执行失败:{regionRet["msg"]}!'
                        self.VD_LOG_DEBUG(ip, msg)
                        errMsg += msg
                        regionNum = -1
                    else:
                        regionNum = regionRet['data'][0][0]

                    # 写入结果[隐私遮蔽数量, 多边形区域， 马赛克， 支持颜色种类数]
                    # regionNum = 8 if '节点不存在' in ret['data'][0] else ret['data'][0]
                    regionType = 'polygon' if '节点不存在' in ret['data'][1] else str(ret['data'][1][0])
                    mosaicCap = 1 if 'mosaic' in ret['data'][2][0] else 0
                    maskTypeNum = 0 if '节点不存在' in ret['data'][2] else len(ret['data'][2][0].split(','))
                    resList.append([current_chan, regionNum, regionType, mosaicCap, maskTypeNum])
                except Exception as e:
                    msg = f"通道{current_chan}获取隐私保护能力集失败，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg
        except Exception as e:
            msg = f"设备获取隐私保护能力集失败，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) == 1:
                if str(resList[0][0]) == '1':
                    tmp1 = [f'最多{resList[0][1]}块', f'{regionTypeDict[resList[0][2]]}区域',
                           '支持马赛克' if resList[0][3] else '', '支持多种颜色设置' if resList[0][4] else '']
                    return ','.join(tmp1)
            elif len(resList) > 1:
                # 根据支持数量对全景通道的结果进行统计
                fullSceneRes = sorted(resList[1:], key=lambda x: (-x[1], x[2]))
                tmp1 = [f'【{chanTypeDict[resList[0][0]]}】', f'最多{resList[0][1]}块', f'{regionTypeDict[resList[0][2]]}区域',
                       '支持马赛克' if resList[0][3] else '', '支持多种颜色设置' if resList[0][4] else '']
                tmp1 = tmp1[0] + ','.join(tmp1[1:])
                tmp1 = re.sub(',,', ',', tmp1)

                tmp2 = [f'【{chanTypeDict[fullSceneRes[0][0]]}】', f'最多{fullSceneRes[0][1]}块', f'{regionTypeDict[fullSceneRes[0][2]]}区域',
                       '支持马赛克' if fullSceneRes[0][3] else '', '支持多种颜色设置' if fullSceneRes[0][4] else '']
                tmp2 = tmp2[0] + ','.join(tmp2[1:])
                tmp2 = re.sub(',,', ',', tmp2)
                return tmp2 + '\n' + tmp1
            else:
                return errMsg

    # 接口协议
    def getNetWorkApiCap(self):
        '''获取支持的api协议
        暂不支持中英文区分'''
        ApiDict = {
            "ONVIF": "开放型网络视频接口",
            "ISAPI": "ISAPI",
            "SDK": "SDK",
            "v2.0": "Ehome(v2.0)",
            "v4.0": "Ehome(v4.0)",
            "v5.0": "ISUP(5.0)",
            "GB28181": 'GB28181-2016',
            "OTAPServer": "OTAP",
            "SupportVideoImgDB": "视图库"
        }

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        errMsg = ''
        resList = []

        try:
            # 获取onvif能力
            chanlCapUrl = '/ISAPI/System/Network/Integrate/capabilities'
            onvifCap = self.get(chanlCapUrl)
            if "</ONVIF>" in onvifCap:
                resList.append("ONVIF")

            # 获取28181能力
            chanlCapUrl = '/ISAPI/System/Network/SIP/1/capabilities'
            Gb28181Cap = self.get(chanlCapUrl)
            if "</GB28181>" in Gb28181Cap:
                resList.append("GB28181")

            # 获取Ehome能力
            chanlCapUrl = '/ISAPI/System/Network/Ehome/capabilities'
            ret = self.get(chanlCapUrl)
            if "</Ehome>" in ret:
                protocolVersion = re.findall('<protocolVersion opt="(.*?)">', ret,
                                             re.S)[0]
                if protocolVersion:
                    resList += protocolVersion.split(",")

            # 获取视图库能力
            chanlCapUrl = '/ISAPI/System/Network/capabilities'
            ImgDBCap = self.get(chanlCapUrl)
            if '</isSupportVideoImgDB>' in ImgDBCap:
                resList.append("SupportVideoImgDB")

            # 获取otap的能力
            chanlCapUrl = '/ISAPI/System/Network/OTAPServerList/capabilities?format=json'
            otapCap = self.get(chanlCapUrl)
            if '</OTAPServerList>' in otapCap:
                resList.append("OTAPServer")

            # 获取SDK能力
            chanlCapUrl = '/ISAPI/Security/adminAccesses'
            otapCap = self.get(chanlCapUrl)
            if '<protocol>DEV_MANAGE</protocol>' in otapCap:
                resList.append("SDK")

        except Exception as e:
            msg = f"设备获取设备接口失败，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                resList = [ApiDict[item] if item in ApiDict else item for item in resList] if not self.isOverseas else resList
                return ','.join(resList)
            else:
                return errMsg

    # 客户端
    def getNetWorkEzvizCap(self):
        '''获取客户端能力
        支持中英文区分'''

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        try:
            contentMgmtCapUrl = '/ISAPI/System/Network/EZVIZ'
            EZVIZCap = self.get(contentMgmtCapUrl)
            if 'notSupport' in EZVIZCap or "invalidOperation" in EZVIZCap or '</EZVIZ>' not in EZVIZCap:
                resList.append('不支持')
            else:
                resList.append('支持')
        except Exception as e:
            msg = f"设备获取客户端能力集失败，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                if '支持' in resList:
                    return 'iVMS-4200,萤石云' if not self.isOverseas else 'iVMS-4200;Hik-Connect'
                else:
                    return 'iVMS-4200'
            else:
                if errMsg == '':
                    return 'iVMS-4200'
                else:
                    return errMsg

    # 网络存储
    def getNetWorkStrogeNas(self):
        '''获取NAS能力判断'''

        # 1、获取设备通道数
        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = ''
        errMsg = ''

        try:
            chanlCapUrl = '/ISAPI/ContentMgmt/Storage/nas/'
            ret = self.isapi_get(chanlCapUrl,
                                 path=[".//supportMountType"],
                                 type=["attrib"],
                                 attrib=["opt"])
            if not ret['success']:
                msg = f'通道获取网络存储协议执行失败:{ret["msg"]}!'
                self.VD_LOG_DEBUG(ip, msg)
                errMsg += msg
            else:
                resList = ret['data'][0][0].split(',')
        except Exception as e:
            msg = f"设备获取网络存储能力失败，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
               return 'NAS（' + ','.join(resList) + '均支持）' if not self.isOverseas else 'NAS（' + ','.join(resList)+ '）'
            else:
                if 'notSupport' in errMsg:
                    return '不支持' if not self.isOverseas else 'No'
                else:
                    return errMsg

    # 网络协议
    def getNetWorkThirApi(self):
        '''获取第三方网络协议'''

        chans_num = self.deviceInfo['chalNum']
        ip = self.deviceInfo["IP"]
        resList = []
        errMsg = ''

        try:
            # 默认具备的能力
            resList.append('ICMP')
            resList.append('RTP')
            resList.append('UDP')
            resList.append('IGMP')

            contentMgmtCapUrl = '/ISAPI/System/Network/interfaces/'
            IP6Cap = self.get(contentMgmtCapUrl)
            if '</IPAddress>' in IP6Cap:
                resList.append('TCP/IP')
            if 'ipv6Address' in IP6Cap:
                resList.append("IPv6")
            if '<PrimaryDNS>' in IP6Cap:
                resList.append("DNS")

            contentMgmtCapUrl = '/ISAPI/System/Network/capabilities/'
            NetCap = self.get(contentMgmtCapUrl)
            if '<isSupportHttps>true</isSupportHttps>' in NetCap:
                resList.append("HTTPS")
            if '<isSupportDdns>true</isSupportDdns>' in NetCap:
                resList.append("DDNS")
            if '<isSupportFtp>true</isSupportFtp>' in NetCap:
                resList.append("FTP")
            if '<isSupportUpnp>true</isSupportUpnp>' in NetCap:
                resList.append("UPnP")
            if '<isSupport802_1x>true</isSupport802_1x>' in NetCap:
                resList.append("802.1X")
            if '<isSupportPPPoE>true</isSupportPPPoE>' in NetCap:
                resList.append("PPPoE")
            if '<isSupportWebSocket>true</isSupportWebSocket>' in NetCap:
                resList.append("WebSocket")
            if '<isSupportWebSocketS>true</isSupportWebSocketS>' in NetCap:
                resList.append("WebSockets")
            if '<isSupportDHCPServer>' in NetCap:
                resList.append("DHCP")
            root = etree.XML(str(NetCap).encode("utf-8"))
            if root.xpath("//*[local-name()='isSupport']")[0].text:
                resList.append("SNMP")

            contentMgmtCapUrl = '/ISAPI/Security/adminAccesses/capabilities'
            NetCap = self.isapi_get(contentMgmtCapUrl, path=[".//protocol"],
                                           type=["attrib"], attrib=["opt"])
            NetCap = NetCap["data"][0][0]
            if 'HTTP' in NetCap:
                resList.append("HTTP")
            if 'RTSP' in NetCap:
                resList.append("RTSP")
            if 'Bonjour' in NetCap:
                resList.append("Bonjour")

            contentMgmtCapUrl = '/ISAPI/System/Network/qos/dscp'
            QoSret = self.get(contentMgmtCapUrl)
            if '</DSCP>' in QoSret:
                resList.append("QoS")

            # NTP
            ntpUrl = '/ISAPI/System/time/capabilities'
            ntpCap = self.get(ntpUrl)
            if 'NTP' in ntpCap:
                resList.append("NTP")

            # email
            emailUrl = '/ISAPI/System/Network/mailing/capabilities'
            emailCap = self.get(emailUrl)
            if '</smtp>' in emailCap:
                resList.append("SMTP")

            # SSL/TLS
            TLS_URL = '/ISAPI/Security/adminAccesses/capabilities'
            TLS_Cap = self.get(TLS_URL)
            if 'TLS' in TLS_Cap:
                resList.append("SSL/TLS")

            # IGMP

            # UDP

            # DHCP
            DHCP_URL = '/ISAPI/System/discoveryMode'
            DHCP_Cap = self.get(DHCP_URL)
            if 'DiscoveryMode' in DHCP_Cap:
                resList.append("DHCP")

            # RTCP
            for current_chan in range(1, chans_num + 1):
                try:
                    rtcpUrl = f'/ISAPI/Streaming/channels/{chans_num}/capabilities'
                    rtcpCap = self.get(rtcpUrl)
                    if '<isSupportRTCPCfg>true</isSupportRTCPCfg>' in rtcpCap:
                        resList.append("RTCP")
                        break
                except Exception as e:
                    msg = f"通道{current_chan}获取RTCP功能出错，异常原因：{str(e)}"
                    self.VD_LOG_DEBUG(ip, msg)
                    errMsg += msg

        except Exception as e:
            msg = f"设备获取网络协议功能异常，异常原因：{str(e)}"
            self.VD_LOG_DEBUG(ip, msg)
            errMsg += msg
        finally:
            if len(resList) > 0:
                return ",".join(list(set(resList)))
            else:
                return errMsg

    # 音频采样率
    def getAudioSamplingRate(self):
        ip = self.ip
        ans = []
        chans_num = self.deviceInfo['chalNum']
        errMsg = ""
        for chan in range(1, chans_num + 1):
            try:
                streamUrl = f'/ISAPI/System/Audio/channels/{chan}/dynamicCap'
                ret = self.get(streamUrl)
                if "</audioSamplingRate>" not in ret:
                    errMsg += f"通道{chan}未读取到音频采样率能力，请检查设备或联系工具组进行排查"
                    print(errMsg)
                    continue
                audioSamplingRatelist = re.findall('>(.*?)</audioSamplingRate>', ret)
                if audioSamplingRatelist == []:
                    errMsg += f"通道{chan}未读取到任何音频采样率，请联系工具组进行排查"
                    print(errMsg)
                    continue
                # audioSamplingRatelist = [int(x) for x in audioSamplingRatelist]
                # audioSamplingRatelist = sorted(audioSamplingRatelist)

                ans += audioSamplingRatelist
            except Exception as e:
                self.VD_LOG_DEBUG(ip, str(e))
                errMsg += f"通道{chan}获取音频采样率能力异常，异常原因：{str(e)}"
                print(errMsg)

        if len(ans) > 0:
            end_audioSamplingRatelist = []
            ans = sorted(list(set(ans)), key = lambda x: eval(x), reverse=False)
            for i in ans:
                end_audioSamplingRatelist.append(str(i) + "kHz")
            return "/".join(list(set(end_audioSamplingRatelist)))
        else:
            return errMsg

    # 带包装重量
    def getPackingSize(self):
        msg = '''该规格项请前往齐力前行平台查询：
                http://frontends.hikvision.com/#/demo/specTest/sizeWeightLib
                重量误差范围：【大于200g：±5%，小于200g：±10g】
                重量的范围误差超5%~10%提交建议，超10%提交缺陷！
                IPD产品的spec参数对外不提供带包装重量！'''
        return msg

    # 包装尺寸
    def getPackageSize(self):
        msg = '''该规格项请前往齐力前行平台查询：
                http://frontends.hikvision.com/#/demo/specTest/sizeWeightLib
                尺寸误差范围：【±5%】'''
        return msg

    # 设备重量
    def getWeight(self):
        msg = '''该规格项为【设备重量】;
                该规格项请前往齐力前行平台查询：
                http://frontends.hikvision.com/#/demo/specTest/sizeWeightLib
                重量误差范围：【大于200g：±5%，小于200g：±10g】
                重量的范围误差超5%~10%提交建议，超10%提交缺陷！'''
        return msg

    # 水平范围
    def getHorizontalExtent(self):
        msg = '''该规格项请前往齐力前行平台查询：
                http://frontends.hikvision.com/#/demo/specTest/ptzLib
                调节角度/云台功能误差范围：【±3°】'''
        return msg

    # 垂直范围
    def getVerticalRange(self):
        msg = '''该规格项请前往齐力前行平台查询：
                http://frontends.hikvision.com/#/demo/specTest/ptzLib
                调节角度/云台功能误差范围：【±3°】'''
        return msg

    # 水平速度
    def getHorizontalVelocity(self):
        msg = '''该规格项请前往齐力前行平台查询：
                http://frontends.hikvision.com/#/demo/specTest/ptzLib
                调节角度/云台功能误差范围：【±3°】'''
        return msg

    # 垂直速度
    def getVerticalVelocity(self):
        msg = '''该规格项请前往齐力前行平台查询：
                http://frontends.hikvision.com/#/demo/specTest/ptzLib
                调节角度/云台功能误差范围：【±3°】'''
        return msg

    # 调节角度
    def getAdjustAngle(self):
        msg = '''该规格项请前往齐力前行平台查询：
                http://frontends.hikvision.com/#/demo/specTest/ptzLib
                调节角度/云台功能误差范围：【±3°】'''
        return msg

    # 全结构化
    def getMixedTargetDetection(self):
        IntegSupportList = self.IntegSupportList
        if "mixedTargetDetection" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 智能交通
    def getIntelligentTraffic(self):
        IntegSupportList = self.IntegSupportList
        if "intelligentTraffic" in IntegSupportList:
            return '支持，需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 拥挤检测
    def getCongestionDetection(self):
        IntegSupportList = self.IntegSupportList
        if "congestionDetection" in IntegSupportList:
            return '支持，具体参数需手动比对' if not self.isOverseas else 'Yes, but manual comparison required'
        else:
            return '不支持，具体参数需手动比对' if not self.isOverseas else 'No, but manual comparison required'

    # 人脸比对
    def getfaceContrast(self):
        IntegSupportList = self.IntegSupportList
        if "faceContrast" in IntegSupportList:
            return '支持' if not self.isOverseas else 'Yes'
        else:
            return '不支持' if not self.isOverseas else 'No'
