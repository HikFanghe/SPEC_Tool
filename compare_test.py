# -*- coding: utf-8 -*-
"""
@Auth ： Fanghe.Lin
@File ：compare_test.py.py
@IDE ：PyCharm
@Time ： 2023/10/31 9:59
@Institution: Hikvision, China
"""
import traceback
import warnings
import openpyxl
from lib.mtd_com_fun import MtdComFun
import pandas as pd
import numpy as np
import re


class Test(MtdComFun):
    def __init__(self):
        self.resultHandle = {
            "深度学习框架": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "浏览器": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', [' '], None],
            "恢复出厂设置": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "开放能力": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', None, None],
            "开放资源规格": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', [' '], None],
            "开发语言": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "Smart事件": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "最大分辨率": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, ['×', 'x']],
            "聚焦模式": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "P/N制": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', ['制'], None],
            "预置点": ['self.resHandleGeneral_3', 'self.resCompGeneral_3', None, '(\d+)'],
            "快门": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', [' ', ',', '，', 's'], ['~','to']],
            "普通事件": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "数字变倍": ['self.resHandleGeneral_3', 'self.resCompGeneral_3', None, '(\d+)'],
            "码率控制": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "音频压缩标准": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "音频压缩码率": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', ['\(', '\)', '\（', '\）', '\s'], None],
            "视频压缩码率": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, ['~', 'to']],
            "视频压缩标准": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', None, None],
            "水尺识别": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', None, None],
            "H.264编码类型": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "H.265编码类型": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "同时预览路数": ['self.resHandleGeneral_3', 'self.resCompGeneral_3', None, '(\d+)'],
            "用户管理": ['self.resHandleGeneral_3', 'self.resCompGeneral_3', None, '(\d+)个'],
            "其他功能": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "低功耗协议": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "主码流帧率分辨率": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', [' '], None],
            "子码流帧率分辨率": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', [' '], None],
            "第三码流帧率分辨率": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', [' '], None],
            "第四码流帧率分辨率": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', [' '], None],
            "第五码流帧率分辨率": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', [' '], None],
            "守望功能": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "定时任务": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "图像增强": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "图像设置": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', ['通过客户端或者浏览器可调'], None],
            "图像防抖": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "日夜转换模式": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "隐私保护": ['self.resHandleGeneral_2', 'self.resCompGeneral_2', ['【全景】', '【细节】'], None],  # 这条可能需修改
            "接口协议": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "客户端": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', ['海康互联'], None],
            "网络存储": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', ['均支持', '支持', "\/", '\(', '\（', '\)', '\）', ' '],None],# 可能还是有点问题
            "网络协议": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', None, None],
            "音频采样率": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', ['\s'], None],
            "ROI": ['self.resHandleGeneral_1', 'self.resCompGeneral_1', ['\n'], None],
            "网页客户端语言":['self.resHandleGeneral_2', 'self.resCompGeneral_2', [' ', '\(', '\)'], None],
        }


    def get_excel_content(self, input_ex, output_ex):
        # 获取spec的excel中所有的子项内容
        df = pd.read_excel(input_ex, header=3, usecols=[2,3,4])
        print(df.shape)
        item = df.iloc[:,0].tolist()
        ac_data = df.iloc[:,2].tolist()
        spec_data = df.iloc[:,1].tolist()


        # wb = openpyxl.load_workbook(output_ex)
        wb  = openpyxl.Workbook()
        sheet = wb.active
        for i in range(len(item)):
            try:
                tmp = item[i]
                sheet[f'A{i + 5}'] = spec_data[i]
                sheet[f'B{i + 5}'] = ac_data[i]
                if item[i] in self.resultHandle:
                    itemFun = self.resultHandle[item[i]]
                    result = self.resHandleCallFun(eval(itemFun[0]), eval(itemFun[1]), ac_data[i],spec_data[i],
                                                                     delStr=itemFun[2], sep=itemFun[3])
                    sheet[f'C{i + 5}'].value = result
                else:
                    if str(spec_data[i]).strip('\n') == str(ac_data[i]).strip('\n'):
                        sheet[f'C{i + 5}'].value = "P"
                    else:
                        sheet[f'C{i + 5}'].value = "F"
            except Exception as e:
                print(traceback.format_exc())
        wb.save(output_ex)
if __name__ == '__main__':
    input = re.sub('/', r'\\', "D:/02 前端自动化/工具开发/工具开发/sepc/specDataDocuments/问题排查相关SPEC/2023-12-18_QJK_DS-2DF7C432MXR-D_EPC_Spec_10.20.102.60_report.xlsx")
    output = re.sub('_report','_compare_report',input)
    test = Test()
    test.get_excel_content(input, output)