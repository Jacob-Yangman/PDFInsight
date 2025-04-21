from typing import List, Optional
from PIL import Image
from openai import OpenAI
import base64
import io
from model_config import ModelConfig
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

class ImageAnalyzer:
    def __init__(self, config: ModelConfig):
        try:
            self.client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
            self.model_name = config.name
        except Exception as e:
            raise ValueError(f"模型初始化失败: {str(e)}")
    
    def _image_to_hashable(self, image: Image.Image) -> str:
        """将图片转换为可哈希的 base64 字符串"""
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    @lru_cache(maxsize=100)
    def _analyze_image_cached(self, image_hash: str, prompt: Optional[str] = None) -> str:
        """带缓存的图片分析方法"""
        # 准备对话内容
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_hash}"}
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
                timeout=300  # 设置超时
            )
            if not completion.choices:
                raise ValueError("API返回结果为空")
            return completion.choices[0].message.content
        except Exception as e:
            print(f"图片分析失败，将重试: {str(e)}")
            raise

    def analyze_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """分析单张图片的内容"""
        try:
            # 确保图片是RGB模式
            if not isinstance(image, Image.Image):
                raise ValueError("输入必须是PIL Image对象")
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image_hash = self._image_to_hashable(image)
            return self._analyze_image_cached(image_hash, prompt)
        except Exception as e:
            print(f"图片处理失败: {str(e)}")
            raise

    def analyze_images(self, images: List[Image.Image], prompt: Optional[str] = None) -> List[str]:
        """批量分析多张图片的内容"""
        if not isinstance(images, list):
            raise ValueError("输入必须是图片列表")
        
        # 使用线程池并行处理图片分析
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.analyze_image, image, prompt)
                for image in images
            ]
            
            results = []
            for future in futures:
                try:
                    result = future.result()
                    if not isinstance(result, str):
                        raise ValueError(f"单张图片分析结果类型错误: 期望str类型，实际为{type(result)}")
                    results.append(result)
                except Exception as e:
                    print(f"图片分析失败: {str(e)}")
                    results.append("图片分析失败")
            
            return results