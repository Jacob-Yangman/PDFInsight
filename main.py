# coding=utf-8
"""
    @Author: Jacob
    @Date  : 2025/4/20
    @Desc  : 入口函数
"""

import os
from typing import List, Optional
from pathlib import Path
from openai import OpenAI
from document_loader import DocumentLoaderFactory
from image_analyzer import ImageAnalyzer
from text_chunker import TextChunker, FixedLengthChunker, SentenceChunker, ParagraphChunker
from storage_manager import StorageManager, JsonStorageStrategy
import yaml
from model_config import ModelConfig, load_model_config
from utils.api_key_tester import APIKeyTester
from concurrent.futures import ThreadPoolExecutor
from utils.process_bar import create_progress_bar
import logging
from logging_config import setup_logging
import httpx
from datetime import datetime  # 新增导入

# 初始化日志
setup_logging()

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)




def load_prompt(prompt_name: str) -> str:
    """加载提示文本"""
    prompt_file = f"{prompt_name}.txt"
    prompt_path = Path(__file__).parent / prompt_file
    if not prompt_path.exists():
        prompt_path = Path(__file__).parent / "prompts" / prompt_file
    return prompt_path.read_text(encoding="utf-8")

class DocumentProcessor:
    """文档处理器，整合文档加载、图片分析、文本分块和存储功能"""
    
    def __init__(self, model_config: ModelConfig):
        """初始化文档处理器
        
        Args:
            model_config: 模型配置对象
        """
        self.image_analyzer = ImageAnalyzer(model_config)
        self.chunker = TextChunker()  # 默认不指定策略
        self.storage_manager = StorageManager()  # 默认使用JSON存储
    
    def _ensure_dir_exists(self, dir_path: str):
        """确保目录存在，不存在则创建"""
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            
    def _validate_api_key(self, model_config: ModelConfig) -> bool:
        """验证API_KEY是否有效"""
        return APIKeyTester.test_api_key(model_config)
    
    def process_document(self, file_path: str, output_dir: Optional[str] = None,
                        prompt: Optional[str] = None,
                        chunk_strategy: Optional[str] = 'fixed',
                        save_format: Optional[str] = 'json',
                        overwrite_output: bool = True) -> List[str]:
            
        logger.info(f"正在处理文档 {file_path}".center(40, '*'))
        

        prompt_text = load_prompt(prompt) if isinstance(prompt, str) else prompt
        if output_dir:
            self._ensure_dir_exists(output_dir)
        
        # 1. 加载文档并转换为图片
        loader = DocumentLoaderFactory.create_loader(file_path, 'pdf')
        images = loader.load()
                
        # 2. 使用多图像分析功能
        texts = self.image_analyzer.analyze_images(images, prompt_text)
        combined_text = '\n\n'.join(texts)

        # 保存解析后的中间结果为 MD 文件
        if output_dir:
            intermediate_output_path = Path(output_dir) / f'{Path(file_path).stem}_extracted_content.md'
        else:
            intermediate_output_path = Path(file_path).with_suffix('_extracted_content.txt')
        
        with open(intermediate_output_path, 'w', encoding='utf-8') as f:
            f.write(combined_text)
        
        logger.info(f'解析结果已保存到: {intermediate_output_path}')
        
        # 3. 根据选择的策略设置分块器
        # 修改策略设置部分
        if chunk_strategy in ['fixed', 'sentence', 'paragraph', 'table']:
            self.chunker.set_strategy(self.chunker.strategies[chunk_strategy])
        else:
            self.chunker.set_strategy(FixedLengthChunker())
        
        # 4. 文本分块
        with create_progress_bar() as progress:
            task_chunk = progress.add_task("文本分块", total=1)
            chunks = self.chunker.chunk_text(combined_text)
            progress.update(task_chunk, advance=1)
            
        # 5. 保存文本块到本地
        if output_dir:
            output_path = Path(output_dir) / f'{Path(file_path).stem}_chunks.{save_format}'
        else:
            output_path = Path(file_path).with_suffix(f'.chunks.{save_format}')

        if not overwrite_output:
            counter = 1
            original_stem = output_path.stem
            while output_path.exists():
                output_path = output_path.with_name(f"{original_stem}_{counter}{output_path.suffix}")
                counter += 1

        with create_progress_bar() as progress:
            task_save = progress.add_task("保存文本块", total=len(chunks))
            self.storage_manager.save_chunks(chunks, str(output_path), save_format)
            progress.update(task_save, completed=len(chunks))
            
        logger.info(f'文本块已保存到: {output_path}')
        print('\n预览前3个文本块：')
        for i, chunk in enumerate(chunks[:3], 1):
            print(f'\n块 {i}:\n{chunk}\n{"-"*50}')
            
        logger.info("*" * 80)


def main():

    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    overwrite_output = config['pdf'].get('overwrite_output', True)
    model_config = load_model_config()
    processor = DocumentProcessor(model_config)
    
    # 验证API_KEY
    if not processor._validate_api_key(model_config):
        print("API_KEY无效，请检查配置后重试")
        return
        
    # 处理文档
    try:
        input_dir = Path(config['pdf']['input_dir'])
        for pdf_file in input_dir.glob('*.pdf'):
            processor.process_document(
                str(pdf_file),
                output_dir=config['pdf']['output_dir'],
                prompt=config['pdf']['default_prompt'],
                chunk_strategy=config['pdf']['chunk_strategy'],
                save_format=config['pdf']['save_format'],
                overwrite_output=overwrite_output
            )
        
    except Exception as e:
        print(f'处理文档时出错: {str(e)}')


if __name__ == '__main__':
    main()


