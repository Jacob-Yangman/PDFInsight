from abc import ABC, abstractmethod
from typing import List
import re
import spacy

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
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            if end >= text_length:
                chunks.append(text[start:])
                break
            
            # 在chunk_size位置寻找最近的句子结束符
            next_period = text.find('.', end - 50, end + 50)
            if next_period != -1:
                end = next_period + 1
            
            chunks.append(text[start:end])
            start = end - self.overlap

        return chunks

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
        doc = self.nlp(text)
        sentences = list(doc.sents)
        chunks = []
        
        for i in range(0, len(sentences), self.sentences_per_chunk):
            chunk = sentences[i:i + self.sentences_per_chunk]
            chunks.append(''.join([sent.text_with_ws for sent in chunk]).strip())
        
        return chunks

class ParagraphChunker(ChunkStrategy):
    """基于段落的分块策略"""
    
    def __init__(self, paragraphs_per_chunk: int = 2):
        """初始化段落分块器
        
        Args:
            paragraphs_per_chunk: 每个块包含的段落数
        """
        self.paragraphs_per_chunk = paragraphs_per_chunk

    def split(self, text: str) -> List[str]:
        # 使用多种段落分隔符进行分割
        paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        chunks = []
        
        for i in range(0, len(paragraphs), self.paragraphs_per_chunk):
            chunk = paragraphs[i:i + self.paragraphs_per_chunk]
            chunks.append('\n\n'.join(chunk))
        
        return chunks

class TextChunker:
    """文本分块器主类，用于管理和使用不同的分块策略"""
    
    def __init__(self, strategy: ChunkStrategy):
        """初始化文本分块器
        
        Args:
            strategy: 分块策略实例
        """
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