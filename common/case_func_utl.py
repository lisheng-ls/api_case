"""
编写整个接口测试过程中的一些方法
"""
import re

from jsonpath_ng import parse

from common.load_execl_info import load_excel_info
from common.util_func import rdm_future_date_time
from core.logger import logger


#随机方法白名单
func_router = {
    "rdm_future_date_time":rdm_future_date_time
}


#1、读取全局变量
def get_global_variable(file_path):
    global_variables = load_excel_info(file_path=file_path,sheet_name='全局变量')
    global_variable_dict = {global_variable[0]:global_variable[1]for global_variable in global_variables}
    return global_variable_dict


#2、获取接口默认参数
def get_api_default_param(file_path):
    api_default_params = load_excel_info(file_path=file_path,sheet_name='接口默认参数')
    api_default_params_dict = {api_default_param[0]:api_default_param[1] for api_default_param in api_default_params}
    return api_default_params_dict

#3、获取测试集合管理信息
def get_test_case_name(file_path):
    test_case_names = load_excel_info(file_path=file_path,sheet_name='测试集合管理')
    test_case_names = [test_case_name[0] for test_case_name in test_case_names if test_case_name[1]=='y']
    return test_case_names

#4、获取某个测试集合的测试数据
def get_single_case_info(file_path,suit_name):
    """

    单个集合测试数据样式：
    {用例名称1：[{接口名称1：接口参数1，
                接口名称2：接口参数1}]
     用例名称2：[{接口名称1：接口参数1，
                接口名称2：接口参数1}]
    }
    :param file_path:
    :param sheet_name:
    :return:
    """

    test_case_infos = load_excel_info(file_path=file_path,sheet_name=suit_name)

    case_info_dict = {}
    for test_case_info in test_case_infos:
        #用例名称
        case_name = test_case_info[1]
        #接口名称
        api_name = test_case_info[2]
        #接口参数
        api_info=[test_case_info[i] for i in range(3,len(test_case_info))]

        api_info_dict = {api_name: api_info}
        if case_name not in case_info_dict:
            case_info_dict[case_name] = [api_info_dict]
        else:
            case_info_dict[case_name].append(api_info_dict)

    return case_info_dict

#获取全部测试数据
def get_all_case_info(file_path,suit_names):
    """
    多个集合测试数据样式：
    [(测试结合名称，测试用例名称，[测试用例数据])]
    :param file_path:
    :param suit_names:
    :return:
    """
    all_suit_case_infos = []
    for suit_name in suit_names:
        single_suit_case_infos = get_single_case_info(file_path,suit_name)

        for case_name,case_info in single_suit_case_infos.items():
            data = (suit_name,case_name,case_info)


            all_suit_case_infos.append(data)


    return all_suit_case_infos

#5、将接口数据中的测试数据替换值默认数据
def update_api_default_param(api_default_param,test_case_info):
    api_data=api_default_param.update(test_case_info)
    return api_data


#正对excel中动态变量应用，进行识别与替换
def regx_sub(s,vars_dict):
    """

    :param s: 目标字符串
    :param vars_dict: 公共变量存储字典
    :return: 替换后的字符串
    """
    res = re.compile(r'\$\{([^}]+)\}')
    resps = res.findall(s)

    def repl_func(match):
        #match是正则匹配到的对象
        #${xxx}
        #match.group(1) : xxx
        # match.group(0) : xxx
        return vars_dict.get(match.group(1),match.group(0))
    s = res.sub(repl_func,s)
    return s

#针对excel中的动态方法进行识别与替换
def regx_func_sub(s):
    res = re.compile(r'\$\{\{([^}]+)\((.*?)\)\}\}')
    resps = res.findall(s)

    def repl_func(match):
        #方法名称
        func_name = match.group(1)
        #方法参数
        args = match.group(2)
        if func_name not in func_router:
            logger.info(f'没有{func_name}方法')
            raise ValueError(f'没有{func_name}方法')
        return func_router[func_name](args)
    s = res.sub(repl_func,s)
    return s

#组合方法
def regx_sub_data(s,vars_dict=None):
    if vars_dict:
        s=regx_sub(s,vars_dict)
    else:
        s=regx_func_sub(s)
    return s


#复杂json替换
def json_info_sub(json_data,jsonpath,sub_data):
    """
    :param json_data:原json数据
    :param jsonpath: jsonpath
    :param sub_data: 替换数据
    :return: json_data
    """
    jsonpath=parse(jsonpath)
    matches = list(jsonpath.find(json_data))
    if not matches:
        logger.error(f'根据{jsonpath}从{json_data}中没有提取到数据')
        raise ValueError(f'根据{jsonpath}从{json_data}中没有提取到数据')
    for match in matches:
        value = match.context.value
        key = str(match.path)
        value[key] = sub_data
    return json_data


if __name__ == '__main__':
    file_path = r'D:\学习项目\PythonProject\testcase\1.xlsx'
    sheet_name = '新增客户测试集合'
    #print(get_global_variable())
    #print(get_api_default_param())
    # sheet_names=get_test_case_name()
    # for sheet_name in sheet_names:
    #     #print(get_test_case_info(sheet_name))
    #     print(update_api_default_param(sheet_name))
    #s='adadada${token}dadad${name}'
    # vars_dict ={"token":"123456",
    #             'name':'张三'}
    # #print(regx_sub(s, vars_dict))
    #
    # s="'next_time': ${{rdm_future_date_time(10)}}"
    # # print(regx_func_sub(s))
    # print(regx_sub_data(s,vars_dict=vars_dict))

    # json_data ={
    dict={'host': 'http://121.11.97.201:8090/', 'username': 15888881000, 'password': 1234}
    # print(get_single_case_info(file_path=file_path, suit_name=sheet_name))
    s='${host}/login'

    print(regx_sub_data(s=s, vars_dict=dict))