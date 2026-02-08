# detect_pause.py
import json
import wave
import numpy as np
from pathlib import Path
import config

def run(
    audio_path= config.AUDIO_PATH,
    output_json=config.PAUSE_JSON_PATH,
    frame_ms=30,          # 每帧多长（毫秒）
    silence_thresh=0.01,  # 音量阈值（越小越严格）
    min_silence_ms=700    # 至少多长才算停顿
):
    """
    从 wav 音频中检测停顿区间
    """

    audio_path = Path(audio_path)
    output_json = Path(output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    # 1. 读取 wav
    with wave.open(str(audio_path), "rb") as wf:
        assert wf.getnchannels() == 1, "只支持单声道"
        sample_rate = wf.getframerate()
        samples = wf.readframes(wf.getnframes())
        audio = np.frombuffer(samples, dtype=np.int16).astype(np.float32)
        audio /= 32768.0  # 归一化到 [-1, 1]

    frame_size = int(sample_rate * frame_ms / 1000)
    total_frames = len(audio) // frame_size

    pauses = []
    silence_start = None

    # 2. 扫描每一帧
    for i in range(total_frames):
        frame = audio[i * frame_size:(i + 1) * frame_size]
        energy = np.sqrt(np.mean(frame ** 2))

        t = i * frame_ms / 1000.0

        if energy < silence_thresh:
            if silence_start is None:
                silence_start = t
        else:
            if silence_start is not None:
                dur = t - silence_start
                if dur * 1000 >= min_silence_ms:
                    pauses.append({
                        "start": round(silence_start, 3),
                        "end": round(t, 3),
                        "duration": round(dur, 3)
                    })
                silence_start = None

    # 3. 处理结尾是静音的情况
    if silence_start is not None:
        end_t = total_frames * frame_ms / 1000.0
        dur = end_t - silence_start
        if dur * 1000 >= min_silence_ms:
            pauses.append({
                "start": round(silence_start, 3),
                "end": round(end_t, 3),
                "duration": round(dur, 3)
            })

    # 4. 保存
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(pauses, f, ensure_ascii=False, indent=2)

    print(f"[detect_pause] found {len(pauses)} pauses")
    print(f"[detect_pause] saved to {output_json}")


if __name__ == "__main__":
    run()
