import os
from dataclasses import dataclass
from typing import TypedDict

from dotenv import load_dotenv

#加载env文件
load_dotenv()


@dataclass
class ModelConfig(TypedDict):
    lv_model_name:str
    llm_model_name: str
    api_key:str
    base_url: str

llm_config = ModelConfig(
    lv_model_name=os.getenv('LV_MODEL_NAME'),
    llm_model_name=os.getenv('LLM_MODEL_NAME'),
    api_key=os.getenv('API_KEY'),
    base_url=os.getenv('BASE_URL')
)