from faster_whisper import WhisperModel

# 在 Apple M 系列上启用 Metal + FP16
model = WhisperModel("small", device="metal", compute_type="float16")

# 可选：静音过滤提速；中文内容建议温度为 0，提升一致性
segments, _ = model.transcribe(
    "money.wav",
    beam_size=1,           # 贪心，最快
    vad_filter=True,       # 跳过静音
    temperature=0.0
)

with open("money_china_simple.txt","w",encoding="utf-8") as f:
    for s in segments:
        f.write(s.text + "\n")