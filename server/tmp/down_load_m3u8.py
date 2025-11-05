import subprocess
import os
import sys


def download_video(url, output_name="video", output_dir="."):
    """
    使用yt-dlp下载视频，支持自定义输出名称

    参数:
    url (str): 视频m3u8链接
    output_name (str): 自定义输出文件名前缀（不包含扩展名）
    output_dir (str): 输出目录路径
    """
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    # 构建输出模板 - 保持原格式但替换title为自定义名称
    output_template = os.path.join(
        output_dir,
        f"{output_name}.%(ext)s"
    )

    # 构建命令
    command = [
        'yt-dlp',
        '-ci',  # 继续下载和忽略错误
        '-o', output_template,
        url
    ]

    try:
        print(f"开始下载: {url}")
        print(f"输出路径: {output_template}")

        # 执行命令并捕获输出
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print("✅ 下载成功!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 下载失败: {e}")
        print(f"错误详情: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ 错误: 未找到yt-dlp。请安装yt-dlp:")
        print("pip install yt-dlp")
        print("或: brew install yt-dlp (macOS)")
        print("或: sudo apt install yt-dlp (Linux)")
        return False
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        return False


# 示例用法
if __name__ == "__main__":
    url = "https://v-vod-k.xiaoeknow.com/a8307e36f7a64aeeae086cc157bb356b/appfvn6my9u7697/video/b_u_d07g5c5st3c629qdmda0/mdyufp7f063y/drm/main.m3u8?sign=87f5c7b6ff237949c57a76c97b84ac8f&t=68f0ffa9&us=KZksVanZRy"
    output_name = "8-10"
    output_dir = "."

    # 执行下载
    success = download_video(url, output_name, output_dir)

    # 返回退出码
    sys.exit(0 if success else 1)