# PDFInsight

## 项目描述

### 技术视角
PDFInsight是一个基于Python的高性能文档智能处理系统，集成了先进的视觉模型实现PDF文档的智能解析。系统采用模块化设计，支持文档加载、图片分析、文本分块等核心功能，并提供灵活的存储策略。通过多模态分析技术，实现了文档内容的精准提取和结构化处理。

## 项目结构

```
PDFInsight/
├── .gitignore          # Git忽略规则
├── .vscode/            # VSCode配置
│   └── settings.json   # 编辑器设置
├── README.md           # 项目说明文档
├── config.yaml         # 配置文件
├── document_loader.py  # 文档加载模块
├── image_analyzer.py   # 图像分析模块
├── main.py             # 主程序入口
├── model_config.py     # 模型配置模块
├── requirements.txt    # 项目依赖
├── storage_manager.py  # 存储管理模块
└── text_chunker.py     # 文本分块模块
```

## 核心功能

- 支持PDF文档智能加载和解析
- 基于通义千问API的高精度图像文字识别
- 灵活的文本分块策略（固定长度、句子、段落）
- 可扩展的存储管理（支持JSON、CSV格式）
- 友好的进度显示和错误处理

## 使用方法
```bash
git clone https://github.com/Jacob-Yangman/PDFInsight.git
cd PDFInsight
```


1. 安装依赖：
```bash
conda create -n pdf_insight python=3.10
conda activate pdf_insight
```
```bash
pip install -r requirements.txt
```

2. 安装poppler（PDF转图片工具）：
- Windows：
  - 下载poppler： https://github.com/oschwartz10612/poppler-windows/releases
  - 解压到C:\poppler目录
  - 将C:\poppler\Library\bin添加到系统PATH环境变量

- MacOS：
```bash
brew install poppler
```

- Linux：
```bash
sudo apt-get install poppler-utils
```

3. 设置API密钥：
```python
export DASHSCOPE_API_KEY="your_api_key_here"
```

4. 运行程序：
```python
python main.py
```

## 配置选项

- `chunk_strategy`: 分块策略 ('fixed'、'sentence'、'paragraph')
- `save_format`: 存储格式 ('json'、'csv')
- `prompt`: 自定义图像分析提示词
- `output_dir`: 自定义输出目录