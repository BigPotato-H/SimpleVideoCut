# scripts/transcribe.py
import json
from pathlib import Path
from faster_whisper import WhisperModel
from config import CUT_AUDIO, SUBTITLE_JSON



def run(
    audio_path: Path = CUT_AUDIO,
    output_path: Path = SUBTITLE_JSON,
    model_size="medium",  # 中文口播推荐 medium
    device="cpu",         # 有 GPU 可改成 "cuda"
    compute_type="int8"   # cpu 友好
):
    print("🔊 加载 Whisper 模型...")
    model = WhisperModel(model_size, 
                         device=device, 
                         compute_type=compute_type)
                        #  cache_dir=Path("D:/0hn/py-code/SimpleVideoCut/whisper_cache"))

    print("📝 识别中...")
    segments, info = model.transcribe(
        str(audio_path),
        language="zh",
        beam_size=5,
        vad_filter=True,  # 去掉静音
        vad_parameters=dict(min_silence_duration_ms=300)
    )

    subtitles = []
    for seg in segments:
        subtitles.append({
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip()
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(subtitles, f, ensure_ascii=False, indent=2)

    print(f"✅ 字幕生成完成: {output_path}")
    print(f"📄 段落数: {len(subtitles)}")

if __name__ == "__main__":
    run()
