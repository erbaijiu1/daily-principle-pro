import subprocess

from faster_whisper import WhisperModel
import subprocess
import os

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


def get_txt_from_mp3(file_name_pre, dir_name=""):
    """直接从 MP3 提取文字并保存为 TXT"""
    src_file = os.path.join(dir_name, f"{file_name_pre}.mp3")
    print(f"正在处理音频文件: {src_file}...")

    # 初始化模型（建议将模型初始化放在函数外部以提高多次调用的效率）
    model = WhisperModel("small", device="cpu", compute_type="int8")

    # 直接识别 MP3 文件
    segments, _ = model.transcribe(src_file, beam_size=1, vad_filter=True, temperature=0.0)

    # 提取文本
    full_text = "\n".join([s.text for s in segments])

    # 写入文件
    output_file = f"{file_name_pre}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"✅ 转换完成，结果已保存至: {output_file}")
    return full_text


# 如果你希望在转换前统一音频格式（比如 MP3 转 WAV）以获得更稳定的效果，可以这样做：
def get_txt_from_mp3_with_convert(file_name_pre, dir_name=""):
    """先转为 16kHz WAV 再识别，适合对音质有要求的场景"""
    src_file = os.path.join(dir_name, f"{file_name_pre}.mp3")
    wav_file = f"{file_name_pre}_temp.wav"

    # 使用 FFmpeg 标准化音频
    subprocess.run([
        "ffmpeg", "-y", "-i", src_file,
        "-ar", "16000", "-ac", "1", wav_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(wav_file, beam_size=1)

    full_text = "\n".join([s.text for s in segments])

    with open(f"{file_name_pre}.txt", "w", encoding="utf-8") as f:
        f.write(full_text)

    # 清理临时文件
    if os.path.exists(wav_file):
        os.remove(wav_file)

    return full_text

if __name__ == "__main__":
    files_dir = "/Users/hc/Downloads/"
    get_txt_from_mp3("c585ad85c6909ec99cf2038b3b8f1d67", files_dir)
