# coding=utf-8
"""
    @Author: Jacob
    @Date  : 2025/4/20
    @Desc  : 测试用户API_KEY（Qwen）
"""

from model_config import ModelConfig
from image_analyzer import ImageAnalyzer
from PIL import Image
from io import BytesIO
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

class APIKeyTester:
    """API密钥测试工具类"""
    
    @staticmethod
    def test_api_key(model_config: ModelConfig) -> bool:
        """测试API密钥是否有效"""
        try:
            logger.info("正在测试API_KEY...")
            # 下载测试图片
            # 加载本地测试图片
            test_image_path = Path(__file__).parent.parent / "test" / "test_img.jpeg"
            test_image = Image.open(test_image_path)
            
            # 转换为RGB模式
            if test_image.mode != 'RGB':
                test_image = test_image.convert('RGB')
                
            # 创建分析器并测试API调用
            analyzer = ImageAnalyzer(model_config)
            result = analyzer.analyze_image(test_image, "请描述这张图片")
            
            if result and len(result.strip()) > 0:
                logger.info("API_KEY测试通过")
                return True
            return False
        except Exception as e:
            logger.error(f"API_KEY测试失败: {str(e)}")
            return False