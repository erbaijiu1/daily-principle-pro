import os

from click import prompt

from tmp.down_load_m3u8 import download_video
from tmp.get_video_txt_cpu import mp4_to_txt
from tmp.model_deal import run_chat_demo


def process_text(need_deal_txt:  str, model_name: str = "qwen3-235b-a22b-thinking-2507"):
    if not need_deal_txt:
        print("没有待处理的文本")
        return

    prompt_txt = """
    这是我的语音转文字内容。请帮我整理格式，意思不要做修改。

    要求：
    1. 保持原文内容，只调整格式和段落，通过上下文理解，有错误的词语需要纠正。
    2. 可以合并成一行的短句合并成一行，可以组成一段的内容合并成一段
    3. [根据需要添加：帮我加上合适的标点符号]
    4. [根据需要添加：如果是繁体中文，帮我转换成简体中文]
    5. 保持原文的口语风格和表达特点，尽量不调整语义，错别字或者词语可以调整。
    6. 由于是语音转文字，所以，一些由语音转换来的词需要整体通过语境判断是不是对的，错误的纠正过来。

    内容如下：
    %need_deal_txt%
    """
    prompt_txt = prompt_txt.replace("%need_deal_txt%", need_deal_txt)

    return run_chat_demo(prompt_txt, model_name)

"""
{
    "url": "",
    "file_name": "",
}
"""
if __name__ == "__main__":
    files_dir = "/Users/hc/Downloads/"
    file_name_list = [
        # "main",
        # "main1",
        # "main2",
        "main3",
    ]
    for file_name in file_name_list:
        try:
            source_text = mp4_to_txt(file_name, files_dir)
            result = process_text(source_text)
            # result to file
            with open(f"{file_name}_final.txt", "w", encoding="utf-8") as f:
                f.write(result)

        except Exception as e:
            print(e)
