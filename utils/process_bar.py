# coding=utf-8
"""
    @Author: Jacob
    @Date  : 2025/4/20
    @Desc  : 定义随机色进度条
"""

from rich.progress import (
    Progress, 
    BarColumn, 
    TextColumn, 
    TimeRemainingColumn,
    TimeElapsedColumn,
    ProgressColumn
)
from rich.text import Text

class PercentageColumn(ProgressColumn):
    """自定义百分比列"""
    def render(self, task) -> Text:
        return Text(f"{task.completed}/{task.total} ({task.percentage:>.1f}%)")

def create_progress_bar():
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None, style="cyan", complete_style="bright_magenta"),
        PercentageColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        expand=True
    )