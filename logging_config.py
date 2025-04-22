# coding=utf-8
"""
    @Author: Jacob
    @Date  : 2025/4/20
    @Desc  : 日志配置
"""

import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logging():
    # 确保logs目录存在
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f"{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )