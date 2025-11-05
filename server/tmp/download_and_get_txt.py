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
    这是我的语音转文字内容。请帮我整理格式，但内容不要做任何修改。

    要求：
    1. 保持原文内容，只调整格式和段落，通过上下文理解，有错误的词语需要纠正。
    2. 可以合并成一行的短句合并成一行，可以组成一段的内容合并成一段
    3. [根据需要添加：帮我加上合适的标点符号]
    4. [根据需要添加：如果是繁体中文，帮我转换成简体中文]
    5. 保持原文的口语风格和表达特点，尽量不调整语义，错别字或者词语可以调整。

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
            "url": "https://encrypt-k-vod.xet.tech/9764a7a5vodtransgzp1252524126/5a1ababb5145403701727771063/drm/v.f421220.m3u8?sign=fbc0eb52b2cec9bc6fe78966b091fcb1&t=690b5d2a&us=GgLJIZaiNQ",
            "file_name": "黄金的新高，黄毛的烦恼-1",
        },
        {
            "url": "https://encrypt-k-vod.xet.tech/9764a7a5vodtransgzp1252524126/a9469ce15145403701728852815/drm/v.f421220.m3u8?sign=816375ef491ad7ed3338fa1345815e62&t=690b5d6c&us=VEdwWKGCrg",
            "file_name": "黄金的新高，黄毛的烦恼-2",
        },
        {
            "url": "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/mgn5m1nu0io8/drm/main.m3u8?sign=4e545e1221329b721a8ba0b0b23ec90c&t=690b5d88&us=qEgPAwRWaN",
            "file_name": "黄金的新高，黄毛的烦恼-3",
        },
        {
            "url": "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/mgn5oj240ut0/drm/main.m3u8?sign=4fa7de1b81e5c259cb52bbecc9b994d6&t=690b5db5&us=gsAQgLmlUG",
            "file_name": "黄金的新高，黄毛的烦恼-4",
        },
        {
            "url": "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/mgd64sds07aq/drm/main.m3u8?sign=c5266d5356e480a8b8c6415e86d6d685&t=690b5dd0&us=SetFuMJrjR",
            "file_name": "消费的逻辑-1",
        },
        {
            "url": "https://material-ali.vod.xiaoe-materials.com/70df0a4fa19f71f0814a6733a78e0102/05271c23725c592f52a3eace5de62793-sd-encrypt-stream.m3u8?sign=422c27874ffd7f56cf3b717c1e1f23e3&t=690b5deb&us=LXyloMXEzG",
            "file_name": "消费的逻辑-2",
        },
        {
            "url": "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/mgd69tt8081e/drm/main.m3u8?sign=4a80367f95040615ef9786677609f1ef&t=690b5e0a&us=qUmbjylejA",
            "file_name": "消费的逻辑-3",
        },
        {
            "url": "https://encrypt-k-vod.xet.tech/9764a7a5vodtransgzp1252524126/39b054305145403701000876701/drm/v.f421220.m3u8?sign=c63def71643c20078fcb8be61450e314&t=690b5e24&us=qXHNyuEhRQ",
            "file_name": "消费的逻辑-4",
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

