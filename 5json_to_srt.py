# scripts/json_to_srt.py
import json
from pathlib import Path

from config import SUBTITLE_JSON, SRT_FILE  


def format_time(seconds: float) -> str:
    """把秒转成 SRT 时间格式 hh:mm:ss,ms"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def json_to_srt(json_path: Path, srt_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        subtitles = json.load(f)

    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, sub in enumerate(subtitles, start=1):
            start = format_time(sub["start"])
            end = format_time(sub["end"])
            text = sub["text"]
            f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")

    print(f"✅ SRT 生成完成: {srt_path}")

if __name__ == "__main__":
    json_to_srt(SUBTITLE_JSON, SRT_FILE)
