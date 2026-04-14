#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成标签系统下载人群包的 CURL 脚本。
可以在本地测试或者线上环境中直接运行。
需要预先安装依赖： pip install requests pycryptodome
"""

import requests
import base64
import json
import argparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# ================= 默认配置区域 (从 bootstrap.properties 读取或手动设置) =================
# PUBLIC_KEY_URL = "http://sso-test.ciccwm.com"
# label_url_host = "http://label-management-test.ciccwm.com"
#
# DEFAULT_LOGIN_NAME = "superadmin"
# DEFAULT_LOGIN_PASSWORD = "cIcc2024@ciccwm"
# DEFAULT_TARGET_ENTITY_ID = "40"
# DEFAULT_PACKAGE_ID = "1103" # ai_line_send_id (ai_line_can_send_id)

# product
PUBLIC_KEY_URL = "http://ma-sso.ciccwm.com"
label_url_host = "http://indicator-management.ciccwm.com"

DEFAULT_LOGIN_NAME = "admin3_awm"
DEFAULT_LOGIN_PASSWORD = "admin3_awm33"
DEFAULT_TARGET_ENTITY_ID = "40"
DEFAULT_PACKAGE_ID = "10313" # ai_line_send_id (ai_line_can_send_id)
# ======================================================================================

def get_public_key(server_url):
    print("[1/4] 获取鉴权公钥...")
    url = f"{server_url}/api/sso/ssoFacade/getPublicKey"
    # 强制不使用代理
    resp = requests.get(url, proxies={"http": None, "https": None})
    print(resp.status_code)

    resp.raise_for_status()
    data = resp.json()

    # 根据后端 PublicKeyRspDto 解析 PublicKey
    pub_key = ""
    if "data" in data and isinstance(data["data"], dict) and "publicKey" in data["data"]:
        pub_key = data["data"]["publicKey"]
    elif "publicKey" in data:
        pub_key = data["publicKey"]
    else:
        print("未识别的公钥返回格式，请检查网络或后端结构：", data)
        exit(1)

    print(f"      获取成功! 公钥前缀: {pub_key[:20]}...")
    return pub_key

def encrypt_password(password, pub_key_str):
    print("[2/4] 使用 RSA 算法加密密码...")
    # 补齐标准 PEM 格式头尾
    if "BEGIN PUBLIC KEY" not in pub_key_str:
        pub_key_str = f"-----BEGIN PUBLIC KEY-----\n{pub_key_str}\n-----END PUBLIC KEY-----"

    rsakey = RSA.importKey(pub_key_str)
    cipher = PKCS1_v1_5.new(rsakey)
    encrypted = cipher.encrypt(password.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')

def login(session, base_url, username, encrypted_password):
    print("[3/4] 执行标签系统登录...")
    url = f"{base_url}/api/sso/ssoFacade/login"
    payload = {
        "userAccount": username,
        "userPassword": encrypted_password
    }
    resp = session.post(url, json=payload, proxies={"http": None, "https": None})
    resp.raise_for_status()
    data = resp.json()

    cookie_str = ""

    # 优先从响应头的 Set-Cookie 中提取 access-token
    set_cookie_headers = []
    if hasattr(resp, 'raw') and hasattr(resp.raw, 'headers') and hasattr(resp.raw.headers, 'getlist'):
        set_cookie_headers = resp.raw.headers.getlist('Set-Cookie')
    elif 'Set-Cookie' in resp.headers:
        set_cookie_headers = resp.headers['Set-Cookie'].split(', ')

    if set_cookie_headers:
        for set_cookie_header in set_cookie_headers:
            cookies = set_cookie_header.split(";")
            for cookie in cookies:
                name_value = cookie.split("=", 1)
                if len(name_value) == 2 and name_value[0].strip() == "access-token" and name_value[1].strip():
                    cookie_str = cookie.strip()
                    break
            if cookie_str:
                break

    # 如果从 header 没找到，再尝试从 body 提取（兼容旧逻辑）
    if not cookie_str:
        if "data" in data and isinstance(data["data"], dict) and "cookie" in data["data"]:
            cookie_str = data["data"]["cookie"]
        elif "cookie" in data:
            cookie_str = data["cookie"]

    # 最后兜底：从 session cookies 中提取
    if not cookie_str:
        cookies_dict = session.cookies.get_dict()
        if cookies_dict:
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])

    if not cookie_str:
        print("      登录失败或未能找到有效的 Cookie。")
        print("      后端返回体:", data)
        print("      响应头 Set-Cookie:", resp.headers.get('Set-Cookie'))
        exit(1)

    print("      登录成功! 获得有效 Cookie凭证。")
    return cookie_str

def generate_curl(base_url, origin, cookie_str, package_id, target_entity_id):
    print("[4/4] 正在生成人群包下载命令...")

    url = f"{base_url}/api/labelx/open/pack/{package_id}/download?targetEntityId={target_entity_id}"

    curl_cmd = (
        f"curl -X GET '{url}' \\\n"
        f"  -H 'Cookie: {cookie_str}' \\\n"
        f"  -H 'Origin: {origin}' \\\n"
        f"  -o 'package_{package_id}_users.csv'"
    )

    print("\n=========================================================================")
    print(" ✅ 验证成功! 您可以直接复制以下 CURL 命令在终端执行，下载人群包数据:")
    print("=========================================================================\n")
    print(curl_cmd)
    print("\n=========================================================================\n")
    print(f"💡 提示：人群包将会被保存为当前目录下的 package_{package_id}_users.csv 文件。")

def main():
    session = requests.Session()
    try:
        pub_key = get_public_key(PUBLIC_KEY_URL)
        enc_pw = encrypt_password(DEFAULT_LOGIN_PASSWORD, pub_key)
        cookie = login(session, PUBLIC_KEY_URL, DEFAULT_LOGIN_NAME, enc_pw)
        generate_curl(label_url_host,  label_url_host, cookie, DEFAULT_PACKAGE_ID, DEFAULT_TARGET_ENTITY_ID)
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ 网络请求失败: {e}")
        if e.response is not None:
             print("响应内容:", e.response.text)
    except Exception as e:
        print(f"\n❌ 脚本执行发生未知异常: {e}")

if __name__ == "__main__":
    main()
