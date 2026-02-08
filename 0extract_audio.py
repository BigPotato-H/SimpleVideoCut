import os
import subprocess

import config


# ===== 2. 输入输出 =====
root_path = config.root_path
input_video = root_path + config.input_video     
output_audio = str(config.AUDIO_PATH)

# ===== 3. ffmpeg 命令 =====
cmd = [
    "ffmpeg",
    "-y",              # 覆盖输出
    "-i", input_video,
    "-vn",             # 不要视频
    "-ac", "1",        # 单声道
    "-ar", "16000",    # 16k 采样率
    output_audio
]

print("Running:", " ".join(cmd))
subprocess.run(cmd, check=True)

print("✅ 音频提取完成:", output_audio)
