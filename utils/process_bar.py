from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
import random

def create_progress_bar():
    random_color = f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})"
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(style=random_color),
        TimeRemainingColumn(),
    )