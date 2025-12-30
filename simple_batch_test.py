"""
简单的批处理测试示例 - 使用 cache:// URL
"""
import os
from pdf_craft_sdk import PDFCraftClient, BatchFile, FormatType

# 使用提供的 API Key
API_KEY = "your_api_key_here"

# 初始化客户端
client = PDFCraftClient(api_key=API_KEY)

print("=== 批处理功能测试 ===\n")

# 使用 cache:// 格式的 URL (你需要先上传文件获取缓存 URL)
# 这里使用的是示例,你需要替换成实际的缓存 URL
files = [
    {"url": "cache://example.pdf", "fileName": "test_document.pdf"}
]

print("注意: 请先上传文件到系统获取 cache:// URL,然后替换上面的示例 URL")
print("\n创建批次...")

try:
    # 创建批次
    batch = client.create_batch(
        files=files,
        output_format=FormatType.MARKDOWN,
        includes_footnotes=False
    )

    print(f"✅ 批次创建成功!")
    print(f"   批次 ID: {batch.batch_id}")
    print(f"   总文件数: {batch.total_files}")
    print(f"   状态: {batch.status}")

    batch_id = batch.batch_id

    # 启动批次
    print(f"\n启动批次...")
    result = client.start_batch(batch_id)
    print(f"✅ 批次已启动,排队任务数: {result.queued_jobs}")

    # 查询状态
    print(f"\n查询批次状态...")
    batch_detail = client.get_batch(batch_id)
    print(f"   状态: {batch_detail.status}")
    print(f"   进度: {batch_detail.progress}%")

    # 获取并发状态
    print(f"\n查询并发状态...")
    status = client.get_concurrent_status()
    print(f"   最大并发数: {status.max_concurrent_jobs}")
    print(f"   当前运行任务数: {status.current_running_jobs}")
    print(f"   可用槽位: {status.available_slots}")
    print(f"   可以提交新任务: {'是' if status.can_submit_new_job else '否'}")

    print("\n✅ 所有测试完成!")

except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
