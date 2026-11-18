import re
from pathlib import Path

from agent.state import ApiState
from core.logger import logger

def _parse_md_file_step1(md_path):
    if md_path is None:
        logger.error(f'md文件不存在，无法进行下一步，请检查文件路径:{md_path}是否有有效')
        raise ValueError('md文件不存在，无法进行下一步，请检查文件路径是否有有效')

    #读取md文件
    md_path_obj = Path(md_path)

    md_content = md_path_obj.read_text(encoding='utf-8')
    if md_content is None:
        logger.info('接口文档为空，请检查')
        raise ValueError('接口文档为空，请检查')

    return md_content


def _parse_md_file_step2(md_content):
    """
        提取：接口名称、url、method、请求参数params
        部分接口无参数表格，params返回空列表[]
        """
    # 按 ### 1.0、 切分每一个接口块，支持版本号通用 ### \d+\.\d+、
    api_block_re = re.compile(
        r"###\s+\d+\.\d+、\s*(.*?)\s*"  # group1 接口名称
        r"\*\*请求URL\*\*\s*?-\s*`?\s*(\S+?)\s*`?\s*"  # group2 url，处理反引号包裹
        r"\*\*请求方式\*\*\s*?-\s*(\S+)\s*",  # group3 method
        re.DOTALL
    )

    # 匹配【参数】后面的markdown表格块，遇到下一个 **请求示例** / **返回参数说明**终止
    param_table_re = re.compile(
        r"\*\*参数\*\*\s*?(\|.*?\|\r?\n\|[-: |]+\|\r?\n(?:\|.*?\|\r?\n)*)",
        re.DOTALL
    )

    def parse_md_table(table_str: str):
        """解析md表格为字典数组"""
        rows = []
        for line in table_str.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            cells = re.findall(r"\|\s*([^|]+?)\s*", line)
            if cells:
                rows.append(cells)
        if len(rows) < 3:
            return []
        headers = rows[0]
        data_rows = rows[2:]
        return [dict(zip(headers, row)) for row in data_rows]

    result = []
    # 迭代全部接口块
    for block_match in api_block_re.finditer(md_content):
        api_name = block_match.group(1).strip()
        url = block_match.group(2).strip()
        method = block_match.group(3).strip()

        # 在整个接口块文本内找参数表格
        block_start = block_match.start()
        # 截取从当前接口开始，直到下一个 ### 标题之前的文本
        next_title = re.search(r"###\s+\d+\.\d+、", md_content[block_start + 1:])
        if next_title:
            block_end = block_start + 1 + next_title.start()
        else:
            block_end = len(md_content)
        api_chunk = md_content[block_start:block_end]

        table_match = param_table_re.search(api_chunk)
        params = []
        if table_match:
            table_raw = table_match.group(1)
            params = parse_md_table(table_raw)

        result.append({
            "api_name": api_name,
            "url": url,
            "method": method,
            "params": params
        })
    return result


def parse_md_file(state:ApiState) -> ApiState:
    """
    步骤一：1、解析上传的md文件,获取接口参数
    1、验证md文件是否有效，并读取md_content

    2、通过正则，获取每个接口参数：接口名称、请求url、请求方式、参数
    """
    #1、验证md文件是否有效，并读取md_content
    md_content = _parse_md_file_step1(md_path=state['md_path'])

    #2、通过正则，获取每个接口参数：接口名称、请求url、请求方式、参数

    json_data = _parse_md_file_step2(md_content=md_content)

    #3、更新state
    state['md_content'] = json_data
    return state

if __name__ == '__main__':
    md_path = r'D:\学习项目\PythonProject\doc\接口文档.md'
    md_content = _parse_md_file_step1(md_path)
    print(md_content)
    api_info = _parse_md_file_step2(md_content)
    print(api_info)