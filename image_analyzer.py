# coding=utf-8
"""
    @Author: Jacob
    @Date  : 2025/4/20
    @Desc  : 图片解析器，负责解析图片中的文字和图表信息
"""

from typing import List, Optional, Dict
from PIL import Image
from openai import OpenAI
import base64
import io
import pickle
from pathlib import Path
from model_config import ModelConfig
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from utils.process_bar import create_progress_bar
import logging
from concurrent.futures import as_completed
logger = logging.getLogger(__name__)

class ImageAnalyzer:
    def __init__(self, config: ModelConfig):
        try:
            self.client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
            self.model_name = config.name
            self.model_config = config
            self.cache_file = Path('cache/image_cache.pkl')
            self._load_cache()  # 加载持久化缓存
        except Exception as e:
            raise ValueError(f"模型初始化失败: {str(e)}")
    
    def _load_cache(self):
        """加载持久化缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    self._persistent_cache = pickle.load(f)
            except:
                self._persistent_cache = {}
        else:
            self._persistent_cache = {}
    
    def _save_cache(self):
        """保存持久化缓存"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self._persistent_cache, f)
    
    def _image_to_hashable(self, image: Image.Image) -> str:
        """将图片转换为可哈希的 base64 字符串"""
        buffer = io.BytesIO()
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(buffer, format='JPEG', quality=95)
        # 阿里云API要求纯base64编码，不带其他前缀
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _analyze_image_with_cache(self, image_hash: str, prompt: Optional[str] = None) -> str:
        """带缓存的图片分析方法"""
        # 检查图片大小是否超过API限制
        if len(image_hash) > 4 * 1024 * 1024:  # 4MB限制
            raise ValueError("图片大小超过API限制(4MB)")
        # 先检查持久化缓存
        cache_key = f"{image_hash}_{prompt if prompt else 'default'}"
        if cache_key in self._persistent_cache:
            # print(f"缓存命中: {cache_key[:10]}")  # 添加缓存命中输出
            return self._persistent_cache[cache_key]
        
        # 准备对话内容 - 修改为阿里云视觉API要求的格式
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",  # 修改为image_url
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_hash}"  # 添加data URL前缀
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt if prompt else "请详细描述这张图片中的内容，包括文字和图表信息。"
                    }
                ]
            }
        ]
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                timeout=300
            )
            if not completion.choices:
                raise ValueError("API返回结果为空")
            
            result = completion.choices[0].message.content
            # 保存到持久化缓存
            self._persistent_cache[cache_key] = result
            if len(self._persistent_cache) > getattr(self.model_config, 'image_cache_size', 100):
                # 清理最旧的缓存项
                oldest_key = next(iter(self._persistent_cache))
                del self._persistent_cache[oldest_key]
            return result
        except Exception as e:
            print(f"图片分析失败，将重试: {str(e)}")
            # 确保缓存文件被保存
            self._save_cache()
            raise

    def analyze_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """分析单张图片的内容"""
        try:
            if not isinstance(image, Image.Image):
                logger.error("输入必须是PIL Image对象")
                raise ValueError("输入必须是PIL Image对象")
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image_hash = self._image_to_hashable(image)
            return self._analyze_image_with_cache(image_hash, prompt)
        except Exception as e:
            logger.error(f"图片处理失败: {str(e)}")
            raise

    def __del__(self):
        """对象销毁时保存缓存"""
        self._save_cache()

    def analyze_images(self, images: List[Image.Image], prompt: Optional[str] = None) -> List[str]:
        """批量分析多张图片的内容"""
        if not isinstance(images, list):
            raise ValueError("输入必须是图片列表")
        
        with create_progress_bar() as progress:
            task = progress.add_task("解析中", total=len(images))
            
            results = []
            # 使用线程池并行处理图片分析
            with ThreadPoolExecutor() as executor:
                futures = list(executor.submit(self.analyze_image, image, prompt) for image in images)
                
                for future in as_completed(futures):  # 使用as_completed确保按完成顺序处理
                    try:
                        result = future.result()
                        if not isinstance(result, str):
                            raise ValueError(f"单张图片分析结果类型错误: 期望str类型，实际为{type(result)}")
                        results.append(result)
                    except Exception as e:
                        print(f"图片分析失败: {str(e)}")
                        results.append("图片分析失败")
                    finally:
                        progress.update(task, advance=1)
        
        return results