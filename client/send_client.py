"""
掉用接口客户端
"""
import requests
import jsonpath
from core.logger import logger

class RequestClient:
    def __init__(self):
        self.resp : requests.Response | None

    def send(self,**kwargs):
        for key, value in kwargs.items():
            logger.info(f'接口的{key}是{value}')
        self.resp = requests.request(**kwargs)
        if self.resp.status_code == 200:
           return self.resp
        else:
           logger.error(f'接口访问失败，请检查：{self.resp.text}')
           raise RuntimeError(f'接口访问失败，请检查：{self.resp.text}')

    def get_response_info(self,json_path:str) -> str:
        #根据json_path,提取响应结果
        resp = self.resp.json()
        if not resp:
            logger.info(f'接口响应结果为空,无法根据{json_path}提取结果：{resp}')
        else:
            json_data = jsonpath.jsonpath(resp,json_path)[0]
            if not json_data:
                logger.info(f'根据{json_path}，提取的结果为空')
                return None
            return json_data
if __name__ == '__main__':
    request_client = RequestClient()
    url='http://193.112.98.218:18081/api-dev/api/collegecolumn/public/list'
    method = 'get'
    resp = request_client.send(url=url,method=method)
    print(resp.json())
    resp1 = request_client.get_response_info(json_path='$..message1')
    print(resp1)