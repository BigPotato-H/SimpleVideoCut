import os
from pathlib import Path
from win32com import client
from config import RUN_DIR, PPT_FILE

def ppt_to_images(ppt_path: str, out_dir: str, format: int = 17):
    """
    PPT → 每页图片 (PNG)
    format=17 对应 PNG
    """
    ppt_path = Path(ppt_path).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 打开 PowerPoint
    powerpoint = client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = 1

    presentation = powerpoint.Presentations.Open(str(ppt_path), WithWindow=False)
    
    # 导出每页为图片
    for i, slide in enumerate(presentation.Slides, start=1):
        slide_path = out_dir / f"slide_{i:03d}.png"
        slide.Export(str(slide_path), 'PNG')
        print(f"✅ 导出 {slide_path}")

    presentation.Close()
    powerpoint.Quit()

if __name__ == "__main__":
    ppt_to_images(PPT_FILE, RUN_DIR/"slides_images")
