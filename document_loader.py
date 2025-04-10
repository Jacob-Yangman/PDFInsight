from abc import ABC, abstractmethod
from typing import List, Union, BinaryIO
from pathlib import Path
import tempfile

from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image

class DocumentLoader(ABC):
    """抽象基类，定义文档加载器的接口"""
    
    @abstractmethod
    def load(self) -> List[Image.Image]:
        """加载文档并转换为图片列表"""
        pass

class PDFLoader(DocumentLoader):
    """PDF文档加载器，负责将PDF转换为图片"""
    
    def __init__(self, source: Union[str, Path, BinaryIO], dpi: int = 200):
        self.source = source
        self.dpi = dpi

    def load(self) -> List[Image.Image]:
        """将PDF文档转换为PIL Image对象列表
        
        Returns:
            List[Image.Image]: 每页PDF对应的图片列表
        """
        try:
            if isinstance(self.source, (str, Path)):
                images = convert_from_path(self.source, dpi=self.dpi)
            else:
                # 处理二进制流输入
                with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
                    tmp.write(self.source.read())
                    tmp.seek(0)
                    images = convert_from_path(tmp.name, dpi=self.dpi)
            
            # 确保所有图片都是RGB模式
            processed_images = []
            for img in images:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                processed_images.append(img)
            return processed_images
        except Exception as e:
            raise Exception(f"PDF转换失败: {str(e)}")

class DocumentLoaderFactory:
    """文档加载器工厂类，用于创建不同类型的文档加载器"""
    
    @staticmethod
    def create_loader(file_path: Union[str, Path, BinaryIO], file_type: str = 'pdf', **kwargs) -> DocumentLoader:
        """根据文件类型创建对应的文档加载器
        
        Args:
            file_path: 文件路径或二进制流
            file_type: 文件类型，目前支持'pdf'
            **kwargs: 额外的参数
        
        Returns:
            DocumentLoader: 对应类型的文档加载器实例
        """
        if file_type.lower() == 'pdf':
            return PDFLoader(file_path, **kwargs)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")