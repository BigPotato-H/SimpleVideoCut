# detect_clap.py
import json
import wave
import numpy as np
from pathlib import Path

from config import AUDIO_PATH, CLAP_JSON_PATH


def run(
    audio_path: Path = AUDIO_PATH,
    output_json: Path = CLAP_JSON_PATH,
    frame_ms=10,          # 更细，抓瞬态
    peak_thresh=0.6,      # 能量峰值阈值（关键参数）
    min_gap=0.5           # 两次拍手最小间隔（秒）
):
    """
    检测拍手 / 明显瞬态声，输出 marker
    """

    # 1. 读音频
    with wave.open(str(audio_path), "rb") as wf:
        assert wf.getnchannels() == 1, "只支持单声道"
        sr = wf.getframerate()
        samples = wf.readframes(wf.getnframes())
        audio = np.frombuffer(samples, dtype=np.int16).astype(np.float32)
        audio /= 32768.0

    frame_size = int(sr * frame_ms / 1000)
    total_frames = len(audio) // frame_size

    markers = []
    last_mark_time = -999

    # 2. 扫描瞬时能量
    for i in range(total_frames):
        frame = audio[i * frame_size:(i + 1) * frame_size]
        peak = np.max(np.abs(frame))
        t = i * frame_ms / 1000.0

        if peak > peak_thresh and (t - last_mark_time) > min_gap:
            markers.append({
                "type": "clap",
                "time": round(t, 3)
            })
            last_mark_time = t

    # 3. 保存
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(markers, f, ensure_ascii=False, indent=2)

    print(f"👏 detected {len(markers)} claps")
    print(f"📍 saved to {output_json}")


if __name__ == "__main__":
    run()
