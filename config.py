from datetime import datetime
from pathlib import Path
from utils import env
# ===== 1. 注入 ffmpeg 到当前进程环境 =====
env.setup_ffmpeg()

# 换成自己的视频路径
root_path = r"D:\0hn\000vehicle\0-oral\\"

# 换成自己的视频名称
input_video = "378630b72a0fd815dfd57e6ef84f2995.mp4"     

BASE_OUTPUT_DIR = Path(root_path)
#日期
RUN_DATE = datetime.now().strftime("%Y-%m-%d")
RUN_DIR = BASE_OUTPUT_DIR / RUN_DATE
RUN_DIR.mkdir(parents=True, exist_ok=True)

INPUT_VIDEO = BASE_OUTPUT_DIR / input_video
#提出来了音频
AUDIO_PATH = RUN_DIR / "0audio.wav"
#识别音频中的暂停（要被cut的）
PAUSE_JSON_PATH = RUN_DIR / "1pauses.json"
#识别音频中的拍手（标记重录的，需要手动确认剪掉的范围）
CLAP_JSON_PATH=RUN_DIR / "2clap_markers.json"

# 剪辑后的视频
CUT_VIDEO = RUN_DIR / "3cut_video.mp4"
# 剪辑后的音频
CUT_AUDIO = RUN_DIR / "3cut_audio.wav"
# 输出字幕（可手动修改）
SUBTITLE_JSON = RUN_DIR / "4subtitles.json"
# 输出字幕srt（导入剪映用）
SRT_FILE = RUN_DIR / "5subtitles.srt"