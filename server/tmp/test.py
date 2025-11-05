from tmp.download_and_get_txt import process_text

# 打开 tmp.txt ,得到 内容： source_text
file_name_pre = "黄金的新高，黄毛的烦恼-4"
source_text = open(f"{file_name_pre}.txt", "r", encoding="utf-8").read()
result = process_text(source_text)
# result to file
with open(f"{file_name_pre}_final.txt", "w", encoding="utf-8") as f:
    f.write(result)