from model_config import ModelConfig
from image_analyzer import ImageAnalyzer
from PIL import Image
import requests
from io import BytesIO
import logging
logger = logging.getLogger(__name__)

class APIKeyTester:
    """API密钥测试工具类"""
    
    @staticmethod
    def test_api_key(model_config: ModelConfig) -> bool:
        """测试API密钥是否有效"""
        try:
            # 下载测试图片
            test_image_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"
            response = requests.get(test_image_url)
            test_image = Image.open(BytesIO(response.content))
            
            # 转换为RGB模式
            if test_image.mode != 'RGB':
                test_image = test_image.convert('RGB')
                
            # 创建分析器并测试API调用
            analyzer = ImageAnalyzer(model_config)
            result = analyzer.analyze_image(test_image, "请描述这张图片")
            
            return bool(result and len(result.strip()) > 0)
        except Exception as e:
            logger.error(f"API_KEY测试失败: {str(e)}")
            return False