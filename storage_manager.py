import json
import csv
from typing import List, Dict, Any
from pathlib import Path
from abc import ABC, abstractmethod

class StorageStrategy(ABC):
    """存储策略抽象基类"""
    
    @abstractmethod
    def save(self, chunks: List[str], file_path: str) -> None:
        """保存文本块到文件
        
        Args:
            chunks: 文本块列表
            file_path: 保存文件路径
        """
        pass

class JsonStorageStrategy(StorageStrategy):
    """JSON格式存储策略"""
    
    def save(self, chunks: List[str], file_path: str) -> None:
        data = {
            'chunks': chunks,
            'total_chunks': len(chunks)
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class CsvStorageStrategy(StorageStrategy):
    """CSV格式存储策略"""
    
    def save(self, chunks: List[str], file_path: str) -> None:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['chunk_id', 'content'])
            for i, chunk in enumerate(chunks, 1):
                writer.writerow([i, chunk])

class StorageManager:
    """存储管理器，负责文本块的本地化存储"""
    
    def __init__(self, strategy: StorageStrategy = None):
        """初始化存储管理器
        
        Args:
            strategy: 存储策略实例，默认使用JSON格式
        """
        self.strategy = strategy or JsonStorageStrategy()
    
    def set_strategy(self, strategy: StorageStrategy) -> None:
        """更改存储策略
        
        Args:
            strategy: 新的存储策略实例
        """
        self.strategy = strategy
    
    def save_chunks(self, chunks: List[str], file_path: str,
                    format: str = 'json') -> None:
        """保存文本块到指定格式的文件
        
        Args:
            chunks: 文本块列表
            file_path: 保存文件路径
            format: 存储格式，可选'json'或'csv'
        """
        # 确保目标目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 根据格式选择存储策略
        if format.lower() == 'csv':
            self.set_strategy(CsvStorageStrategy())
        else:  # 默认使用JSON格式
            self.set_strategy(JsonStorageStrategy())
        
        # 保存文本块
        self.strategy.save(chunks, file_path)