from abc import ABC, abstractmethod
from typing import List
import re
import spacy
import argparse

class ChunkStrategy(ABC):
    """文本分块策略的抽象基类"""
    
    @abstractmethod
    def split(self, text: str) -> List[str]:
        """将文本分割成块
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 文本块列表
        """
        pass

class FixedLengthChunker(ChunkStrategy):
    """固定长度分块策略"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """初始化固定长度分块器
        
        Args:
            chunk_size: 每个块的目标长度
            overlap: 相邻块之间的重叠字符数
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> List[str]:
        code_blocks = re.findall(r'```.*?```', text, re.DOTALL)
        text_without_code = re.sub(r'```.*?```', 'CODE_BLOCK_PLACEHOLDER', text, flags=re.DOTALL)

        chunks = []
        start = 0
        text_length = len(text_without_code)

        while start < text_length:
            end = start + self.chunk_size
            if end >= text_length:
                chunk = text_without_code[start:]
            else:
                # 在chunk_size位置寻找最近的句子结束符
                next_period = text_without_code.find('。', end - 50, end + 50)
                if next_period != -1:
                    end = next_period + 1
                chunk = text_without_code[start:end]

            # 恢复代码块
            chunk = self._restore_code_blocks(chunk, code_blocks)
            chunks.append(chunk)
            start = end - self.overlap

        return chunks

    def _restore_code_blocks(self, chunk, code_blocks):
        index = 0
        while 'CODE_BLOCK_PLACEHOLDER' in chunk:
            if index < len(code_blocks):
                chunk = chunk.replace('CODE_BLOCK_PLACEHOLDER', code_blocks[index], 1)
                index += 1
            else:
                chunk = chunk.replace('CODE_BLOCK_PLACEHOLDER', '', 1)
        return chunk

class SentenceChunker(ChunkStrategy):
    """基于句子的分块策略"""
    
    def __init__(self, sentences_per_chunk: int = 3):
        """初始化句子分块器
        
        Args:
            sentences_per_chunk: 每个块包含的句子数
        """
        self.sentences_per_chunk = sentences_per_chunk
        try:
            self.nlp = spacy.load('zh_core_web_sm')
        except OSError:
            # 如果模型未下载，使用小型模型
            spacy.cli.download('zh_core_web_sm')
            self.nlp = spacy.load('zh_core_web_sm')

    def split(self, text: str) -> List[str]:
        code_blocks = re.findall(r'```.*?```', text, re.DOTALL)
        text_without_code = re.sub(r'```.*?```', 'CODE_BLOCK_PLACEHOLDER', text, flags=re.DOTALL)

        doc = self.nlp(text_without_code)
        sentences = list(doc.sents)
        chunks = []
        
        for i in range(0, len(sentences), self.sentences_per_chunk):
            chunk = sentences[i:i + self.sentences_per_chunk]
            chunk_text = ''.join([sent.text_with_ws for sent in chunk]).strip()
            # 恢复代码块
            chunk_text = self._restore_code_blocks(chunk_text, code_blocks)
            chunks.append(chunk_text)
        
        return chunks

    def _restore_code_blocks(self, chunk, code_blocks):
        index = 0
        while 'CODE_BLOCK_PLACEHOLDER' in chunk:
            if index < len(code_blocks):
                chunk = chunk.replace('CODE_BLOCK_PLACEHOLDER', code_blocks[index], 1)
                index += 1
            else:
                chunk = chunk.replace('CODE_BLOCK_PLACEHOLDER', '', 1)
        return chunk

class ParagraphChunker(ChunkStrategy):
    """基于段落的分块策略"""
    
    def __init__(self, paragraphs_per_chunk: int = 2):
        """初始化段落分块器
        
        Args:
            paragraphs_per_chunk: 每个块包含的段落数
        """
        self.paragraphs_per_chunk = paragraphs_per_chunk

    def split(self, text: str) -> List[str]:
        code_blocks = re.findall(r'```.*?```', text, re.DOTALL)
        text_without_code = re.sub(r'```.*?```', 'CODE_BLOCK_PLACEHOLDER', text, flags=re.DOTALL)

        # 使用多种段落分隔符进行分割
        paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text_without_code)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        chunks = []
        
        for i in range(0, len(paragraphs), self.paragraphs_per_chunk):
            chunk = paragraphs[i:i + self.paragraphs_per_chunk]
            chunk_text = '\n\n'.join(chunk)
            # 恢复代码块
            chunk_text = self._restore_code_blocks(chunk_text, code_blocks)
            chunks.append(chunk_text)
        
        return chunks

    def _restore_code_blocks(self, chunk, code_blocks):
        index = 0
        while 'CODE_BLOCK_PLACEHOLDER' in chunk:
            if index < len(code_blocks):
                chunk = chunk.replace('CODE_BLOCK_PLACEHOLDER', code_blocks[index], 1)
                index += 1
            else:
                chunk = chunk.replace('CODE_BLOCK_PLACEHOLDER', '', 1)
        return chunk

class TableChunker(ChunkStrategy):
    """专门处理表格内容的分块策略"""
    
    def chunk_text(self, text: str) -> List[str]:
        # 识别表格内容（假设表格已按prompt要求转换为Markdown格式）
        tables = []
        current_table = []
        in_table = False
        
        for line in text.split('\n'):
            if line.strip().startswith('|') and line.strip().endswith('|'):
                in_table = True
                current_table.append(line)
            elif in_table:
                tables.append('\n'.join(current_table))
                current_table = []
                in_table = False
        
        # 将每个表格作为独立分块
        return tables

    def split(self, text: str) -> List[str]:
        """兼容其他分块策略的split方法"""
        return self.chunk_text(text)

# 在TextChunker类中注册新策略
class TextChunker:
    def __init__(self, strategy=None):
        self.strategies = {
            'fixed': FixedLengthChunker(),
            'sentence': SentenceChunker(),
            'paragraph': ParagraphChunker(),
            'table': TableChunker()  # 新增表格分块策略
        }
        self.strategy = strategy

    def set_strategy(self, strategy: ChunkStrategy):
        """更改分块策略
        
        Args:
            strategy: 新的分块策略实例
        """
        self.strategy = strategy

    def chunk_text(self, text: str) -> List[str]:
        """使用当前策略对文本进行分块
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 文本块列表
        """
        return self.strategy.split(text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='单独调用文本分块器')
    parser.add_argument('-i', '--input', required=True, type=str, help='输入MD文件路径')
    parser.add_argument('-m', '--mode', required=True, type=str, 
                       choices=['fixed', 'sentence', 'paragraph', 'table'], 
                       help='分块模式: fixed(固定长度)/sentence(句子)/paragraph(段落)/table(表格)')
    parser.add_argument('-o', '--output', type=str, help='输出文件路径')
    
    args = parser.parse_args()
    
    # 读取 MD 文件内容
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 初始化分块器
    chunker = TextChunker()
    chunker.set_strategy(chunker.strategies[args.mode])
    
    # 进行分块
    chunks = chunker.chunk_text(text)
    
    # 打印分块结果
    if args.output:
        from storage_manager import StorageManager
        storage = StorageManager()
        curr_format = args.output.split('.')[-1] if '.' in args.output else 'json'
        storage.save_chunks(chunks, args.output, curr_format)
        print(f'分块结果已保存到: {args.output}')
    else:
        for i, chunk in enumerate(chunks, 1):
            print(f'块 {i}:\n{chunk}\n{"-"*50}')