# -*- coding: utf-8 -*-
"""
@Auth ： Fanghe.Lin
@File ：defaultFun.py
@IDE ：PyCharm
@Time ： 2023/11/28 14:32
@Institution: Hikvision, China
"""
import datetime
import json
import re
import time
import traceback
import requests

# ------------------云服务器获取------------------------
def service_cfg(service_type="SPEC_VERSION"):
    """查询服务配置信息"""
    url = 'http://hice.hikvision.com.cn/gw1/frontends_group_qd/CATTDataManage/CloudParameter/Operation'
    data = {
        "name": service_type,
        "userName": "linfanghe",
        "operation": "view"
    }

    try:
        searchReq = requests.post(url, data=json.dumps(data))
        searchData = searchReq.json()
        searchReq.close()
        if not searchData['Success']:
            return False, f'连接云空间获取{service_type}云服务配置失败,请联系集成测试CATT工具开发组排查!'
        CFG = searchData["msg"]
        return True, CFG
    except Exception as ex:
        print(traceback.print_exc())
        return False, f'连接云空间获取{service_type}云服务配置出现异常:{str(ex)}!请联系集成测试CATT工具开发组排查!'

