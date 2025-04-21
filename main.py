import os
from typing import List, Optional
from pathlib import Path
import random
from tqdm import tqdm

from document_loader import DocumentLoaderFactory
from image_analyzer import ImageAnalyzer
from text_chunker import TextChunker, FixedLengthChunker, SentenceChunker, ParagraphChunker
from storage_manager import StorageManager, JsonStorageStrategy
import yaml
from model_config import load_model_config
from concurrent.futures import ThreadPoolExecutor

def load_prompt(prompt_name: str) -> str:
    """从prompts目录加载提示文本"""
    prompt_path = Path(__file__).parent / "prompts" / f"{prompt_name}.txt"
    return prompt_path.read_text(encoding="utf-8")

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
    
    def _ensure_dir_exists(self, dir_path: str):
        """确保目录存在，不存在则创建"""
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            
    def process_document(self, file_path: str, output_dir: Optional[str] = None,
                        prompt: Optional[str] = None,
                        chunk_strategy: Optional[str] = 'fixed',
                        save_format: Optional[str] = 'json') -> List[str]:
        print(f"正在加载文档 {file_path}")
        # 加载提示
        prompt_text = load_prompt(prompt) if isinstance(prompt, str) else prompt
        # 确保输出目录存在
        if output_dir:
            self._ensure_dir_exists(output_dir)
        
        print(f"文档 {file_path} 加载完成")
        # 1. 加载文档并转换为图片
        loader = DocumentLoaderFactory.create_loader(file_path, 'pdf')
        images = loader.load()
        
        print(f"文档 {file_path} 已转换为图片，正在解析图片内容")
        
        # 2. 使用多图像分析功能
        texts = self.image_analyzer.analyze_images(images, prompt_text)
        combined_text = '\n\n'.join(texts)
        
        print(f"文档 {file_path} 图片分析完成，开始根据策略进行文本分块")
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
        
        print(f"文档 {file_path} 文本分块完成，开始保存文本块")
        # 5. 保存文本块到本地
        if output_dir:
            output_path = Path(output_dir) / f'{Path(file_path).stem}.chunks.{save_format}'
        else:
            output_path = Path(file_path).with_suffix(f'.chunks.{save_format}')
        
        with tqdm(total=1, desc='保存文本块', colour=random_color()) as pbar:
            self.storage_manager.save_chunks(chunks, str(output_path), save_format)
            pbar.update(1)
        
        print(f'文本块已保存到: {Path(output_dir) / Path(file_path).stem}.chunks.json')
        return chunks

def main():
    # 加载配置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    model_config = load_model_config()
    processor = DocumentProcessor(model_config)
    
    # 处理文档
    try:
        input_dir = Path(config['pdf']['input_dir'])
        for pdf_file in input_dir.glob('*.pdf'):
            chunks = processor.process_document(
                str(pdf_file),
                output_dir=config['pdf']['output_dir'],
                prompt=config['pdf']['default_prompt'],
                chunk_strategy=config['pdf']['chunk_strategy'],
                save_format=config['pdf']['save_format']
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


