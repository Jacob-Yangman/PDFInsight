# PDFInsight

## 项目描述

### 技术视角
PDFInsight是一个基于Python的高性能文档智能处理系统，集成了先进的视觉模型实现PDF文档的智能解析。系统采用模块化设计，支持文档加载、图片分析、文本分块等核心功能，并提供灵活的存储策略。通过多模态分析技术，实现了文档内容的精准提取和结构化处理。

## 项目结构

```
PDFInsight/
├── document_loader.py   # 文档加载模块
├── image_analyzer.py    # 图像分析模块
├── text_chunker.py     # 文本分块模块
├── storage_manager.py  # 存储管理模块
├── main.py            # 主程序入口
├── requirements.txt   # 项目依赖
├── pdfs/             # PDF文档目录
└── output/           # 输出结果目录
```

## 核心功能

- 支持PDF文档智能加载和解析
- 基于通义千问API的高精度图像文字识别
- 灵活的文本分块策略（固定长度、句子、段落）
- 可扩展的存储管理（支持JSON、CSV格式）
- 友好的进度显示和错误处理

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 设置API密钥：
```python
export DASHSCOPE_API_KEY="your_api_key_here"
```

3. 运行程序：
```python
python main.py
```

## 配置选项

- `chunk_strategy`: 分块策略 ('fixed'、'sentence'、'paragraph')
- `save_format`: 存储格式 ('json'、'csv')
- `prompt`: 自定义图像分析提示词
- `output_dir`: 自定义输出目录