from tmp.download_and_get_txt import process_text

# 读取readme.md, 得到source_text
file_name_pre = "what_is_asset3"
source_text = open(f"{file_name_pre}.txt", "r", encoding="utf-8").read()

result = process_text(source_text, "qwen-plus-2025-07-28")
