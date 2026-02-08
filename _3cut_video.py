import json
import subprocess
from pathlib import Path

from config import INPUT_VIDEO,RUN_DIR, PAUSE_JSON_PATH, CUT_VIDEO, CUT_AUDIO
import shutil

def load_pauses(pause_json: Path):
    with open(pause_json, "r", encoding="utf-8") as f:
        return json.load(f)

def merge_close_pauses(pauses, gap=0.3):
    merged = []
    for p in pauses:
        if not merged:
            merged.append(p)
            continue

        last = merged[-1]
        if p["start"] - last["end"] < gap:
            last["end"] = p["end"]
            last["duration"] = round(last["end"] - last["start"], 3)
        else:
            merged.append(p)

    return merged

def invert_pauses(pauses, video_duration, buffer=0.15):
    keep = []
    cur = 0.0

    for p in pauses:
        start = max(p["start"] - buffer, cur)
        end = min(p["end"] + buffer, video_duration)

        if start > cur:
            keep.append((cur, start))

        cur = end

    if cur < video_duration:
        keep.append((cur, video_duration))

    return keep


def get_video_duration(video: Path) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video)
    ]
    out = subprocess.check_output(cmd)
    return float(out.strip())


def extract_segments(video: Path, segments, work_dir: Path):
    seg_files = []

    for i, (start, end) in enumerate(segments):
        out = work_dir / f"seg_{i:03d}.mp4"
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", f"{start}",
            "-to", f"{end}",
            "-i", str(video),
            "-c", "copy",
            str(out)
        ]
        subprocess.run(cmd, check=True)
        seg_files.append(out)

    return seg_files


def concat_segments(seg_files, output_file: Path, is_audio=False):
    list_file = output_file.parent / "concat.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for seg in seg_files:
            f.write(f"file '{seg.as_posix()}'\n")

    if is_audio:
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-ac", "1",
            "-ar", "16000",
            "-c:a", "pcm_s16le",
            str(output_file)
        ]
    else:
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(output_file)
        ]

    subprocess.run(cmd, check=True)




def run():
    video = INPUT_VIDEO
    pauses = load_pauses(PAUSE_JSON_PATH)
    pauses = merge_close_pauses(pauses, gap=0.3)
    duration = get_video_duration(video)
    keep_segments = invert_pauses(pauses, duration)

    print(f"🎬 video duration: {duration:.2f}s")
    print(f"✂️ keep segments: {len(keep_segments)}")

    seg_dir = RUN_DIR / "segments"
    if seg_dir.exists():
        shutil.rmtree(seg_dir)   
    seg_dir.mkdir(parents=True)

    seg_files_video = []
    seg_files_audio = []

    for idx, (start, end) in enumerate(keep_segments):
        # 输出路径
        v_path = seg_dir / f"seg_{idx:03d}.mp4"
        a_path = seg_dir / f"seg_{idx:03d}.wav"

        # ffmpeg 同步剪切
        cmd_video = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-to", str(end),
            "-i", str(video),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-an",
            str(v_path)
        ]

        cmd_audio = [
            "ffmpeg",
            "-y",
            "-i", str(video),
            "-ss", str(start),
            "-to", str(end),
            "-vn",            # 不保留视频
            "-ac", "1",
            "-ar", "16000",
            str(a_path)
        ]

        subprocess.run(cmd_video, check=True)
        subprocess.run(cmd_audio, check=True)

        seg_files_video.append(v_path)
        seg_files_audio.append(a_path)

    # -------------------------------
    # 合并视频
    # -------------------------------
    output_video = CUT_VIDEO
    concat_segments(seg_files_video, output_video)

    # -------------------------------
    # 合并音频
    # -------------------------------
    output_audio = CUT_AUDIO
    concat_segments(seg_files_audio, output_audio, is_audio=True)

    print("✅ 剪辑完成:")
    print("   视频:", output_video)
    print("   音频:", output_audio)


if __name__ == "__main__":
    run()
