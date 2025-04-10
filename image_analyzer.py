from typing import List, Optional
from PIL import Image
from openai import OpenAI
import os
import base64
import io

class ImageAnalyzer:
    """图片内容分析器，使用qwen2.5-vl-max模型进行图片内容解析"""
    
    def __init__(self, api_key: str):
        """初始化图片分析器
        
        Args:
            api_key: 通义千问API密钥
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    def analyze_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """分析单张图片的内容
        
        Args:
            image: PIL Image对象
            prompt: 可选的提示词，用于引导模型关注特定内容
        
        Returns:
            str: 图片内容的文本描述
        """
        try:
            # 确保图片是RGB模式
            if not isinstance(image, Image.Image):
                raise ValueError("输入必须是PIL Image对象")
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 将图片转换为base64格式
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=95)
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
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
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
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
                    model="qwen-vl-max-latest",
                    messages=messages
                )
                return completion.choices[0].message.content
            except Exception as e:
                raise Exception(f"API调用失败: {str(e)}")
                
        except Exception as e:
            raise Exception(f"图片分析失败: {str(e)}")
    
    def analyze_images(self, images: List[Image.Image], prompt: Optional[str] = None) -> List[str]:
        """批量分析多张图片的内容
        
        Args:
            images: PIL Image对象列表
            prompt: 可选的提示词，用于引导模型关注特定内容
        
        Returns:
            List[str]: 每张图片对应的内容描述列表
        """
        if not isinstance(images, list):
            raise ValueError("输入必须是图片列表")
            
        results = []
        for image in images:
            result = self.analyze_image(image, prompt)
            if not isinstance(result, str):
                raise ValueError(f"单张图片分析结果类型错误: 期望str类型，实际为{type(result)}")
            results.append(result)
        return results