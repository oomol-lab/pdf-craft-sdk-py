"""
测试其他批处理 API 端点的响应格式
"""
import os
import requests
import json

API_KEY = os.getenv("PDF_CRAFT_API_KEY", "your_api_key_here")
BASE_URL = "https://pdf-server.oomol.com/api/v1/conversion"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 先创建一个批次
print("1. 创建批次...")
files = [{"url": "https://arxiv.org/pdf/1706.03762.pdf", "fileName": "test.pdf"}]
data = {"files": files, "outputFormat": "markdown", "includesFootnotes": False}
response = requests.post(f"{BASE_URL}/batches", json=data, headers=headers)
batch_result = response.json()
print(f"创建批次响应: {json.dumps(batch_result, indent=2)}")

if batch_result.get("success"):
    batch_id = batch_result["data"]["batchId"]
    print(f"\n批次 ID: {batch_id}")

    # 测试启动批次
    print(f"\n2. 启动批次...")
    response = requests.post(f"{BASE_URL}/batches/{batch_id}/start", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2)}")

    # 测试获取批次详情
    print(f"\n3. 获取批次详情...")
    response = requests.get(f"{BASE_URL}/batches/{batch_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2)}")

    # 测试获取批次列表
    print(f"\n4. 获取批次列表...")
    response = requests.get(f"{BASE_URL}/batches?page=1&pageSize=5", headers=headers)
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应(部分): success={result.get('success')}, 包含字段: {list(result.keys())}")
    if "data" in result:
        print(f"data 字段: {list(result['data'].keys())}")

    # 测试获取并发状态
    print(f"\n5. 获取并发状态...")
    response = requests.get(f"{BASE_URL}/concurrent-status", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2)}")
