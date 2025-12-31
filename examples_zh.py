#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Craft SDK - 使用示例
演示所有主要功能的完整示例

从这里获取你的 API 密钥: https://console.oomol.com/api-key
"""

from pdf_craft_sdk import PDFCraftClient, FormatType, UploadProgress, PollingStrategy
from pdf_craft_sdk.exceptions import APIError

# 请将下方替换为你从 https://console.oomol.com/api-key 获取的 API 密钥
API_KEY = "your_api_key_here"


def example_1_basic_conversion():
    """示例 1: 基础本地 PDF 转换"""
    print("\n" + "="*60)
    print("示例 1: 基础本地 PDF 转换")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # 简单的一行转换
    download_url = client.convert_local_pdf("document.pdf")
    print(f"✅ 转换成功! 下载链接: {download_url}")


def example_2_with_progress():
    """示例 2: 带进度追踪的上传"""
    print("\n" + "="*60)
    print("示例 2: 带进度追踪的上传")
    print("="*60)

    def on_progress(progress: UploadProgress):
        print(f"📤 上传进度: {progress.percentage:.2f}% "
              f"({progress.current_part}/{progress.total_parts} 分片)")

    client = PDFCraftClient(api_key=API_KEY)

    download_url = client.convert_local_pdf(
        "large_document.pdf",
        progress_callback=on_progress
    )
    print(f"✅ 下载链接: {download_url}")


def example_3_epub_conversion():
    """示例 3: 转换为 EPUB 格式"""
    print("\n" + "="*60)
    print("示例 3: 转换为 EPUB 格式")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    download_url = client.convert_local_pdf(
        "document.pdf",
        format_type=FormatType.EPUB,
        includes_footnotes=True
    )
    print(f"✅ EPUB 文件已就绪: {download_url}")


def example_4_manual_steps():
    """示例 4: 手动上传和转换 (分步操作)"""
    print("\n" + "="*60)
    print("示例 4: 手动上传和转换")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # 步骤 1: 上传文件
    print("步骤 1: 正在上传文件...")
    cache_url = client.upload_file("document.pdf")
    print(f"✅ 已上传到: {cache_url}")

    # 步骤 2: 提交转换任务
    print("\n步骤 2: 正在提交转换任务...")
    task_id = client.submit_conversion(cache_url, format_type=FormatType.MARKDOWN)
    print(f"✅ 任务 ID: {task_id}")

    # 步骤 3: 等待完成
    print("\n步骤 3: 正在等待完成...")
    download_url = client.wait_for_completion(task_id)
    print(f"✅ 下载链接: {download_url}")


def example_5_remote_pdf():
    """示例 5: 转换远程 PDF (HTTPS URL)"""
    print("\n" + "="*60)
    print("示例 5: 转换远程 PDF")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # 如果你已经有来自上传 API 的 HTTPS URL
    pdf_url = "https://oomol-file-cache.example.com/your-file.pdf"

    download_url = client.convert(pdf_url, format_type=FormatType.MARKDOWN)
    print(f"✅ 下载链接: {download_url}")


def example_6_custom_polling():
    """示例 6: 自定义轮询策略"""
    print("\n" + "="*60)
    print("示例 6: 自定义轮询策略")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # 每 3 秒稳定轮询
    download_url = client.convert_local_pdf(
        "document.pdf",
        check_interval_ms=3000,
        max_check_interval_ms=3000,
        backoff_factor=PollingStrategy.FIXED
    )
    print(f"✅ 下载链接: {download_url}")

    # 对于长时间运行的任务
    download_url = client.convert_local_pdf(
        "large_document.pdf",
        check_interval_ms=5000,
        max_check_interval_ms=60000,  # 1 分钟
        backoff_factor=PollingStrategy.AGGRESSIVE
    )
    print(f"✅ 下载链接: {download_url}")


def example_7_error_handling():
    """示例 7: 正确的错误处理"""
    print("\n" + "="*60)
    print("示例 7: 错误处理")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    try:
        download_url = client.convert_local_pdf("document.pdf")
        print(f"✅ 成功: {download_url}")
    except FileNotFoundError:
        print("❌ 文件未找到!")
    except APIError as e:
        print(f"❌ API 错误: {e}")
    except TimeoutError:
        print("❌ 转换超时")
    except Exception as e:
        print(f"❌ 意外错误: {e}")


def example_8_batch_processing():
    """示例 8: 批量处理多个文件"""
    print("\n" + "="*60)
    print("示例 8: 批量处理")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

    # 提交所有任务而不等待
    task_ids = []
    for pdf_file in pdf_files:
        try:
            print(f"📄 正在处理 {pdf_file}...")
            task_id = client.convert_local_pdf(pdf_file, wait=False)
            task_ids.append((pdf_file, task_id))
            print(f"✅ 任务已提交: {task_id}")
        except Exception as e:
            print(f"❌ 处理 {pdf_file} 时出错: {e}")

    # 等待所有任务完成
    print("\n⏳ 正在等待所有任务完成...")
    for pdf_file, task_id in task_ids:
        try:
            download_url = client.wait_for_completion(task_id)
            print(f"✅ {pdf_file}: {download_url}")
        except Exception as e:
            print(f"❌ {pdf_file} 失败: {e}")


def example_9_custom_endpoint():
    """示例 9: 使用自定义上传端点"""
    print("\n" + "="*60)
    print("示例 9: 自定义上传端点")
    print("="*60)

    client = PDFCraftClient(
        api_key=API_KEY,
        upload_base_url="https://custom.example.com/upload"
    )

    download_url = client.convert_local_pdf("document.pdf")
    print(f"✅ 下载链接: {download_url}")


def example_10_async_workflow():
    """示例 10: 异步工作流 (现在提交,稍后检查)"""
    print("\n" + "="*60)
    print("示例 10: 异步工作流")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # 立即提交并获取任务 ID
    task_id = client.convert_local_pdf("document.pdf", wait=False)
    print(f"✅ 任务已提交: {task_id}")
    print("💡 现在你可以做其他工作...")

    # 稍后检查结果
    print("\n⏳ 正在检查结果...")
    download_url = client.wait_for_completion(task_id)
    print(f"✅ 下载链接: {download_url}")


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("PDF Craft SDK - 完整使用示例")
    print("="*60)

    # 检查 API key
    if API_KEY == "your_api_key_here":
        print("\n❌ 错误: 请在脚本中设置你的 API 密钥")
        print("   从这里获取 API 密钥: https://console.oomol.com/api-key")
        print("   然后将 'your_api_key_here' 替换为你的实际 API 密钥")
        return

    examples = [
        ("基础转换", example_1_basic_conversion),
        ("进度追踪", example_2_with_progress),
        ("EPUB 转换", example_3_epub_conversion),
        ("手动分步", example_4_manual_steps),
        ("远程 PDF", example_5_remote_pdf),
        ("自定义轮询", example_6_custom_polling),
        ("错误处理", example_7_error_handling),
        ("批量处理", example_8_batch_processing),
        ("自定义端点", example_9_custom_endpoint),
        ("异步工作流", example_10_async_workflow),
    ]

    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n" + "="*60)
    choice = input("\n输入示例编号 (1-10) 或 'all' 运行全部: ").strip().lower()

    if choice == 'all':
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n❌ 示例失败: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        try:
            examples[int(choice) - 1][1]()
        except Exception as e:
            print(f"\n❌ 示例失败: {e}")
    else:
        print("❌ 无效选择")

    print("\n" + "="*60)
    print("完成!")
    print("="*60)


if __name__ == "__main__":
    main()
