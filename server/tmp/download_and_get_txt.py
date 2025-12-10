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
    url_and_file_name_list = [
        {
            "url": "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/miv5wazs0qn8/drm/main.m3u8?sign=253f621575bf62c44711f09a979a5b5f&t=69382bf5&us=mpQkUjhvxO",
            "file_name": "日本有没有失去30年（一）20251206",
        },
        {
            "url": "https://material-ali.vod.xiaoe-materials.com/909a41edd31c71f080064531959d0102/c22e8321d239d06faf0a7ee3eaed3fb6-sd-encrypt-stream.m3u8?sign=e32c03baa3a622d2148c51938baf42b8&t=69382c6e&us=meirhAGaVw",
            "file_name": "日本有没有失去30年（二）20251206",
        },
        {
            "url": "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/miv61rgr0tav/drm/main.m3u8?sign=8ccadec21485343807fe282624767070&t=69382c8c&us=yYBqQEYSCW",
            "file_name": "日本有没有失去30年（三）20251206",
        },{
            "url": "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/miv651co0cjs/drm/main.m3u8?sign=79aac4a85bf41728051e730c950d7f9e&t=69382ca7&us=mhpYZjPiJl",
            "file_name": "日本有没有失去30年（四）20251206",
        }
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

