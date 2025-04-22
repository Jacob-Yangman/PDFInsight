# coding=utf-8
"""
    @Author: Jacob
    @Date  : 2025/4/20
    @Desc  : 定义随机色进度条
"""

from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
import random

def create_progress_bar():
    random_color = f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})"
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(style=random_color),
        TimeRemainingColumn(),
    )