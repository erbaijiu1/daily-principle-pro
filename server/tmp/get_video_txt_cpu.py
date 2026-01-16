import subprocess

from faster_whisper import WhisperModel

def mp4_to_txt(file_name_pre, dir_name = ""):
    # 3. 执行 ffmpeg 转换命令
    print("开始转换视频为音频...")
    src_file = f"{dir_name}{file_name_pre}.mp4" if dir_name else file_name_pre
    subprocess.run(
        [
            "ffmpeg",
            "-y",  # 覆盖现有文件
            "-i", f"{src_file}",
            "-ar", "16000",  # 16kHz 采样率
            "-ac", "1",      # 单声道
            "-vn",           # 禁用视频流
            f"{file_name_pre}.wav"
        ],
        check=True,  # 遇到错误立即抛出异常
        stdout=subprocess.DEVNULL,  # 隐藏ffmpeg输出
        stderr=subprocess.DEVNULL
    )
    print(f"✅ 音频转换完成: {file_name_pre}.wav")

    model = WhisperModel("small", device="cpu", compute_type="int8")  # 或 "int8_float16"
    segments, _ = model.transcribe(f"{file_name_pre}.wav", beam_size=1, vad_filter=True, temperature=0.0)

    # 先得到完整的文本
    full_text = "\n".join([s.text for s in segments])

    # 再写到文件
    with open(f"{file_name_pre}.txt","w",encoding="utf-8") as f:
        f.write(full_text)

    return full_text

if __name__ == "__main__":
    mp4_to_txt("8-10")
