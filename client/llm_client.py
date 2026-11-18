import os
from typing import Optional

from langchain_core.exceptions import LangChainException
from langchain_openai import ChatOpenAI

from core.logger import logger
from config.model_config import llm_config

_llm_client ={}

def get_llm_client(model_name:Optional[str]=None,json_mode:bool=False):
    """
    #
    :param model_name:模型名称，如果未传，则用默认的模型
    :param json_mode: 是否返回json格式数据
    :return:
    """
    #模型名称
    model_name = model_name or llm_config.llm_model_name or 'qwen-flash'

    # 缓存键：模型名+JSON模式，唯一标识不同配置的客户端
    cache_key = (model_name, json_mode)

    if cache_key in _llm_client:
        logger.debug(f'模型已经初始化,模型名称：{model_name},是否返回json格式数据：{json_mode}')
        return _llm_client[cache_key]

    #检验核心参数是否缺少
    if not llm_config.api_key :
        logger.error('模型缺少关键参数：api_key，无法初始化，请检查，env配置文件')
        raise ValueError('模型缺少关键参数：api_key，无法初始化，请检查，env配置文件')
    if not llm_config.base_url :
        logger.error('模型缺少关键参数：base_url，无法初始化，请检查，env配置文件')
        raise ValueError('模型缺少关键参数：base_url，无法初始化，请检查，env配置文件')

    logger.info(f"[LLM客户端] 开始初始化新实例：模型={model_name}，JSON模式={json_mode}")

    model_kwargs = {}
    if json_mode:
        model_kwargs['response_format'] = {"type": "json_object"}
        logger.debug(f"[LLM客户端] 已开启JSON输出模式，模型将返回标准JSON结构")
    try:
        llm_client = ChatOpenAI(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            model_kwargs=model_kwargs,
            model=model_name,
        )
    except LangChainException as e:
        raise Exception(f"[LLM客户端] 模型【{model_name}】初始化失败（LangChain层）：{str(e)}") from e
    # 6. 新实例存入全局缓存，供后续调用复用
    _llm_client[cache_key] = llm_client

    logger.info(f"[LLM客户端] 实例初始化成功并缓存：模型={model_name}，JSON模式={json_mode}")

    return llm_client