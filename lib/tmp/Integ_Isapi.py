# encoding: utf-8
'''
@author: qianjin
@license: (C) Copyright 2013-2019, Node Supply Chain Manager Corporation Limited.
@contact: deamoncao100@gmail.com
@software: garner
@file: Integ_Isapi.py
@time: 2022/11/24 14:04
@desc:

'''
import datetime

import requests
import urllib3,hashlib
import threading
from requests.compat import urlparse, str
from lib.tmp.mtd_com_fun import *
def SHA256(str):
    sha256 = hashlib.sha256()
    sha256.update(str.encode('utf-8'))
    return sha256.hexdigest()

class MyHTTPDigestAuth():
    """Attaches HTTP Digest SHA256 Authentication to the given Request object."""
    def __init__(self, username, password):
        self.username = username
        self.password = password
        # Keep state in per-thread local storage
        self._thread_local = threading.local()

    def init_per_thread_state(self):
        # Ensure state is initialized just once per-thread
        if not hasattr(self._thread_local, 'init'):
            self._thread_local.init = True
            self._thread_local.last_nonce = ''
            self._thread_local.nonce_count = 0
            self._thread_local.chal = {}
            self._thread_local.pos = None
            self._thread_local.num_401_calls = None

    def build_digest_header(self, method, url):
        """
        :rtype: str
        """

        realm = self._thread_local.chal['realm']
        nonce = self._thread_local.chal['nonce']
        qop = self._thread_local.chal.get('qop')
        algorithm = self._thread_local.chal.get('algorithm')
        opaque = self._thread_local.chal.get('opaque')
        hash_utf8 = None

        if algorithm is None:
            _algorithm = 'MD5'
        else:
            _algorithm = algorithm.upper()
        # lambdas assume digest modules are imported at the top level
        if _algorithm == 'MD5' or _algorithm == 'MD5-SESS':

            def md5_utf8(x):
                if isinstance(x, str):
                    x = x.encode('utf-8')
                return hashlib.md5(x).hexdigest()

            hash_utf8 = md5_utf8
        elif _algorithm == 'SHA':

            def sha_utf8(x):
                if isinstance(x, str):
                    x = x.encode('utf-8')
                return hashlib.sha1(x).hexdigest()

            hash_utf8 = sha_utf8
        elif _algorithm == 'SHA-256':

            def sha256_utf8(x):
                if isinstance(x, str):
                    x = x.encode('utf-8')
                return hashlib.sha256(x).hexdigest()

            hash_utf8 = sha256_utf8

        KD = lambda s, d: hash_utf8("%s:%s" % (s, d))

        if hash_utf8 is None:
            return None

        # XXX not implemented yet
        entdig = None
        p_parsed = urlparse(url)
        #: path is request-uri defined in RFC 2616 which should not be empty
        path = p_parsed.path or "/"
        if p_parsed.query:
            path += '?' + p_parsed.query

        A1 = '%s:%s:%s' % (self.username, realm, self.password)
        A2 = '%s:%s' % (method, path)

        HA1 = hash_utf8(A1)
        HA2 = hash_utf8(A2)

        if nonce == self._thread_local.last_nonce:
            self._thread_local.nonce_count += 1
        else:
            self._thread_local.nonce_count = 1
        ncvalue = '%08x' % self._thread_local.nonce_count
        s = str(self._thread_local.nonce_count).encode('utf-8')
        s += nonce.encode('utf-8')
        s += time.ctime().encode('utf-8')
        s += os.urandom(8)

        cnonce = (hashlib.sha1(s).hexdigest()[:16])
        if _algorithm == 'MD5-SESS':
            HA1 = hash_utf8('%s:%s:%s' % (HA1, nonce, cnonce))

        if not qop:
            respdig = KD(HA1, "%s:%s" % (nonce, HA2))
        elif qop == 'auth' or 'auth' in qop.split(','):
            noncebit = "%s:%s:%s:%s:%s" % (nonce, ncvalue, cnonce, 'auth', HA2)
            respdig = KD(HA1, noncebit)
        else:
            # XXX handle auth-int.
            return None

        self._thread_local.last_nonce = nonce

        # XXX should the partial digests be encoded too?
        base = 'username="%s", realm="%s", nonce="%s", uri="%s", ' \
               'response="%s"' % (self.username, realm, nonce, path, respdig)
        if opaque:
            base += ', opaque="%s"' % opaque
        if algorithm:
            base += ', algorithm="%s"' % algorithm
        if entdig:
            base += ', digest="%s"' % entdig
        if qop:
            base += ', qop="auth", nc=%s, cnonce="%s"' % (ncvalue, cnonce)

        return 'Digest %s' % (base)

    def handle_redirect(self, r, **kwargs):
        """Reset num_401_calls counter on redirects."""
        if r.is_redirect:
            self._thread_local.num_401_calls = 1

    def handle_401(self, r, **kwargs):
        """
        Takes the given response and tries digest-auth, if needed.

        :rtype: requests.Response
        """

        if self._thread_local.pos is not None:
            # Rewind the file position indicator of the body to where
            # it was to resend the request.
            r.request.body.seek(self._thread_local.pos)
        s_auth = r.headers.get('www-authenticate', '')

        if 'digest' in s_auth.lower() and self._thread_local.num_401_calls < 2:

            self._thread_local.num_401_calls += 1
            pat = re.compile(r'digest ', flags=re.IGNORECASE)
            self._thread_local.chal = requests.utils.parse_dict_header(
                pat.sub('', s_auth, count=1))

            # Consume content and release the original connection
            # to allow our new request to reuse the same one.
            r.content
            r.close()
            prep = r.request.copy()
            requests.cookies.extract_cookies_to_jar(prep._cookies, r.request,
                                                    r.raw)
            prep.prepare_cookies(prep._cookies)

            prep.headers['Authorization'] = self.build_digest_header(
                prep.method, prep.url)
            _r = r.connection.send(prep, **kwargs)
            _r.history.append(r)
            _r.request = prep

            return _r

        self._thread_local.num_401_calls = 1
        return r

    def __call__(self, r):
        # Initialize per-thread state, if needed
        self.init_per_thread_state()
        # If we have a saved nonce, skip the 401
        if self._thread_local.last_nonce:
            r.headers['Authorization'] = self.build_digest_header(
                r.method, r.url)
        try:
            self._thread_local.pos = r.body.tell()
        except AttributeError:
            # In the case of HTTPDigestAuth being reused and the body of
            # the previous request was a file-like object, pos has the
            # file position of the previous body. Ensure it's set to
            # None.
            self._thread_local.pos = None
        r.register_hook('response', self.handle_401)
        r.register_hook('response', self.handle_redirect)
        self._thread_local.num_401_calls = 1

        return r

    def __eq__(self, other):
        return all([
            self.username == getattr(other, 'username', None),
            self.password == getattr(other, 'password', None)
        ])

    def __ne__(self, other):
        return not self == other

class EZVIZ_ISAPI():
    def __init__(self, dev_paras):

        #self.my_print = my_print

        # 设备IP
        self.ip = dev_paras["IP"]
        # 设备账号
        self.username = dev_paras["U_NAME"]
        # 设备密码
        self.password = dev_paras["P_WORD"]
        # 是否海外设备
        # self.isEnglish = True if dev_paras["IS_ENGLISH"] == "Y" else False
        # # 是否萤石物理确权
        # self.isPhysical = True if dev_paras["IF_Physical"] == "Y" else False
        # # 如果是萤石物理确权的则已添加的萤石账号用户令牌为
        # self.userToken = dev_paras["U_TOKEN"]
        #
        # # 当前使用的萤石账号
        # self.currentAccount = None
        # # 当前使用的appKey
        # self.appKey = None
        # # 当前使用的appSecret
        # self.appSecret = None
        # # 当前使用的accessToken
        # self.EZO_AccessToken = None
        # # 当前设备序列号
        # self.EZO_DeviceSerial = dev_paras["S_NUMBER"]
        # # 设备码流加密密码
        # self.validateCode = dev_paras["V_CODE"]
        # # 萤石账号添加设备是否成功
        # self.addDevFlag = False
        #
        # # 是否登录成功
        # self.IsLogin = False
        # # 登录描述信息
        # self.login_msg = ''
        #
        # # 中英文设备萤石接口的统一前缀
        # if not self.isEnglish:
        #     # 中文设备前缀
        #     # ISAPI透传前缀
        #     self.urlHead_isapi = "https://open.ys7.com/api/hikvision"
        #     # 萤石账户请求前缀
        #     self.urlHead_ezviz = "https://open.ys7.com/api/lapp"
        # else:
        #     # 英文设备前缀
        #     self.urlHead = "https://open.ys7.com/api/hikvision"
        #     self.urlHead_ezviz = "https://open.ys7.com/api/lapp"

        self.session = requests.Session()
        self.session.auth =HTTPDigestAuth(self.username, self.password)

    def __del__(self):
        self.session.close()

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
            except ValueError:
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
            #self.my_print(traceback.format_exc())
            return False, f"将报文数据进行格式转换时出现异常:{str(e)}!"

    def get_subStatusCode(self, data=""):
        """获取设备返回报文中的的错误状态码"""
        try:
            # 判断报文的格式
            formatFlag, formatMsg = self.judge_data_format(data)
            if not formatFlag:
                #self.my_print(formatMsg)
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
            #self.my_print(traceback.format_exc())
            #self.my_print(f"获取错误状态码失败:{str(e)}!")
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
                    #self.my_print(data)
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
                    #self.my_print(f'type_list[{index}]={type_list[index]}')
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
                        #self.my_print(data)
                        raise Exception(f'传入的参数type_list中存在不支持的值{type_list[index]}')
            elif formatMsg[0] == 1:
                for path_item in path_list:
                    #self.my_print("json路径:" + path_item)
                    json_temp = formatMsg[1]
                    path_json = path_item.split("/")
                    while "" in path_json:
                        path_json.remove("")
                    for item in path_json:
                        if isinstance(json_temp, list):
                            try:
                                json_temp = json_temp[int(item)]
                            except Exception as e:
                                #self.my_print(str(e))
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
            #self.my_print(f'ret={ret}')
            return ret
        except Exception as e:
            #self.my_print(traceback.format_exc())
            ret = {
                'success': False,
                'msg': f'报文解析出现异常：{str(e)}',
                'data': []
            }
            return ret

    # def http_data_put(self, url, data=None, path_list=None, value_list=None):
    #     """
    #     实现xml或json数据的节点相关内容获取操作
    #     输入参数：
    #         data：要处理的xml或json数据
    #         path_list：查询路径，以列表传入
    #         type_list: 查询类型，包含element, value, attrib，分别代表节点、值、属性，以列表传入
    #         attrib_list：属性名，当查询类型为属性时，需传入属性名，以列表传入
    #     输出参数：
    #         {
    #             'success':True/False,
    #             'msg':'',
    #             'data':[]
    #         }
    #         其中：
    #         success为True时, data为各path对应的值或属性等（若对应节点不存在，则为该节点不存在的报错信息），[path1查询结果，path2查询结果……]
    #         success为False时, msg为错误信息, 只要有一个节点不存在，结果就是False
    #     """
    #     try:
    #         ret = {
    #             'success': True,
    #             'msg': '',
    #             'data': []
    #         }
    #
    #         if not isinstance(path_list, list):
    #             ret['success'] = False
    #             ret['msg'] = '参数path_list必须为列表'
    #             return ret
    #         if not isinstance(value_list, list):
    #             ret['success'] = False
    #             ret['msg'] = '参数value_list必须为列表'
    #             return ret
    #
    #         if not path_list:
    #             putFlag, putMsg = self.put(url, data)
    #             if not putFlag:
    #                 ret['success'] = False
    #                 ret['msg'] = putMsg
    #                 return ret
    #             else:
    #                 ret['data'] = putMsg
    #                 return ret
    #
    #         flag = True  # 返回结果
    #         result_list = []  # 返回内容
    #         error = []
    #         xmlData = None
    #         jsonData = None
    #
    #         # 判断报文格式
    #         formatFlag, formatMsg = self.judge_data_format(data)
    #         if not formatFlag:
    #             ret['success'] = False
    #             ret['msg'] = f"解析报文信息之前判断报文格式失败:{formatMsg}"
    #             return ret
    #
    #         if formatMsg[0] == 0:
    #             # 处理XML
    #             xmlData = formatMsg[1]
    #             error_code = xmlData.xpath(".//*[local-name()='subStatusCode']")
    #             if error_code:
    #                 #self.my_print(data)
    #                 ret['success'] = False
    #                 ret['msg'] = f"获取内容出错:{error_code[0].text}"
    #                 return ret
    #
    #             for index, path_item in enumerate(path_list):
    #                 xml_path = re.sub(r'/([^/][\w\.]*)', r"/*[local-name()='\1']", path_item)
    #                 # #self.my_print(u"xpath路径:" + xml_path)
    #                 result = xmlData.xpath(xml_path)
    #                 # #self.my_print(result)
    #                 #self.my_print(f'type_list[{index}]={value_list[index]}')
    #                 if not result:
    #                     result_list.append(u"%s节点不存在" % path_item)
    #                     error.append("%s节点不存在" % path_item)
    #                     flag = False
    #                 else:
    #                     result[0].text = value_list[index]
    #         elif formatMsg[0] == 1:
    #             jsonData = formatMsg[1]
    #             for index, path_item in enumerate(path_list):
    #                 #self.my_print("json路径:" + path_item)
    #                 path_json = path_item.replace(".", "").split("/")
    #                 path_str = 'jsonData'
    #
    #                 for item in path_json:
    #                     path_str += f'[{item}]'
    #                 try:
    #                     #self.my_print(eval(path_str))
    #                 except Exception as e:
    #                     #self.my_print(str(e))
    #                     result_list.append(u"%s节点不存在" % path_item)
    #                     error.append(u"%s节点不存在！" % path_item)
    #                     continue
    #
    #                 set_value = f'"{value_list[index]}"'
    #                 assignment = path_str + f'={set_value}'
    #                 #self.my_print(assignment)
    #                 exec(assignment)
    #                 #self.my_print(eval(path_str))
    #         else:
    #             ret['success'] = False
    #             ret['msg'] = f"该报文不属于XML/JSON格式，请确认!"
    #             return ret
    #
    #         if not flag:
    #             ret['success'] = flag
    #             ret['msg'] = ','.join(error)
    #             ret['data'] = result_list
    #             #self.my_print(f'ret={ret}')
    #         else:
    #             if formatMsg[0] == 0:
    #                 putData = etree.tostring(xmlData)
    #             else:
    #                 putData = json.dumps(jsonData)
    #             putFlag, putMsg = self.isapi_put(url, putData)
    #             if not putFlag:
    #                 ret['success'] = False
    #                 ret['msg'] = putMsg
    #                 return ret
    #             else:
    #                 ret['data'] = putMsg
    #                 return ret
    #         return ret
    #     except Exception as e:
    #         #self.my_print(traceback.format_exc())
    #         ret = {
    #             'success': False,
    #             'msg': f'报文解析出现异常：{str(e)}',
    #             'data': []
    #         }
    #         return ret

    # def isapi_get_by_xpath(self, url, data=None, path=[], type=[], attrib=[]):
    #     """
    #     GET报文后去获取感兴趣的键的值或属性
    #     :param url:
    #     :param data:
    #     :param path:
    #     :param type:
    #     :param attrib:
    #     :return:
    #     """
    #     ret = {
    #         'success': True,
    #         'msg': '',
    #         'data': []
    #     }
    #
    #     getFlag, getMsg = self.isapi_get(url, data)
    #     if not getFlag:
    #         ret["success"] = False
    #         ret["msg"] = getMsg
    #         return ret
    #     return self.http_data_get(getMsg, path, type, attrib)
    #
    # def isapi_set_by_xpath(self, url, data=None, path=[], value=[]):
    #     """
    #     先GET获取相关报文再进行对应的键值修改下发
    #     :param url:
    #     :param data:
    #     :param path:
    #     :param type:
    #     :param attrib:
    #     :return:
    #     """
    #     ret = {
    #         'success': True,
    #         'msg': '',
    #         'data': []
    #     }
    #
    #     getFlag, getMsg = self.isapi_get(url, data)
    #     if not getFlag:
    #         ret["success"] = False
    #         ret["msg"] = getMsg
    #         return ret
    #     return self.http_data_put(url, getMsg, path, value)

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
                if formatMsg[0]==1:
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
        VD_LOG_DEBUG(self.ip,'ISAPI [GET %s]\r\n[Response %s]' % (url,content.text))
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
                    VD_LOG_DEBUG(self.ip,'ISAPI [POST %s]\r\n[PostData None]' % (url))
                    postData = None
                else:
                    if not type(b"\x00") == type(data):
                        VD_LOG_DEBUG(self.ip,'ISAPI [POST %s]\r\n[PostData %s]' % (url, data))
                        if "\n" in data:
                            postData = data.replace("\n", "")
                        else:
                            postData = data
                    elif b'xmlns="http://www.hikvision.com/ver20/XMLSchema"' in data or b'<?xml version="1.0" encoding="UTF-8"?>' in data:
                        VD_LOG_DEBUG(self.ip,
                            f'ISAPI [POST {url}]\r\n[PostData {data.decode()}]'
                        )
                        postData = data.decode()
                    else:
                        try:
                            json.loads(data)
                            VD_LOG_DEBUG(self.ip,f'ISAPI [POST {url}]\r\n[PostData {data}]')
                            postData = data
                        except Exception as e:
                            VD_LOG_DEBUG(self.ip,
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
            VD_LOG_DEBUG(self.ip,"url %s try again more time %d" % (url, i))
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

    def post_file(self,
                  path,
                  data,
                  filename,
                  filepath,
                  timeout=30,
                  binary_key='importImage'):  # 发送Data和File的混合数据
        '''将filepath对应的文件上传
        '''
        url = 'http://' + self.ip + path
        print('ISAPI [POST FILE %s]' % (url))
        content = None
        if type(data) == type(''):
            data = data.encode()
        for i in range(3):
            try:
                content = self.session.post(url,
                                            data,
                                            timeout=timeout,
                                            verify=False)
                self.content = content
                self.status_code = content.status_code
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
                    raise Exception(msg)
                else:
                    time.sleep(1)

        data[binary_key] = (filename, open(filepath, 'rb').read())
        encode_data = urllib3.encode_multipart_formdata(data)
        data = encode_data[0]
        content.headers['Content-Type'] = encode_data[1]
        content = self.session.post(url,
                                    data,
                                    headers=content.headers,
                                    timeout=timeout,
                                    verify=False)
        return content.text

    def post_file_by_url(self,
                         path,
                         data,
                         filename,
                         file_url,
                         timeout=30,
                         binary_key='importImage'):  # 发送Data和File的混合数据
        '''将file_url对应的文件上传
        '''
        url = 'http://' + self.ip + path
        print('ISAPI [POST FILE %s]' % (url))
        resp = requests.get(file_url)
        file_content = resp.content
        content = None
        for i in range(3):
            try:
                content = self.session.post(url,
                                            data,
                                            timeout=timeout,
                                            verify=False)
                self.content = content
                break
            except Exception as e:
                if i == 2:
                    if 'timed out' in str(e) or 'timeout' in str(e):
                        msg = f'ISAPI [POST {url}]操作超时'
                        raise Exception(msg)
                    else:
                        raise Exception(e)
                else:
                    time.sleep(1)
        print('data=', data)
        data[binary_key] = (filename, file_content)
        # data['importImage'] = (filename, file_content)
        encode_data = urllib3.encode_multipart_formdata(data)
        data = encode_data[0]
        content.headers['Content-Type'] = encode_data[1]
        content = self.session.post(url,
                                    data,
                                    headers=content.headers,
                                    timeout=timeout,
                                    verify=False)
        self.status_code = content.status_code
        return content.text

    def put(self, path, data, timeout=60, ResponseCode=False):
        url = 'http://' + self.ip + path
        putData = None
        # self.pathList
        # logfilepath = global_variable.LOGRESFILEPATH
        logfilepath=None
        # print('ISAPI [PUT %s]' % (url))
        content = None
        isResSuc = 'F'
        # content = self.session.put(url, data, timeout=timeout, verify=False)
        get_time = str(datetime.datetime.now())[:19]
        for i in range(3):
            try:
                get_time = str(datetime.datetime.now())[:19]
                if not data:
                    VD_LOG_DEBUG(self.ip,'ISAPI [PUT %s]\r\n[PutData None]' % (url))
                    putData = None
                else:
                    if not type(b"\x00") == type(data):
                        # print('ISAPI [PUT %s]\r\n[PutData %s]' % (url, data))
                        if "\n" in data:
                            putData = data.replace("\n", "")
                        else:
                            putData = data
                    elif b'xmlns="http://www.hikvision.com/ver20/XMLSchema"' in data or b'<?xml version="1.0" encoding="UTF-8"?>' in data:
                        VD_LOG_DEBUG(self.ip,
                            f'ISAPI [PUT {url}]\r\n[PutData {data.decode()}]')
                        postData = data.decode()
                    else:
                        try:
                            json.loads(data)
                            VD_LOG_DEBUG(self.ip,f'ISAPI [PUT {url}]\r\n[PutData {data}]')
                            postData = data
                        except Exception as e:
                            VD_LOG_DEBUG(self.ip,'ISAPI [PUT %s]\r\n[PutData is fileBytes]' %
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
            VD_LOG_DEBUG(self.ip,"url %s try again more time %d" % (url, i))
            time.sleep(1)
        VD_LOG_DEBUG(self.ip,'ISAPI [PUT %s]\r\n[Response %s]' % (url,content.text))
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

    def put_file(self, path, filepath, timeout=None, ResponseCode=False):
        '''
        上传文件（流式上传）
         参数：
            path：uri
            filepath: 文件路径
            timeout： 请求超时时间
            ResponseCode: 是否返回响应码
        '''
        url = 'http://' + self.ip + path
        print('ISAPI [PUT %s]' % (url))

        content = None
        # content = self.session.put(url, data, timeout=timeout, verify=False)
        try_times = 5
        for i in range(try_times):
            try:
                t1 = time.time()
                with open(filepath, 'rb') as f:
                    content = self.session.put(url,
                                               data=f,
                                               timeout=timeout,
                                               verify=False)
                self.content = content
                self.status_code = content.status_code
                t2 = time.time()
                print(f'this loop consum_time = {t2 - t1}')
                break
            except Exception as e:
                print(traceback.format_exc())
                t2 = time.time()
                print(f'this loop consum_time = {t2 - t1}')
                if i == try_times - 1:
                    print(traceback.format_exc())
                    if 'timed out' in str(e).lower() or 'timeout' in str(
                            e).lower():
                        msg = f'ISAPI [PUT {url}]操作超时'
                    elif 'Failed to establish a new connection' in str(e):
                        msg = f'ISAPI [PUT {url}]连接失败'
                    else:
                        msg = f'ISAPI [PUT {url}]操作失败{e}'
                    raise Exception(msg)
                else:
                    time.sleep(1)
                    print('try again...')
        if ResponseCode:
            return content.status_code
        else:
            return content.text

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
        put_ret=None
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

    # def http_data_get(self, data=None, path_list=[], type_list=[], attrib_list=[]):
    #     """
    #     实现xml或json数据的节点相关内容获取操作
    #     输入参数：
    #         data：要处理的xml或json数据
    #         path_list：查询路径，以列表传入
    #         type_list: 查询类型，包含element, value, attrib，分别代表节点、值、属性，以列表传入
    #         attrib_list：属性名，当查询类型为属性时，需传入属性名，以列表传入
    #     输出参数：
    #         {
    #             'success':True/False,
    #             'msg':'',
    #             'data':[]
    #         }
    #         其中：
    #         success为True时, data为各path对应的值或属性等（若对应节点不存在，则为该节点不存在的报错信息），[path1查询结果，path2查询结果……]
    #         success为False时, msg为错误信息, 只要有一个节点不存在，结果就是False
    #     """
    #     ret = {
    #         'success': True,
    #         'msg': '',
    #         'data': []
    #     }
    #     if not isinstance(path_list, list):
    #         ret['success'] = False
    #         ret['msg'] = '参数path_list必须为列表'
    #         return ret
    #     if not isinstance(type_list, list):
    #         ret['success'] = False
    #         ret['msg'] = '参数type_list必须为列表'
    #         return ret
    #     if not isinstance(attrib_list, list):
    #         ret['success'] = False
    #         ret['msg'] = '参数attrib_list必须为列表'
    #         return ret
    #     flag = True  # 返回结果
    #     result_list = []  # 返回内容
    #     error = []
    #     xml_ret = self._isapi_is_xml(data)
    #     if xml_ret is not None:
    #         # 处理XML
    #         error_code = xml_ret.xpath(".//*[local-name()='subStatusCode']")
    #         if error_code:
    #             print(data)
    #             ret['success'] = False
    #             ret['msg'] = u"获取内容出错:%s！" % (error_code[0].text)
    #             return ret
    #
    #         if not path_list:
    #             ret['data'] = data
    #             return ret
    #
    #         for index, path_item in enumerate(path_list):
    #             xml_path = re.sub(r'/([^/][\w\.]*)', r"/*[local-name()='\1']", path_item)
    #             # print(u"xpath路径:" + xml_path)
    #             result = xml_ret.xpath(xml_path)
    #             # print(result)
    #             print(f'type_list[{index}]={type_list[index]}')
    #             if not result:
    #                 result_list.append(u"%s节点不存在" % path_item)
    #                 error.append("%s节点不存在" % path_item)
    #                 flag = False
    #             elif type_list[index] == "element":
    #                 result_list.append(result)
    #             elif type_list[index] == "value":
    #                 # print('value')
    #                 value = []
    #                 for one in result:
    #                     if one.text:  # 节点内容非空
    #                         value.append(one.text)
    #                     else:  # 节点内容为空时返回空字符串
    #                         value.append('')
    #                 result_list.append(value)
    #             elif type_list[index] == "attrib":
    #                 result_list.append([one.attrib.get(attrib_list[index]) for one in result])
    #             else:
    #                 print(data)
    #                 raise Exception(f'传入的参数type_list中存在不支持的值{type_list[index]}')
    #     else:
    #         json_ret = self._isapi_is_json(data)
    #         if not json_ret:
    #             ret = {
    #                 'success': False,
    #                 'msg': u"返回内容不是XML/JSON格式！",
    #                 'data': []
    #             }
    #             return ret
    #         else:
    #             for path_item in path_list:
    #                 print("json路径:" + path_item)
    #                 json_temp = json_ret
    #                 path_json = path_item.split("/")
    #                 while "" in path_json:
    #                     path_json.remove("")
    #                 for item in path_json:
    #                     if isinstance(json_temp, list):
    #                         try:
    #                             json_temp = json_temp[int(item)]
    #                         except Exception as e:
    #                             print(str(e))
    #                             error.append(str(e))
    #                             flag = False
    #                             break
    #                     elif isinstance(json_temp, dict):
    #                         json_temp = json_temp.get(item)
    #                     else:
    #                         flag = False
    #                         break
    #                     if json_temp is None:
    #                         flag = False
    #                         break
    #                 if json_temp is None:
    #                     result_list.append(u"%s节点内容为空！" % path_item)
    #                     error.append(u"%s节点内容为空！" % path_item)
    #                 else:
    #                     result_list.append(json_temp)
    #     if not flag:
    #         print(data)
    #     if not flag:
    #         print(data)
    #     ret['success'] = flag
    #     ret['msg'] = ','.join(error)
    #     ret['data'] = result_list
    #     print(f'ret={ret}')
    #     return ret


if __name__=="__main__":
    devInfo={
        "IP":"10.41.203.139",
        "U_NAME":"admin",
        "P_WORD":"abcd1234"
    }
    isapi_test=EZVIZ_ISAPI(devInfo)
    page = isapi_test.get(f'/ISAPI/System/Video/inputs/channels')
    root = etree.XML(str(page).encode('utf-8'))

    if '</name>' in str(page):
        channel_name = root.xpath("//*[local-name()='name']")
        print(len(channel_name))
        for index in channel_name:
            print(index.text)


    # ResolutionUrl="/ISAPI/Streaming/channels/101"
    # ResWith = 1920
    # ResHeigh = 1080
    # response = isapi_test.set_by_xpath(ResolutionUrl, ["//*[local-name()='videoResolutionWidth']",
    # "//*[local-name()='videoResolutionHeight']"], [ResWith, ResHeigh])
    # print(response)
    # if 'OK' not in response:
    #     msg = '通道%d主码流修改分辨率为%s*%s失败!' % (
    #     1, str(ResWith), str(ResHeigh)) + isapi_test.get_subStatusCode(response)


