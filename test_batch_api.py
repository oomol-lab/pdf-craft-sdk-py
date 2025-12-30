"""
简单的批处理 API 测试脚本
"""
import requests
import json

API_KEY = "your_api_key_here"
BASE_URL = "https://pdf-server.oomol.com/api/v1/conversion"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 测试创建批次
print("测试 API 端点:", BASE_URL)
print("测试创建批次...")

files = [
    {
        "url": "https://arxiv.org/pdf/1706.03762.pdf",
        "fileName": "test.pdf"
    }
]

data = {
    "files": files,
    "outputFormat": "markdown",
    "includesFootnotes": False
}

endpoint = f"{BASE_URL}/batches"
print(f"\n请求 URL: {endpoint}")
print(f"请求数据: {json.dumps(data, indent=2)}")

response = requests.post(endpoint, json=data, headers=headers)

print(f"\n响应状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}")
print(f"响应内容: {response.text}")

if response.ok:
    try:
        result = response.json()
        print(f"\n解析后的 JSON: {json.dumps(result, indent=2)}")
    except:
        print("\n无法解析为 JSON")
else:
    print(f"\n❌ 请求失败: HTTP {response.status_code}")
