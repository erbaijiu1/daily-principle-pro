import os
import requests
from faster_whisper import WhisperModel
from openai import OpenAI  # 建议使用标准 OpenAI 库，兼容性最强

from tmp.model_deal import process_text_with_prompt

# --- 配置区 ---
# 如果你有自己的 API Key，填在这里；如果没有，可以配置本地 Ollama 或其他大模型
LLM_API_KEY = "your-api-key"
LLM_BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o"  # 或者 "deepseek-chat" 等

# 下载保存路径
DOWNLOAD_DIR = "./temp_audio"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class OnlineAudioTask:
    def __init__(self, url, alias):
        self.url = url
        self.alias = alias


def download_file(url, alias):
    """将在线 MP3 下载到本地"""
    local_path = os.path.join(DOWNLOAD_DIR, f"{alias}.mp3")
    print(f"正在从网络下载: {alias}...")

    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()  # 如果下载失败抛出异常

    with open(local_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ 下载完成: {local_path}")
    return local_path


def transcribe_audio(file_path):
    """提取文字 (参考你之前的逻辑)"""
    print(f"正在识别文字: {file_path}...")
    # 这里建议将模型实例化提到外部，避免循环内重复加载
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(file_path, beam_size=1, vad_filter=True)

    full_text = "\n".join([s.text for s in segments])
    return full_text


def call_llm(text):
    """调用大模型对文字进行精简或总结"""
    if not LLM_API_KEY or "your-api-key" in LLM_API_KEY:
        print("⚠️ 未配置 API Key，将跳过大模型处理环节。")
        return text

    print("正在通过大模型优化文本内容...")
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    prompt = f"以下是从语音识别出的原始文本，请帮我进行排版润色，修正错别字，并总结核心要点：\n\n{text}"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content


def process_online_list(tasks):
    """
    重构后的主逻辑：
    1. 第一阶段：全量下载（抢在链接失效前完成）
    2. 第二阶段：全量处理（识别 + 大模型加工）
    """

    # --- 第一阶段：全部下载 ---
    print(f"🚀 开始第一阶段：批量下载 (共 {len(tasks)} 个任务)...")
    for task in tasks:
        try:
            local_file = download_file(task['url'], task['alias'])
            # 将本地路径存入 task 字典中，方便下一阶段使用
            task['local_path'] = local_file
        except Exception as e:
            print(f"❌ 下载 {task['alias']} 失败: {str(e)}")
            task['local_path'] = None  # 标记为下载失败

    print("\n" + "=" * 30 + "\n")

    # --- 第二阶段：识别与处理 ---
    print("🚀 开始第二阶段：识别与大模型处理...")
    for task in tasks:
        # 跳过第一阶段下载失败的任务
        if not task.get('local_path'):
            print(f"⏩ 跳过任务 {task['alias']} (无本地文件)")
            continue

        local_file = task['local_path']
        try:
            # 2. 转文字
            raw_text = transcribe_audio(local_file)

            # 3. 大模型处理 (调用你自定义的 process_text_with_prompt)
            final_content = process_text_with_prompt(raw_text)

            # 4. 写入本地
            output_file = f"{task['alias']}_final.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_content)

            print(f"✨ 任务成功完成: {output_file}")

            # 5. 清理临时 MP3 文件
            if os.path.exists(local_file):
                os.remove(local_file)

        except Exception as e:
            print(f"❌ 任务 {task['alias']} 处理过程中出错: {str(e)}")


if __name__ == "__main__":
    host_list = [
        "https://wechatapppro-1252524126.file.myqcloud.com/appfvn6my9u7697/audio_compressed/1775926001_hbawo3mnukcqoj.mp3",
        "https://wechatapppro-1252524126.file.myqcloud.com/appfvn6my9u7697/audio_compressed/1775926070_xnmnlrmnukhr3n.mp3",
        "https://wechatapppro-1252524126.file.myqcloud.com/appfvn6my9u7697/audio_compressed/1775926143_0e396amnukja5b.mp3",
        "https://wechatapppro-1252524126.file.myqcloud.com/appfvn6my9u7697/audio_compressed/1775926221_l4kfx1mnukkxqe.mp3",
    ]
    name_pre = "石油危机对经济投资的影响"
    my_tasks = []
    for i, host in enumerate(host_list):
        item = {
                "url": host,
                "alias": f"{name_pre}_{i+1}"
            }
        my_tasks.append(item)

    process_online_list(my_tasks)
