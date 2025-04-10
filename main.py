import os
from typing import List, Optional
from pathlib import Path
import random
from tqdm import tqdm

from document_loader import DocumentLoaderFactory
from image_analyzer import ImageAnalyzer
from text_chunker import TextChunker, FixedLengthChunker, SentenceChunker, ParagraphChunker
from storage_manager import StorageManager, JsonStorageStrategy

class DocumentProcessor:
    """文档处理器，整合文档加载、图片分析、文本分块和存储功能"""
    
    def __init__(self, api_key: str):
        """初始化文档处理器
        
        Args:
            api_key: 通义千问API密钥
        """
        self.image_analyzer = ImageAnalyzer(api_key)
        self.chunker = TextChunker(FixedLengthChunker())  # 默认使用固定长度分块
        self.storage_manager = StorageManager()  # 默认使用JSON存储
    
    def process_document(self, file_path: str, output_dir: Optional[str] = None,
                        prompt: Optional[str] = None,
                        chunk_strategy: Optional[str] = 'fixed',
                        save_format: Optional[str] = 'json') -> List[str]:
        """处理文档：加载、解析、分块和存储
        
        Args:
            file_path: PDF文件路径
            output_dir: 输出目录路径，默认为None（使用输入文件所在目录）
            prompt: 可选的图片分析提示词
            chunk_strategy: 分块策略，可选'fixed'、'sentence'或'paragraph'
            save_format: 存储格式，可选'json'或'csv'
            
        Returns:
            List[str]: 处理后的文本块列表
        """
        # 1. 加载文档并转换为图片
        loader = DocumentLoaderFactory.create_loader(file_path, 'pdf')
        images = loader.load()
        
        # 设置随机颜色的进度条
        def random_color():
            return f'#{random.randint(0, 0xFFFFFF):06x}'
        
        # 2. 分析图片内容
        texts = []
        for img in tqdm(images, desc='分析图片', colour=random_color()):
            text = self.image_analyzer.analyze_image(img, prompt)
            texts.append(text)
        combined_text = '\n\n'.join(texts)
        
        # 3. 根据选择的策略设置分块器
        if chunk_strategy == 'sentence':
            self.chunker.set_strategy(SentenceChunker())
        elif chunk_strategy == 'paragraph':
            self.chunker.set_strategy(ParagraphChunker())
        else:  # 默认使用固定长度分块
            self.chunker.set_strategy(FixedLengthChunker())
        
        # 4. 对文本进行分块
        with tqdm(total=1, desc='文本分块', colour=random_color()) as pbar:
            chunks = self.chunker.chunk_text(combined_text)
            pbar.update(1)
        
        # 5. 保存文本块到本地
        if output_dir:
            output_path = Path(output_dir) / f'{Path(file_path).stem}.chunks.{save_format}'
        else:
            output_path = Path(file_path).with_suffix(f'.chunks.{save_format}')
        
        with tqdm(total=1, desc='保存文本块', colour=random_color()) as pbar:
            self.storage_manager.save_chunks(chunks, str(output_path), save_format)
            pbar.update(1)
        
        return chunks

def main():
    # 示例用法
    api_key = os.getenv("DASHSCOPE_API_KEY")  # 替换为实际的API密钥
    processor = DocumentProcessor(api_key)
    
    # 处理文档示例
    try:
        file_path = r'pdfs\Improved.pdf'  # 替换为实际的PDF文件路径
        output_dir = 'output'  # 指定输出目录
        chunks = processor.process_document(
            file_path,
            output_dir=output_dir,
            prompt='请详细提取文档中的文字内容，包括标题、正文和表格中的文本。',
            chunk_strategy='paragraph',
            save_format='json'  # 可选'json'或'csv'
        )
        
        print(f'文档处理完成，共生成 {len(chunks)} 个文本块')
        print(f'文本块已保存到: {Path(output_dir) / Path(file_path).stem}.chunks.json')
        
        # 打印前3个文本块作为预览
        print('\n预览前3个文本块：')
        for i, chunk in enumerate(chunks[:3], 1):
            print(f'\n块 {i}:\n{chunk}\n{"-"*50}')
            
    except Exception as e:
        print(f'处理文档时出错: {str(e)}')

if __name__ == '__main__':
    main()