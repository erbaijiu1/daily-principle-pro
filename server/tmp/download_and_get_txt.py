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
    6. 由于是语音转文字，所以，一些词需要整体通过语境判断是不是对的，错误的纠正过来。

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
    url_and_file_name_list = [
        {
            "url": "https://encrypt-k-vod.xet.tech/9764a7a5vodtransgzp1252524126/117df24a5145403705784969404/drm/v.f421220.m3u8?sign=63c5da9ec2da5c533d96e3a71a7077c5&t=691b21b5&us=eJffkoWzFr",
            "file_name": "铸大钱的故事 （一）2025-11-15",
        },
        {
            "url": "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/mi16oaf905up/drm/main.m3u8?sign=a7815fcf8f6a84a0443a7729dee35ffa&t=691b2218&us=DZkUNAggum",
            "file_name": "铸大钱的故事 （二）2025-11-15",
        },
        {
            "url": "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/mi16ru7t0hn9/drm/main.m3u8?sign=db9961b8dc453f6dc9a22410d799efb6&t=691b223a&us=RaEQBRaNlj",
            "file_name": "铸大钱的故事 （三）2025-11-15",
        },
    ]
    for item in url_and_file_name_list:
        try:
            download_video(item["url"], item["file_name"])
            source_text = mp4_to_txt(item["file_name"])
            result = process_text(source_text)
            # result to file
            with open(f"{item['file_name']}_final.txt", "w", encoding="utf-8") as f:
                f.write(result)
        except Exception as e:
            print(e)

