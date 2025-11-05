from openai import OpenAI
import os
from typing import List, Dict, Optional, Generator, Union


def chat_with_model(
        messages: List[Dict[str, str]],
        model_name: str = "qwen3-235b-a22b-thinking-2507",
        api_key: Optional[str] = None,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        stream: bool = True
) -> Generator[Union[tuple, str], None, None]:
    """
    与支持思考过程的模型进行对话，区分显示思考过程和最终回复

    参数:
        messages: 消息列表，格式为[{"role": "user", "content": "消息内容"}]
        model_name: 模型名称
        api_key: API密钥，如果为None则从环境变量DASHSCOPE_API_KEY获取
        base_url: API基础URL
        stream: 是否使用流式响应

    返回:
        生成器，逐步返回思考过程和最终回复
    """
    # 初始化客户端
    client = OpenAI(
        api_key=api_key or os.getenv("DASHSCOPE_API_KEY"),
        base_url=base_url.strip()
    )

    # 根据模型名称决定是否需要额外参数
    extra_body = {}
    if model_name.startswith("qwen-plus") or model_name.startswith("qwen-max"):
        extra_body = {"enable_thinking": True}

    # 创建流式请求
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=stream,
        **({"extra_body": extra_body} if extra_body else {})
    )

    is_answering = False  # 是否进入正式回复阶段

    # 处理流式响应
    for chunk in completion:
        delta = chunk.choices[0].delta

        # 处理思考内容
        if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
            if not is_answering:
                yield ("thinking", delta.reasoning_content)

        # 处理正式回复内容
        if hasattr(delta, "content") and delta.content:
            if not is_answering:
                yield ("answer_start", None)
                is_answering = True
            yield ("answer", delta.content)


def run_chat_demo(
        prompt: str,
        model_name: str = "qwen3-235b-a22b-thinking-2507"
):
    """
    运行聊天演示，直观展示思考过程和最终回复

    参数:
        prompt: 用户输入的提示
        model_name: 要使用的模型名称
    """
    messages = [{"role": "user", "content": prompt}]

    print(f"\n{'=' * 20} 与模型对话演示 (模型: {model_name}) {'=' * 20}")
    print(f"用户: {prompt}\n")

    thinking_lines = []
    full_answer = []

    for event_type, content in chat_with_model(messages, model_name=model_name):
        if event_type == "thinking":
            thinking_lines.append(content)
            print(content, end="", flush=True)
        elif event_type == "answer_start":
            print("\n" + "=" * 20 + " 最终回复 " + "=" * 20)
        elif event_type == "answer":
            full_answer.append(content)
            print(content, end="", flush=True)

    print("\n" + "=" * 50)
    print(f"\n思考过程总结: {''.join(thinking_lines)}")
    print(f"最终回复: {''.join(full_answer)}")
    print("=" * 50 + "\n")

    return ''.join(full_answer)


# 使用示例
if __name__ == "__main__":
    # 示例1: 使用默认模型（支持思考过程的模型）
    run_chat_demo("请解释量子计算的基本原理", "qwen3-235b-a22b-thinking-2507")

    # 示例2: 使用需要额外参数的模型
    run_chat_demo("请解释相对论的基本原理", "qwen-plus-2025-07-28")

    # 示例3: 使用另一个需要额外参数的模型
    run_chat_demo("如何制作一杯好喝的咖啡?", "qwen-max")

    # 示例4: 自定义处理
    """
    messages = [{"role": "user", "content": "1+1等于几？"}]
    for event_type, content in chat_with_model(messages, model_name="qwen-plus-2025-07-28"):
        if event_type == "thinking":
            print(f"[思考] {content}", end="", flush=True)
        elif event_type == "answer_start":
            print("\n[开始回复]")
        elif event_type == "answer":
            print(f"[回复] {content}", end="", flush=True)
    """