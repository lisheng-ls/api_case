import copy
from typing import TypedDict


class ApiState(TypedDict):
    #md文件
    md_path:str
    md_content:str

    #解析后的json数据
    parse_json_content:str
    parse_json_path:str


    #excel文件
    excel_path:str
    excel_content:str


api_state: ApiState = {
    'md_path':None,
    'md_content':None,
    'parse_json_content': None,
    'parse_json_path': None,
    'excel_path':None,
    'excel_content':None,
}


#创建初始的ApiState
def create_primary_state():
    return copy.deepcopy(api_state)

