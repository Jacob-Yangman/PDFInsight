# coding=utf-8
"""
    @Author: Jacob
    @Date  : 2025/4/20
    @Desc  : 模型配置加载器
"""

from dataclasses import dataclass
import yaml
from pathlib import Path
import os

@dataclass
class ModelConfig:
    name: str
    api_key: str
    base_url: str

def load_model_config(config_path: str = "config.yaml") -> ModelConfig:
    """加载模型配置并进行验证"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 验证模型名称
        if not config['model']['name']:
            raise ValueError("模型名称不能为空")
            
        # 从环境变量获取API密钥
        env_var_name = config['model']['api_key']
        api_key = os.getenv(env_var_name)
        if not api_key:
            raise ValueError(f"请在环境变量中设置 {env_var_name}")
            
        # 验证API基础URL
        if not config['model']['base_url']:
            raise ValueError("API基础URL不能为空")
            
        return ModelConfig(
            name=config['model']['name'],
            api_key=api_key,
            base_url=config['model']['base_url']
        )
        
    except FileNotFoundError:
        raise FileNotFoundError("配置文件不存在")
    except yaml.YAMLError:
        raise ValueError("配置文件格式错误")