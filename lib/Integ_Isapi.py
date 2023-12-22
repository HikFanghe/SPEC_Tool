# -*- coding: utf-8 -*-
"""
@Auth ： Fanghe.Lin
@File ：Integ_Isapi.py
@IDE ：PyCharm
@Time ： 2023/10/10 10:47
@Institution: Hikvision, China
"""
import datetime
import json
import re
import time
import traceback
import os, sys

import requests
import urllib3,hashlib
import threading
from lxml import etree
from requests.compat import urlparse
from requests.auth import HTTPDigestAuth

time_seq = time.strftime('[%Y-%m-%d-%H-%M-%S]', time.localtime(time.time()))

class Integ_Isapi():
    def __init__(self, deviceInfo = {'IP':None, 'U_NAME':'admin', 'P_WORD': 'abcd1234'}, username = 'admin', password = 'abcd1234'):

        # 设备ip
        self.ip = deviceInfo['IP']
        # 设备账号
        self.username = username
        # 设备密码
        self.password = password
        # 生成会话
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.username, self.password)

    def __del__(self):
        self.session.close()

    @staticmethod
    def VD_LOG_DEBUG(ip, *args, sep=' ', end='\n', file=None):
        '''公共打印log'''
        init_path = os.getcwd()
        # 获取被调用函数在被调用时所处代码行数
        line = sys._getframe().f_back.f_lineno
        # 获取被调用函数所在模块文件名
        file_name = sys._getframe(1).f_code.co_filename
        file_name = file_name.replace("\\", "/").split("/")[-1]
        # sys.stdout.write(f'"{__file__}:{sys._getframe().f_lineno}"  {x}\n')
        args = (str(arg) for arg in args)  # REMIND 防止是数字不能被join
        args_str = " ".join(args)
        # 打印到标准输出，并设置文字和背景颜色 sys.stdout.write(f'"{file_name}:{line}" {time.strftime("%H:%M:%S")} \033[0;94m{"".join(
        # args)}\033[0m\n') # 36 93 96 94

        # time_seq = time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
        # init_path=os.path.abspath(os.path.dirname(__file__))
        # init_path=os.getcwd()
        try:
            os.makedirs(f"log\\{ip}")
        except FileExistsError:
            pass
        log_path_name = f"%s\\log\\{ip}\\log_%s_%s.txt" % (init_path, ip, time_seq)
        info = f'[{file_name}:{line}]{" " + args_str}\n'
        info = info.replace("\r\n", "\n")
        info_log = time_seq + info
        info_log = info_log.encode("gbk", errors="ignore").decode("gbk")
        print(info_log)

        with open(log_path_name, "a+") as f:
            f.write(info_log)
            sys.stdout.write(info)
            f.close()

    # 子类调用父类的方法更改init属性
    def integIsapi_setInit(self, username, password):
        # 设备账号
        self.username = username
        # 设备密码
        self.password = password
        # 生成会话
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.username, self.password)
    def judge_data_format(self, data):
        """判断报文的格式"""
        resultDict = {"XML": 0, "JSON": 1, "fileBytes": 2, "txt": 3, "other": 4}

        flag = False
        convertData = None

        try:
            # 判断是否为XML格式
            try:
                convertData = etree.XML(str(data).encode('utf-8'))
                flag = True
            except etree.XMLSyntaxError:
                flag = False

            if flag:
                return True, [resultDict["XML"], convertData]

            # 判断是否为JSON格式
            try:
                convertData = json.loads(data)
                flag = True
            except ValueError:
                flag = False

            if flag:
                return True, [resultDict["JSON"], convertData]

            # 判断报文是否为文件类型
            if type(b"\x00") == type(data):
                return True, [resultDict["fileBytes"], convertData]

            # 判断报文是否为txt文本
            if type("") == type(data):
                return True, [resultDict["txt"], data]

            return True, [resultDict["other"], data]
        except Exception as e:
            # self.my_print(traceback.format_exc())
            return False, f"将报文数据进行格式转换时出现异常:{str(e)}!"

    def get_subStatusCode(self, data=""):
        """获取设备返回报文中的的错误状态码"""
        try:
            # 判断报文的格式
            formatFlag, formatMsg = self.judge_data_format(data)
            if not formatFlag:
                # self.my_print(formatMsg)
                return ""
            if "Access Error: 404 -- Not Found" in data:
                return "该接口执行返回Access Error: 404 -- Not Found"
            if "subStatusCode" not in data:
                return ""

            if formatMsg[0] == 0:
                subStatusCode = formatMsg[1].xpath("//*[local-name()='subStatusCode']")
                return subStatusCode
            elif formatMsg[0] == 1:
                subStatusCode = formatMsg[1].get("subStatusCode")
                return subStatusCode
            else:
                return ""
        except Exception as e:
            # self.my_print(traceback.format_exc())
            # self.my_print(f"获取错误状态码失败:{str(e)}!")
            return ""

    def http_data_get(self, data=None, path_list=None, type_list=None, attrib_list=None):
        """
        实现xml或json数据的节点相关内容获取操作
        输入参数：
            data：要处理的xml或json数据
            path_list：查询路径，以列表传入
            type_list: 查询类型，包含element, value, attrib，分别代表节点、值、属性，以列表传入
            attrib_list：属性名，当查询类型为属性时，需传入属性名，以列表传入
        输出参数：
            {
                'success':True/False,
                'msg':'',
                'data':[]
            }
            其中：
            success为True时, data为各path对应的值或属性等（若对应节点不存在，则为该节点不存在的报错信息），[path1查询结果，path2查询结果……]
            success为False时, msg为错误信息, 只要有一个节点不存在，结果就是False
        """
        try:
            ret = {
                'success': True,
                'msg': '',
                'data': []
            }

            if not isinstance(path_list, list):
                ret['success'] = False
                ret['msg'] = '参数path_list必须为列表'
                return ret
            if not isinstance(type_list, list):
                ret['success'] = False
                ret['msg'] = '参数type_list必须为列表'
                return ret
            if not isinstance(attrib_list, list):
                ret['success'] = False
                ret['msg'] = '参数attrib_list必须为列表'
                return ret

            flag = True  # 返回结果
            result_list = []  # 返回内容
            error = []

            # 判断报文格式
            formatFlag, formatMsg = self.judge_data_format(data)
            if not formatFlag:
                ret['success'] = False
                ret['msg'] = f"解析报文信息之前判断报文格式失败:{formatMsg}"
                return ret

            if formatMsg[0] == 0:
                # 处理XML
                error_code = formatMsg[1].xpath(".//*[local-name()='subStatusCode']")
                if error_code:
                    # self.my_print(data)
                    ret['success'] = False
                    ret['msg'] = f"获取内容出错:{error_code[0].text}"
                    return ret

                if not path_list:
                    ret['data'] = data
                    return ret

                for index, path_item in enumerate(path_list):
                    xml_path = re.sub(r'/([^/][\w\.]*)', r"/*[local-name()='\1']", path_item)
                    # #self.my_print(u"xpath路径:" + xml_path)
                    result = formatMsg[1].xpath(xml_path)
                    # #self.my_print(result)
                    # self.my_print(f'type_list[{index}]={type_list[index]}')
                    if not result:
                        result_list.append(u"%s节点不存在" % path_item)
                        error.append("%s节点不存在" % path_item)
                        flag = False
                    elif type_list[index] == "element":
                        result_list.append(result)
                    elif type_list[index] == "value":
                        # #self.my_print('value')
                        value = []
                        for one in result:
                            if one.text:  # 节点内容非空
                                value.append(one.text)
                            else:  # 节点内容为空时返回空字符串
                                value.append('')
                        result_list.append(value)
                    elif type_list[index] == "attrib":
                        result_list.append([one.attrib.get(attrib_list[index]) for one in result])
                    else:
                        # self.my_print(data)
                        raise Exception(f'传入的参数type_list中存在不支持的值{type_list[index]}')
            elif formatMsg[0] == 1:
                for path_item in path_list:
                    # self.my_print("json路径:" + path_item)
                    json_temp = formatMsg[1]
                    path_json = path_item.split("/")
                    while "" in path_json:
                        path_json.remove("")
                    for item in path_json:
                        if isinstance(json_temp, list):
                            try:
                                json_temp = json_temp[int(item)]
                            except Exception as e:
                                # self.my_print(str(e))
                                error.append(str(e))
                                flag = False
                                break
                        elif isinstance(json_temp, dict):
                            json_temp = json_temp.get(item)
                        else:
                            flag = False
                            break
                        if json_temp is None:
                            flag = False
                            break
                    if json_temp is None:
                        result_list.append(u"%s节点内容为空！" % path_item)
                        error.append(u"%s节点内容为空！" % path_item)
                    else:
                        result_list.append(json_temp)
            else:
                ret["success"] = False
                ret['msg'] = f"该报文不属于XML/JSON格式，请确认!"
                return ret

            ret['success'] = flag
            ret['msg'] = ','.join(error)
            ret['data'] = result_list
            # self.my_print(f'ret={ret}')
            return ret
        except Exception as e:
            # self.my_print(traceback.format_exc())
            ret = {
                'success': False,
                'msg': f'报文解析出现异常：{str(e)}',
                'data': []
            }
            return ret

    def get(self, path, file_path=None, timeout=30, data=None):
        if 'https://' in path or 'http://' in path:
            url = path
        else:
            url = 'http://' + self.ip + path
        content = None
        isResSuc = 'F'
        # logfilepath = global_variable.LOGRESFILEPATH
        logfilepath = None
        get_time = str(datetime.datetime.now())[:19]
        for i in range(3):
            try:
                get_time = str(datetime.datetime.now())[:19]
                print('ISAPI [GET %s]' % (url))
                content = self.session.get(url,
                                           timeout=timeout,
                                           verify=False,
                                           data=data)
                self.content = content
                self.status_code = content.status_code
                if "configurationData" not in url:
                    # print(f"[Response {content.text}]")
                    pass
                ##判断是否为能力接口
                formatFlag, formatMsg = self.judge_data_format(content.text)
                if formatMsg[0] == 1:
                    if 'capabilities' in url:
                        if '<statusCode>' not in content.text and 'Access Error' not in content.text:
                            isResSuc = 'P'
                            break
                        elif 'notSupport' in content.text or 'invalidOperation' in content.text or 'Access Error' in content.text:
                            isResSuc = 'NA'
                            break
                        else:
                            continue
                    else:
                        if '<statusCode>' not in content.text and 'Access Error' not in content.text:
                            isResSuc = 'P'
                            break
                        elif "/ISAPI/PTZCtrl/channels/1/lockPTZ" in url and (
                                "notSupport" in content.text
                                or "invalidOperation" in content.text):
                            isResSuc = 'NA'
                            break
                else:
                    if 'capabilities' in url:
                        if 'statusCode' not in content.text and 'Access Error' not in content.text:
                            isResSuc = 'P'
                            break
                        elif 'notSupport' in content.text or 'invalidOperation' in content.text or 'Access Error' in content.text:
                            isResSuc = 'NA'
                            break
                        else:
                            continue
                    else:
                        if 'statusCode' not in content.text and 'Access Error' not in content.text:
                            isResSuc = 'P'
                            break
            except Exception as e:
                if i == 2:
                    print(traceback.format_exc())
                    if 'timed out' in str(e).lower() or 'timeout' in str(
                            e).lower():
                        msg = f'ISAPI [GET {url}]操作超时'
                    elif 'Failed to establish a new connection' in str(e):
                        msg = f'ISAPI [GET {url}]连接失败'
                    else:
                        msg = f'ISAPI [GET {url}]操作失败{e}'

                    # 组装报文
                    resdic = {
                        "httpType": "GET",  # 请求方式
                        "URL": url,  # 请求链接
                        "Status": isResSuc,  # 请求结果状态
                        "responseData": msg,  # 设备响应信息
                        "putDataType": "",  # 下发数据类型
                        "putData": None,  # 下发数据
                        "time": get_time  # 下发时间
                    }
                    # import json
                    start_time = time.time()
                    if logfilepath != None:
                        logfilepath.append(resdic)
                        # with open(logfilepath,"a+") as f:
                        #     f.writelines(json.dumps(resdic))
                        #     f.writelines("\n")
                        #     f.close()
                    print(time.time() - start_time)
                    raise Exception(msg)
            print("url %s try again more time %d" % (url, i))
            time.sleep(1)
        # 组装报文
        resdic = {
            "httpType": "GET",  # 请求方式
            "URL": url,  # 请求链接
            "Status": isResSuc,  # 请求结果状态
            "responseData": content.text,  # 设备响应信息
            "putDataType": "",  # 下发数据类型
            "putData": None,  # 下发数据
            "time": get_time  # 下发时间
        }
        # import json
        # print(resdic)
        # print(json.dumps(resdic).replace('\\"','"'))
        if logfilepath != None:
            logfilepath.append(resdic)
            # with open(logfilepath,"a+") as f:
            #     f.writelines(json.dumps(resdic))
            #     f.writelines("\n")
            #     f.close()
        if file_path is not None:
            file_content = content.content
            with open(file_path, 'wb') as f:
                f.write(file_content)
        self.VD_LOG_DEBUG(self.ip, 'ISAPI [GET %s]\r\n[Response %s]' % (url, content.text))
        content.encoding = 'utf-8'
        return content.text

    def get_stream(self, path, timeout=30):
        url = 'http://' + self.ip + path
        print('ISAPI [GET %s]' % (url))
        content = None
        for i in range(3):
            try:
                content = self.session.get(url,
                                           timeout=timeout,
                                           verify=False,
                                           stream=True)
                self.content = content
                self.status_code = content.status_code
                break
            except Exception as e:
                if i == 2:
                    print(traceback.format_exc())
                    if 'timed out' in str(e).lower() or 'timeout' in str(
                            e).lower():
                        msg = f'ISAPI [GET {url}]操作超时'
                    elif 'Failed to establish a new connection' in str(e):
                        msg = f'ISAPI [GET {url}]连接失败'
                    else:
                        msg = f'ISAPI [GET {url}]操作失败{e}'
                    raise Exception(msg)
                else:
                    time.sleep(1)
        return content

    def post(self, path, data, timeout=30, stream=False):
        url = 'http://' + self.ip + path
        # print('ISAPI [POST %s]' % (url))
        postData = None
        # logfilepath = global_variable.LOGRESFILEPATH
        logfilepath = None
        content = None
        isResSuc = 'F'
        get_time = str(datetime.datetime.now())[:19]
        for i in range(3):
            try:
                get_time = str(datetime.datetime.now())[:19]
                if not data:
                    self.VD_LOG_DEBUG(self.ip, 'ISAPI [POST %s]\r\n[PostData None]' % (url))
                    postData = None
                else:
                    if not type(b"\x00") == type(data):
                        self.VD_LOG_DEBUG(self.ip, 'ISAPI [POST %s]\r\n[PostData %s]' % (url, data))
                        if "\n" in data:
                            postData = data.replace("\n", "")
                        else:
                            postData = data
                    elif b'xmlns="http://www.hikvision.com/ver20/XMLSchema"' in data or b'<?xml version="1.0" encoding="UTF-8"?>' in data:
                        self.VD_LOG_DEBUG(self.ip,
                                     f'ISAPI [POST {url}]\r\n[PostData {data.decode()}]'
                                     )
                        postData = data.decode()
                    else:
                        try:
                            json.loads(data)
                            self.VD_LOG_DEBUG(self.ip, f'ISAPI [POST {url}]\r\n[PostData {data}]')
                            postData = data
                        except Exception as e:
                            self.VD_LOG_DEBUG(self.ip,
                                         'ISAPI [POST %s]\r\n[PostData is fileBytes]' %
                                         (url))
                            postData = 'fileBytes'
                if type(data) == type(''):
                    DATA = data.encode()
                else:
                    DATA = data
                content = self.session.post(url,
                                            DATA,
                                            timeout=timeout,
                                            verify=False,
                                            stream=stream)
                self.content = content
                self.status_code = content.status_code
                if stream:
                    return content
                # print('ISAPI [POST %s]\r\n[Response %s]' % (url, content.text))
                formatFlag, formatMsg = self.judge_data_format(content.text)
                if formatMsg[0] == 1:
                    JsonData = json.loads(content.text)
                    if JsonData.get('statusCode', '') == 1 or JsonData.get(
                            'statusCode', ''
                    ) == 7 or 'ok' in content.text or 'OK' in content.text or JsonData.get(
                        "errorCode", "") == 0:
                        isResSuc = 'P'
                        break
                else:
                    if '<statusCode>1</statusCode>' in content.text or '<statusCode>7</statusCode>' in content.text or 'ok' in content.text or 'OK' in content.text or '<errorCode>0</errorCode>' in content.text or '</reboot>' in content.text:
                        isResSuc = 'P'
                        break
                    elif "/ISAPI/System/Video/inputs/channels/1/VCAResource/test" in url:
                        isResSuc = 'P'
                        break

            except Exception as e:
                if i == 2:
                    print(traceback.format_exc())
                    if 'timed out' in str(e).lower() or 'timeout' in str(
                            e).lower():
                        msg = f'ISAPI [POST {url}]操作超时'
                    elif 'Failed to establish a new connection' in str(e):
                        msg = f'ISAPI [POST {url}]连接失败'
                    else:
                        msg = f'ISAPI [POST {url}]操作失败{e}'
                    # 组装报文
                    resdic = {
                        "httpType": "POST",  # 请求方式
                        "URL": url,  # 请求链接
                        "Status": isResSuc,  # 请求结果状态
                        "responseData": msg,  # 设备响应信息
                        "putDataType": "XML/JSON",  # 下发数据类型
                        "putData": postData,  # 下发数据
                        "time": get_time  # 下发时间
                    }
                    # import json
                    if logfilepath != None:
                        logfilepath.append(resdic)
                        # with open(logfilepath,"a+") as f:
                        #     f.writelines(json.dumps(resdic))
                        #     f.writelines("\n")
                        #     f.close()
                    raise Exception(msg)
            self.VD_LOG_DEBUG(self.ip, "url %s try again more time %d" % (url, i))
            time.sleep(1)

        # 组装报文
        resdic = {
            "httpType": "POST",  # 请求方式
            "URL": url,  # 请求链接
            "Status": isResSuc,  # 请求结果状态
            "responseData": content.text,  # 设备响应信息
            "putDataType": "XML/JSON",  # 下发数据类型
            "putData": postData,  # 下发数据 .decode("utf-8").replace("\n","")
            "time": get_time  # 下发时间
        }
        # import json
        # print(json.dumps(resdic).replace('\\',''))
        if logfilepath != None:
            logfilepath.append(resdic)
            # with open(logfilepath,"a+") as f:
            #     f.writelines(json.dumps(resdic))
            #     f.writelines("\n")
            #     f.close()
        return content.text

    def put(self, path, data, timeout=60, ResponseCode=False):
        url = 'http://' + self.ip + path
        putData = None
        # self.pathList
        # logfilepath = global_variable.LOGRESFILEPATH
        logfilepath = None
        # print('ISAPI [PUT %s]' % (url))
        content = None
        isResSuc = 'F'
        # content = self.session.put(url, data, timeout=timeout, verify=False)
        get_time = str(datetime.datetime.now())[:19]
        for i in range(3):
            try:
                get_time = str(datetime.datetime.now())[:19]
                if not data:
                    self.VD_LOG_DEBUG(self.ip, 'ISAPI [PUT %s]\r\n[PutData None]' % (url))
                    putData = None
                else:
                    if not type(b"\x00") == type(data):
                        # print('ISAPI [PUT %s]\r\n[PutData %s]' % (url, data))
                        if "\n" in data:
                            putData = data.replace("\n", "")
                        else:
                            putData = data
                    elif b'xmlns="http://www.hikvision.com/ver20/XMLSchema"' in data or b'<?xml version="1.0" encoding="UTF-8"?>' in data:
                        self.VD_LOG_DEBUG(self.ip,
                                     f'ISAPI [PUT {url}]\r\n[PutData {data.decode()}]')
                        postData = data.decode()
                    else:
                        try:
                            json.loads(data)
                            self.VD_LOG_DEBUG(self.ip, f'ISAPI [PUT {url}]\r\n[PutData {data}]')
                            postData = data
                        except Exception as e:
                           self.VD_LOG_DEBUG(self.ip, 'ISAPI [PUT %s]\r\n[PutData is fileBytes]' %
                                         (url))
                           postData = 'fileBytes'
                        # print(data)
                if type(data) == type(''):
                    DATA = data.encode()
                else:
                    DATA = data
                content = self.session.put(url,
                                           DATA,
                                           timeout=timeout,
                                           verify=False)
                self.content = content
                self.status_code = content.status_code
                # print('ISAPI [PUT %s]\r\n[Response %s]' % (url, content.text))
                ##判断报文格式是否为json字符串
                formatFlag, formatMsg = self.judge_data_format(content.text)
                if formatMsg[0] == 1:
                    JsonData = json.loads(content.text)
                    if JsonData.get('statusCode', '') == 1 or JsonData.get(
                            'statusCode', '') == 7:
                        isResSuc = 'P'
                        break
                else:
                    if '<statusCode>1</statusCode>' in content.text or '<statusCode>7</statusCode>' in content.text:
                        isResSuc = 'P'
                        break
            except Exception as e:
                if i == 2:
                    print(traceback.format_exc())
                    if 'timed out' in str(e).lower() or 'timeout' in str(
                            e).lower():
                        msg = f'ISAPI [PUT {url}]操作超时'
                    elif 'Failed to establish a new connection' in str(e):
                        msg = f'ISAPI [PUT {url}]连接失败'
                    else:
                        msg = f'ISAPI [PUT {url}]操作失败{e}'
                    # 组装报文
                    resdic = {
                        "httpType": "PUT",  # 请求方式
                        "URL": url,  # 请求链接
                        "Status": isResSuc,  # 请求结果状态
                        "responseData": msg,  # 设备响应信息
                        "putDataType": "XML/JSON",  # 下发数据类型
                        "putData": putData,  # 下发数据
                        "time": get_time  # 下发时间
                    }
                    # import json
                    if logfilepath != None:
                        logfilepath.append(resdic)
                        # with open(logfilepath,"a+") as f:
                        #     f.writelines(json.dumps(resdic))
                        #     f.writelines("\n")
                        #     f.close()
                    raise Exception(msg)
            self.VD_LOG_DEBUG(self.ip, "url %s try again more time %d" % (url, i))
            time.sleep(1)
        self.VD_LOG_DEBUG(self.ip, 'ISAPI [PUT %s]\r\n[Response %s]' % (url, content.text))
        # 组装报文
        resdic = {
            "httpType": "PUT",  # 请求方式
            "URL": url,  # 请求链接
            "Status": isResSuc,  # 请求结果状态
            "responseData": content.text,  # 设备响应信息
            "putDataType": "XML/JSON",  # 下发数据类型
            "putData": putData,  # 下发数据 .decode("utf-8").replace("\n","")
            "time": get_time  # 下发时间
        }
        # import json
        # print(resdic)
        # print(json.dumps(resdic))
        # print(json.dumps(resdic).replace('\\"','"'))
        if logfilepath != None:
            logfilepath.append(resdic)
            # with open(logfilepath,"a+") as f:
            #     f.writelines(json.dumps(resdic))
            #     f.writelines("\n")
            #     f.close()

        if ResponseCode:
            return content.status_code
        elif content.text != "":
            return content.text
        else:
            return content.status_code

    def delete(self, path, timeout=30):
        url = 'http://' + self.ip + path
        logfilepath = None
        content = None
        isResSuc = 'F'
        get_time = str(datetime.datetime.now())[:19]
        for i in range(3):
            try:
                get_time = str(datetime.datetime.now())[:19]
                print('ISAPI [DELETE %s]' % (url))
                content = self.session.delete(url,
                                              timeout=timeout,
                                              verify=False)
                self.content = content
                self.status_code = content.status_code
                print(f"[Reponse {content.text}]")
                ##判断报文格式是否为json字符串
                formatFlag, formatMsg = self.judge_data_format(content.text)
                if formatMsg[0] == 1:
                    JsonData = json.loads(content.text)
                    if JsonData.get('statusCode', '') == 1 or JsonData.get(
                            'statusCode', '') == 7:
                        isResSuc = 'P'
                        break
                else:
                    if '<statusCode>1</statusCode>' in content.text or '<statusCode>7</statusCode>' in content.text:
                        isResSuc = 'P'
                        break
            except Exception as e:
                if i == 2:
                    print(traceback.format_exc())
                    if 'timed out' in str(e).lower() or 'timeout' in str(
                            e).lower():
                        msg = f'ISAPI [DELETE {url}]操作超时'
                    elif 'Failed to establish a new connection' in str(e):
                        msg = f'ISAPI [DELETE {url}]连接失败'
                    else:
                        msg = f'ISAPI [DELETE {url}]操作失败{e}'
                    # 组装报文
                    resdic = {
                        "httpType": "DELETE",  # 请求方式
                        "URL": url,  # 请求链接
                        "Status": isResSuc,  # 请求结果状态
                        "responseData": msg,  # 设备响应信息
                        "putDataType": "XML/JSON",  # 下发数据类型
                        "putData": None,  # 下发数据
                        "time": get_time  # 下发时间
                    }
                    # import json
                    if logfilepath != None:
                        logfilepath.append(resdic)
                        # with open(logfilepath,"a+") as f:
                        #     f.writelines(json.dumps(resdic))
                        #     f.writelines("\n")
                        #     f.close()
                    raise Exception(msg)
            print("url %s try again more time %d" % (url, i))
            time.sleep(1)
        # 组装报文
        resdic = {
            "httpType": "DELETE",  # 请求方式
            "URL": url,  # 请求链接
            "Status": isResSuc,  # 请求结果状态
            "responseData": content.text,  # 设备响应信息
            "putDataType": "XML/JSON",  # 下发数据类型
            "putData": None,  # 下发数据 .decode("utf-8").replace("\n","")
            "time": get_time  # 下发时间
        }
        # import json
        # print(resdic)
        # print(json.dumps(resdic))
        # print(json.dumps(resdic).replace('\\"','"'))
        if logfilepath != None:
            logfilepath.append(resdic)
            # with open(logfilepath,"a+") as f:
            #     f.writelines(json.dumps(resdic))
            #     f.writelines("\n")
            #     f.close()
        return content.text

    def get_by_xpath(self, path, xpath):
        """
        :param path: ISAPI URL
        :param xpath: str or list ,xpath为标准格式
        :return: str or dict
        :example: get_by_xpath('/ISAPI/Smart/LineDetection/1', 'aa/bb/cc')
        """
        content = self.get(path)
        print("ISAPI [get_by_xpath get %s]\r\n[Response %s]" % (path, content))
        if 'Access Error: 401 -- Unauthorized' in str(content):
            raise Exception('GET %s fail: Access Error: 401 -- Unauthorized' %
                            path)
        if str(content) == '' or content is None:
            raise Exception('response of GET %s is null! ' % path)
        try:
            content_xml = etree.XML(str(content).encode('utf-8'))
        except Exception as e:
            print('get_by_xpath first content= ', content)
            raise Exception(e)
        if isinstance(xpath, str):
            elements = content_xml.xpath(xpath)
            if len(elements) == 0:
                print(f'response: {content}')
                raise Exception('not find element by xpath %s! ' % xpath)
            else:
                return elements[0]
        if isinstance(xpath, list):
            dict = {}
            for item_xpath in xpath:
                elements = content_xml.xpath(item_xpath)
                if len(elements) == 0:
                    print(f'response: {content}')
                    raise Exception('not find element by xpath %s! ' % xpath)
                else:
                    value = elements[0]
                    dict[item_xpath] = value
            return dict

    def set_by_xpath(self, path, xpath, value, timeout=30, index=0):
        """
        :param path: ISAPI URL
        :param xpath: str or list ,xpath为标准格式，修改节点内容定位到路径
        :return: str or dict
        :example: set_by_xpath('/ISAPI/Smart/LineDetection/1', 'aa/bb/cc', 'true')
        """
        content = self.get(path)
        print("ISAPI [set_by_xpath get %s]\r\n[Response %s]" % (path, content))

        if 'Access Error: 401 -- Unauthorized' in str(content):
            raise Exception('GET %s fail: Access Error: 401 -- Unauthorized' %
                            path)
        if str(content) == '' or content is None:
            raise Exception('response of GET %s is null! ' % path)
        try:
            content_xml = etree.XML(str(content).encode('utf-8'))
        except Exception as e:
            print('set_by_xpath first get content= ', content)
            raise Exception(e)
        if isinstance(xpath, str):
            elements = content_xml.xpath(xpath)
            if len(elements) == 0:
                print(f'response: {content}')
                raise Exception('xpath=' + xpath +
                                " is not in the response of 'GET %s'" % path)
            else:
                content_xml.xpath(xpath)[index].text = str(value)
        if isinstance(xpath, list):
            for item_xpath in xpath:
                if len(content_xml.xpath(item_xpath)) == 0:
                    print(f'response: {content}')
                    raise Exception('xpath=' + item_xpath +
                                    " is not in the response of 'GET %s'" %
                                    path)
                content_xml.xpath(item_xpath)[index].text = str(
                    value[xpath.index(item_xpath)])
        # print(etree.tostring(content_xml).decode("utf-8","ignore"))
        return self.put(path,
                        etree.tostring(content_xml).decode("utf-8", "ignore"),
                        timeout)

    def isapi_put(self, url, path=[], value=[], notExist='skip'):
        '''isapi的put操作设置指定url的节点值,支持xml和json格式（节点不存在时会忽略）
            参数:
                url
                path: 节点路径列表，路径格式由//、/以及节点名称组成（其中//为相对路径，/为绝对路径），
                    若为json格式，都仅支持绝对路径
                value: 节点值列表，与节点路径一一对应
                notExist: 是否允许传入的节点路径不存在
                    skip: 允许, 节点不存在时跳过该节点，继续设置其他节点，结果成功失败有put的返回内容决定
                    error: 不允许, 节点不存在时不执行put操作，结果返回失败
                    create: 节点不存在时创建，仅针对json，若xml则自动兼容skip跳过
            返回值：
                {
                    'success':True/False,
                    'msg':'',
                    'data':''
                }
                其中：
                success为True时, 说明执行了put操作且返回成功，data为put的返回内容
                success为False时, 说明未执行put操作，或PUT操作返回失败，data为put的返回内容
            举例：
                url = '/ISAPI/Intelligent/channels/%s/mixedTargetDetection/capturePicture?format=json' % str(1)
                ret = lib.isapi_put(url,['/MixedTargetCapturePicture/pictureTargetOverlapEnabled'],[True])
                url = '/ISAPI/Streaming/channels/103/regionClip'
                ret = lib.isapi_put(url,['//enabled','//videoResolutionWidth','//videoResolutionHeight'],['true','704','480'])
                if not ret['success']:
                    self.msg = ret['msg']
                    self.result = PY_RUN_WRONG
                    return False
        '''
        ret = {
            'success': True,
            'msg': '',
            'data': []
        }
        if not isinstance(path, list):
            ret['success'] = False
            ret['msg'] = '参数path必须为列表'
            return ret
        if not isinstance(value, list):
            ret['success'] = False
            ret['msg'] = '参数value必须为列表'
            return ret
        if path == []:
            ret['success'] = False
            ret['msg'] = '参数path不能为空列表'
            return ret
        if value == []:
            ret['success'] = False
            ret['msg'] = '参数value不能为空列表'
            return ret
        data = self.get(url)

        flag = True  # 返回结果
        result_list = []  # 返回内容
        error = []
        # xml_ret = self._isapi_is_xml(data)
        formatFlag, formatMsg = self.judge_data_format(data)
        if formatMsg[0] == 0:
            # 处理XML
            if 'subStatusCode' in data:
                error_code = formatMsg[1].xpath(".//*[local-name()='subStatusCode']")
                if error_code:
                    ret['success'] = False
                    ret['msg'] = u"获取内容出错:%s！" % (error_code[0].text)
                    return ret

            for index, path_item in enumerate(path):
                if '*[local-name()=' in path_item:
                    xml_path = path_item
                else:
                    xml_path = re.sub(r'/([^/][\w\.]*)', r"/*[local-name()='\1']", path_item)  # 转换成正规的xpath
                # print(u"xpath路径:" + xml_path)
                nodes = formatMsg[1].xpath(xml_path)  # xpath找到的节点
                # print(result)
                if not nodes:
                    error.append("%s节点内容为空！" % path_item)
                    flag = False
                else:
                    for i in range(nodes.__len__()):
                        nodes[i].text = str(value[index])
            data = etree.tostring(formatMsg[1])
        else:
            # json_ret = self._isapi_is_json(data)

            if not formatFlag:
                ret = {
                    'success': False,
                    'msg': u"返回内容不是XML/JSON格式！",
                    'data': []
                }
                return ret
            else:
                for index, path_item in enumerate(path):
                    print("json路径:" + path_item)
                    json_temp = formatMsg[1]
                    path_json = path_item.split("/")
                    path_str = 'json_ret'
                    if str(value[index]).lower() == 'true':
                        set_value = True
                    elif str(value[index]).lower() == 'fasle':
                        set_value = False
                    elif type(value[index]) == str:
                        set_value = f'"{value[index]}"'
                    else:
                        set_value = f'{value[index]}'

                    item_type_list = []
                    for item in path_json:
                        if item.isdigit():
                            item_type_list.append(int)
                        else:
                            item_type_list.append(str)
                    i = -1
                    for item in path_json:
                        i += 1
                        if item == '':
                            continue
                        if isinstance(json_temp, list):
                            if int(item) > json_temp.__len__() - 1:
                                if notExist == 'create' and item == json_temp.__len__() + 1:
                                    if i == len(path_json) - 1:
                                        json_temp.append(set_value)
                                    elif item_type_list[i + 1] == int:
                                        json_temp[item].append([])
                                    else:
                                        json_temp[item].append({})
                                else:
                                    error.append(f'路径为{path_item}的节点不存在')
                                    flag = False
                                    break
                            try:
                                json_temp = json_temp[int(item)]
                                path_str += f'[{int(item)}]'
                            except Exception as e:
                                print(str(e))
                                error.append(str(e))
                                flag = False
                                break
                        elif isinstance(json_temp, dict):
                            if item not in json_temp:
                                if notExist == 'create':
                                    if i == len(path_json) - 1:
                                        json_temp[item] = set_value
                                    elif item_type_list[i + 1] == int:
                                        json_temp[item] = []
                                    else:
                                        json_temp[item] = {}
                                else:
                                    error.append(f'路径为{path_item}的节点不存在')
                                    flag = False
                                    break
                            json_temp = json_temp.get(item)
                            path_str += f'["{item}"]'
                        else:
                            flag = False
                            break
                        if json_temp is None:
                            flag = False
                            break
                    if json_temp is None:
                        error.append(u"%s节点内容为空！" % path_item)
                    if flag:
                        assignment = path_str + f'={set_value}'
                        print(assignment)
                        exec(assignment)
                        print(eval(path_str))
                        data = json.dumps(formatMsg[1])
        put_ret = None
        if notExist in ['skip', 'create'] or flag:

            put_ret = self.put(url, data)
            print(f'data={data}')
            print(f'put_ret={put_ret}')
            if 'OK' or 'rebootRequired' in put_ret:
                print('返回成功')
                print(f'data={data}')
                ret['success'] = True
            else:
                print('返回失败')
                print(f'data={data}')
                ret['success'] = False
                if 'subStatusCode' in put_ret:
                    msg = f'PUT {url}失败, subStatusCode={self.get_subStatusCode(put_ret)}'
                else:
                    msg = f'PUT {url}失败，无返回内容'
                error.append(msg)
        else:
            ret['success'] = False
        ret['msg'] = ','.join(error)
        ret['data'] = put_ret
        print(f'ret={ret}')
        return ret

    def isapi_get(self, url, data=None, path=[], type=[], attrib=[]):
        """
            实现ISAPI-GET操作,并获取指定路径的节点内容或属性值
            输入参数：
                url: 通过ISAPI get操作的URL
                data：通过ISAPI get操作的数据
                path：查询路径，以列表传入，路径格式由//、/以及节点名称组成（其中//为相对路径，/为绝对路径）
                type: 查询类型，包含element, value, attrib，分别代表节点、值、属性，以列表传入
                attrib：属性名，当查询类型为属性时，需传入属性名，以列表传入
            输出参数：
                {
                    'success':True/False,
                    'msg':'',
                    'data':[]
                }
                其中：
                    success为True时, data为各path对应的值或属性等，[path1查询结果，path2查询结果……]
                    success为False时, msg为错误信息            举例：
                # xml
                url = '/ISAPI/ContentMgmt/channels/%s/cloudStorage/1' % self.dict['Chan']
                path_list = ["//V2.0/enabled","//V2.0/ipAddress","//V2.0/port"]
                type_list = ['value','value','value']
                ret = self.isapi_get(url, path=path_list, type=type_list)
                if ret['success']:
                    ret_data = ret['data']
                else:
                    self.msg = ret['msg']
                    self.result = PY_RUN_NT
                    return False
                enable = ret_data[0][0]
                ipAddress = ret_data[1][0]
                port = ret_data[2][0]

                # json
                cap_url = f'/ISAPI/Intelligent/channels/{channel}/mixedTargetDetection/capturePicOverlap/capabilities?format=json'
                ret = self.isapi_get(cap_url,path=['MixedTargetCapturePicOverlapCap/itemType/@opt','MixedTargetCapturePicOverlapCap/targetAttribute/@opt'],type=['value','value'])
                if not ret['success']:
                    self.msg = f'通道{channel}不支持混合目标检测的图片字符叠加项能力'
                    print(self.msg)
                    self.result = PY_RUN_NA
                    return False
                itemType_opt = ret['data'][0].split(',')
                targetAttribute_opt = ret['data'][1].split(',')
        """

        ret = self.get(url, data)
        # print(ret)
        return self.http_data_get(ret, path, type, attrib)

