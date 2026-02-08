import json
import subprocess
from pathlib import Path
from win32com import client
from config import RUN_DIR, PPT_FILE, PPT_CONFIG_JSON, PPT_VIDEO_OUTPUT
import shutil
# -----------------------------
# 配置
# -----------------------------
OUTPUT_DIR = RUN_DIR / "slides_images"
FPS = 25  # 可修改帧率
PPT_WIDTH = 1920  # PPT 画布宽度
PPT_HEIGHT = 1080  # PPT 画布高度

# -----------------------------
# Step 1: PPT → 图片（高清）
# -----------------------------
def ppt_to_images(ppt_path: str, out_dir: Path, width=PPT_WIDTH, height=PPT_HEIGHT):
    if out_dir.exists():
        shutil.rmtree(out_dir)   
    out_dir.mkdir(parents=True)
    powerpoint = client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = 1
    presentation = powerpoint.Presentations.Open(str(Path(ppt_path).resolve()), WithWindow=False)
    
    for i, slide in enumerate(presentation.Slides, start=1):
        slide_path = out_dir / f"slide_{i:03d}.png"
        # 指定宽高导出
        slide.Export(str(slide_path), 'PNG', width, height)
        print(f"✅ 导出 {slide_path}")
    
    presentation.Close()
    powerpoint.Quit()

# -----------------------------
# Step 2: 图片 → 视频片段（高清）
# -----------------------------
def image_to_video(image_path: Path, duration: float, fps: int):
    output_video = image_path.with_suffix(".mp4")
    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-crf", "18",         # 高质量输出
        "-vf", f"fps={fps}",
        str(output_video)
    ]
    subprocess.run(cmd, check=True)
    return output_video

# -----------------------------
# Step 3: 拼接所有视频片段
# -----------------------------
def concat_videos(video_files, output_path: Path):
    list_file = output_path.parent / "concat.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for vf in video_files:
            f.write(f"file '{vf.as_posix()}'\n")
    
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path)
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ 拼接完成 {output_path}")

# -----------------------------
# Step 4: 主流程
# -----------------------------
def run():
    # 读取 slides.json
    with open(PPT_CONFIG_JSON, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    slides_config = config["slides"]
    
    # PPT → 图片（高清）
    ppt_to_images(PPT_FILE, OUTPUT_DIR)
    
    # 图片 → 视频
    video_files = []
    for slide in slides_config:
        index = slide["index"]
        duration = slide["duration"]
        image_path = OUTPUT_DIR / f"slide_{index:03d}.png"
        vf = image_to_video(image_path, duration, FPS)
        video_files.append(vf)
    
    # 拼接成完整视频
    concat_videos(video_files, PPT_VIDEO_OUTPUT)

if __name__ == "__main__":
    run()
