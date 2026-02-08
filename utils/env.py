# utils/env.py
import os

def setup_ffmpeg():
    ffmpeg_bin = r"D:\0hn\py-code\SimpleVideoCut\ThirdParty\ffmpeg-8.0.1-essentials_build\bin"
    os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ.get("PATH", "")
