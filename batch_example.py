"""
批处理功能使用示例

此示例演示如何使用 PDFCraftClient 进行批量 PDF 转换
"""
import os
import time
from pdf_craft_sdk import PDFCraftClient, BatchFile, FormatType

# 从环境变量获取 API Key
API_KEY = os.getenv("PDF_CRAFT_API_KEY", "your_api_key_here")

# 示例 PDF URL 列表
EXAMPLE_PDFS = [
    {"url": "https://arxiv.org/pdf/1706.03762.pdf", "fileName": "attention_is_all_you_need.pdf"},
    {"url": "https://arxiv.org/pdf/2103.14030.pdf", "fileName": "gpt3_paper.pdf"},
]

def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        print("请先设置 API Key。可以设置环境变量 PDF_CRAFT_API_KEY 或直接修改脚本中的 API_KEY 变量。")
        return

    # 初始化客户端
    client = PDFCraftClient(api_key=API_KEY)

    print("=== 批处理功能演示 ===\n")

    # 示例 1: 创建批次
    print("--- 示例 1: 创建批次 ---")
    try:
        # 准备文件列表
        files = [
            BatchFile(url=pdf["url"], file_name=pdf["fileName"])
            for pdf in EXAMPLE_PDFS
        ]

        # 或者使用字典格式
        # files = [
        #     {"url": pdf["url"], "fileName": pdf["fileName"]}
        #     for pdf in EXAMPLE_PDFS
        # ]

        print(f"创建包含 {len(files)} 个文件的批次...")
        batch = client.create_batch(
            files=files,
            output_format=FormatType.MARKDOWN,
            includes_footnotes=False
        )

        print(f"✅ 批次创建成功!")
        print(f"   批次 ID: {batch.batch_id}")
        print(f"   总文件数: {batch.total_files}")
        print(f"   状态: {batch.status}")
        print(f"   输出格式: {batch.output_format}")

        batch_id = batch.batch_id

    except Exception as e:
        print(f"❌ 创建批次失败: {e}")
        return

    # 示例 2: 启动批次
    print("\n--- 示例 2: 启动批次 ---")
    try:
        print(f"启动批次 {batch_id}...")
        result = client.start_batch(batch_id)
        print(f"✅ 批次启动成功!")
        print(f"   排队任务数: {result.queued_jobs}")
    except Exception as e:
        print(f"❌ 启动批次失败: {e}")
        return

    # 示例 3: 查询批次状态
    print("\n--- 示例 3: 查询批次状态 ---")
    try:
        batch_detail = client.get_batch(batch_id)
        print(f"✅ 批次状态:")
        print(f"   状态: {batch_detail.status}")
        print(f"   进度: {batch_detail.progress}%")
        print(f"   已完成: {batch_detail.completed_files}/{batch_detail.total_files}")
        print(f"   失败: {batch_detail.failed_files}")
    except Exception as e:
        print(f"❌ 查询批次状态失败: {e}")

    # 示例 4: 轮询等待批次完成
    print("\n--- 示例 4: 等待批次完成 ---")
    print("轮询批次状态...")
    max_wait_time = 600  # 最多等待 10 分钟
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        try:
            batch_detail = client.get_batch(batch_id)
            print(f"   进度: {batch_detail.progress}% | 状态: {batch_detail.status} | "
                  f"已完成: {batch_detail.completed_files}/{batch_detail.total_files}")

            # 检查是否完成
            if batch_detail.status in ["completed", "failed", "cancelled"]:
                if batch_detail.status == "completed":
                    print(f"\n✅ 批次处理完成!")
                else:
                    print(f"\n⚠️  批次状态: {batch_detail.status}")
                break

            # 等待 5 秒后再次查询
            time.sleep(5)

        except Exception as e:
            print(f"❌ 查询批次状态失败: {e}")
            break
    else:
        print(f"\n⏱️  等待超时")

    # 示例 5: 获取批次任务列表
    print("\n--- 示例 5: 获取任务列表 ---")
    try:
        jobs_result = client.get_batch_jobs(batch_id, page=1, page_size=20)
        print(f"✅ 任务列表:")
        print(f"   总任务数: {jobs_result.pagination.total}")

        for i, job in enumerate(jobs_result.jobs, 1):
            print(f"\n   任务 {i}:")
            print(f"      文件名: {job.file_name}")
            print(f"      状态: {job.status}")
            print(f"      进度: {job.progress}%")
            if job.status == "completed" and job.result_url:
                print(f"      下载链接: {job.result_url}")
            elif job.status == "failed" and job.error_message:
                print(f"      错误信息: {job.error_message}")

    except Exception as e:
        print(f"❌ 获取任务列表失败: {e}")

    # 示例 6: 获取所有批次列表
    print("\n--- 示例 6: 获取所有批次列表 ---")
    try:
        batches = client.get_batches(page=1, page_size=10, status="all")
        print(f"✅ 批次列表 (共 {batches.pagination.total} 个批次):")

        for i, batch in enumerate(batches.batches[:5], 1):  # 只显示前 5 个
            print(f"\n   批次 {i}:")
            print(f"      ID: {batch['id']}")
            print(f"      状态: {batch['status']}")
            print(f"      进度: {batch['progress']}%")
            print(f"      文件数: {batch['totalFiles']}")

    except Exception as e:
        print(f"❌ 获取批次列表失败: {e}")

    # 示例 7: 批次控制操作
    print("\n--- 示例 7: 批次控制操作 ---")

    # 暂停批次 (如果批次正在运行)
    # try:
    #     result = client.pause_batch(batch_id)
    #     print(f"✅ 批次已暂停, 暂停了 {result.paused_jobs} 个任务")
    # except Exception as e:
    #     print(f"⚠️  暂停批次失败: {e}")

    # 恢复批次
    # try:
    #     result = client.resume_batch(batch_id)
    #     print(f"✅ 批次已恢复, 恢复了 {result.resumed_jobs} 个任务")
    # except Exception as e:
    #     print(f"⚠️  恢复批次失败: {e}")

    # 重试失败的任务
    # try:
    #     result = client.retry_failed_jobs(batch_id)
    #     print(f"✅ 已重试失败的任务, 重试了 {result.retried_jobs} 个任务")
    # except Exception as e:
    #     print(f"⚠️  重试失败任务失败: {e}")

    # 取消批次
    # try:
    #     result = client.cancel_batch(batch_id)
    #     print(f"✅ 批次已取消, 取消了 {result.cancelled_jobs} 个任务")
    # except Exception as e:
    #     print(f"⚠️  取消批次失败: {e}")

    print("批次控制操作示例已注释，如需使用请取消注释")

    # 示例 8: 获取并发状态
    print("\n--- 示例 8: 获取并发状态 ---")
    try:
        status = client.get_concurrent_status()
        print(f"✅ 并发状态:")
        print(f"   最大并发数: {status.max_concurrent_jobs}")
        print(f"   当前运行任务数: {status.current_running_jobs}")
        print(f"   可以提交新任务: {'是' if status.can_submit_new_job else '否'}")
    except Exception as e:
        print(f"❌ 获取并发状态失败: {e}")

    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    main()
