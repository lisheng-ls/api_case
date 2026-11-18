import json

import allure
import pytest

from client.send_client import RequestClient
from common.case_func_utl import get_global_variable, get_test_case_name, get_all_case_info, \
    regx_sub_data, get_api_default_param, json_info_sub
from common.load_execl_info import load_excel_info
from core.logger import logger

file_path = r'D:\学习项目\PythonProject\testcase\1.xlsx'

#全局的环境变量
global_variable_dict = get_global_variable(file_path=file_path)


#测试集合
test_suite_list = get_test_case_name(file_path)

#发送请求客户端
client = RequestClient()

#获取测试数据
all_suit_info = get_all_case_info(file_path=file_path,suit_names=test_suite_list)

# ========== session级fixture，全局只登录一次 ==========
@pytest.fixture(scope="session", autouse=True)
def login():
    login_cilent = RequestClient()
    kwargs = {}
    #登录接口请求参数
    login_info = load_excel_info(file_path, sheet_name='登录登出')[0]
    url = login_info[3]
    url = regx_sub_data(s=url,vars_dict=global_variable_dict)
    method = login_info[4]
    json_data = login_info[6]
    json_data = json.loads(json_data)

    kwargs['url'] = url
    kwargs['method'] = method
    kwargs['json'] = json_data

    #登录
    login_cilent.send(**kwargs)

    #提取参数
    response_extracts =login_info[7]
    response_extracts = json.loads(response_extracts)
    for response_extract in response_extracts:
        for key,value in response_extract.items():
            global_variable_dict[key] = login_cilent.get_response_info(value)

    logger.info(f'登录成功，token和uuid已经存入环境变量中：{global_variable_dict}')
    yield

    logger.info('所有用例执行完成，开始退出')


@pytest.mark.parametrize('suit_name,case_name,case_infos',all_suit_info)
def test_run(suit_name,case_name,case_infos):
    # 给整条业务用例设置allure标题
    allure.dynamic.title(f"【{suit_name}】{case_name}")

    for indx,case_info in enumerate(case_infos,start=1):

        for api_name,api_info in case_info.items():

            with allure.step(f'步骤{indx}:{api_name}'):
                kwargs = {}


                #url,并替换host
                url = api_info[0]
                url = regx_sub_data(s=url,vars_dict=global_variable_dict)
                kwargs['url'] = url

                #请求方式
                method = api_info[1]
                kwargs['method'] = method


                #请求头
                headers = api_info[2]
                if headers:
                    headers= regx_sub_data(s=headers,vars_dict=global_variable_dict)
                    headers = json.loads(headers)
                    kwargs['headers'] = headers
                #请求参数

                #接口默认请求参数,并转换为字典
                api_default_param=get_api_default_param(file_path)[api_name]

                if api_default_param is None:
                    kwargs['json'] = None
                    kwargs['data'] = None
                    kwargs['params'] = None
                    kwargs['files'] = None
                else:
                    api_default_param=json.loads(api_default_param)
                    api_data = api_info[3]
                    if api_data:
                        api_data = regx_sub_data(s=api_data,vars_dict=global_variable_dict)
                        api_data = json.loads(api_data)

                    #发起请求
                    #这里根据

                    if 'json' in api_data:
                        for jsonpath,sub_data in api_data['json'].items():
                            api_default_param['json'] = json_info_sub(api_default_param['json'],jsonpath=jsonpath,sub_data=sub_data)
                    if 'data' in api_data:
                        for jsonpath,sub_data in api_data['data'].items():
                            api_default_param['data'] = json_info_sub(api_default_param['data'],jsonpath=jsonpath,sub_data=sub_data)
                    if 'params' in api_data:
                        for jsonpath,sub_data in api_data['params'].items():
                            api_default_param['params'] = json_info_sub(api_default_param['params'],jsonpath=jsonpath,sub_data=sub_data)
                    if 'files' in api_data:
                        for jsonpath,sub_data in api_data['file'].items():
                            api_default_param['file'] = json_info_sub(api_default_param['file'],jsonpath=jsonpath,sub_data=sub_data)
                    kwargs['json'] = api_default_param.get('json')
                    kwargs['data'] = api_default_param.get('data')
                    kwargs['params'] = api_default_param.get('params')
                    kwargs['files'] = api_default_param.get('files')

                #发起请求
                client = RequestClient()

                client.send(**kwargs)

                #断言接口响应是否正常
                expect_resp = api_info[5]
                expect_resp=json.loads(expect_resp)[0]
                actual_resp =client.get_response_info(expect_resp['actual'])

                #对返回结果进行处理：数字则都转换为字符串类型，字符，则都转换为小写
                if isinstance(actual_resp,(int,float)):
                    actual_resp = str(actual_resp)
                if isinstance(actual_resp,str):
                    actual_resp = actual_resp.lower()

                assert actual_resp == expect_resp['expect'],f"【{case_name}】步骤{indx}断言失败！实际：{actual_resp} 预期：{expect_resp}"


                #提取响应信息
                response_extracts = api_info[4]
                if response_extracts:
                    response_extracts = json.loads(response_extracts)
                    for response_extract in response_extracts:
                        for param,json_path in response_extract.items():
                            global_variable_dict[param] = client.get_response_info(json_path)
                            logger.info(f'变量：{param}的值提取成功为：{client.get_response_info(json_path)}')




if __name__ == '__main__':
    pytest.main(['main.py'])

    """
    生成报告：
    控制台运行：pytest main.py -v -s --alluredir=allure-results --clean-alluredir
    """