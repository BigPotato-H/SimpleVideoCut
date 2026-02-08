def main():
    print("🚀 Step 0: extract audio")
    import _0extract_audio
    _0extract_audio.run()

    print("🟡 Step 1: detect pauses")
    import _1detect_pause
    _1detect_pause.run()

    print("🟡 Step 2: detect clap")
    import _2detect_clap
    _2detect_clap.run()

    print("✂️ Step 3: cut video")
    import _3cut_video
    _3cut_video.run()

    print("🧠 Step 4: transcribe (Whisper)")
    import _4transcribe
    _4transcribe.run()

    print("📝 Step 5: json → srt")
    import _5json_to_srt
    _5json_to_srt.run()

    print("✅ All done!")


if __name__ == "__main__":
    main()
