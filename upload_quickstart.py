#!/usr/bin/env python3
"""
PDF 上传功能快速开始示例

这是一个最简单的示例，展示如何使用上传功能。
"""

import os
from pdf_craft_sdk import PDFCraftClient, UploadProgress

# 配置
API_KEY = os.getenv("PDF_CRAFT_API_KEY", "your_api_key_here")
PDF_FILE = "document.pdf"  # 修改为您的 PDF 文件路径

def main():
    # 创建客户端
    client = PDFCraftClient(api_key=API_KEY)

    print("PDF 上传快速开始示例\n")

    # 示例 1: 最简单的用法 - 上传并转换
    print("=" * 50)
    print("示例 1: 上传并转换 PDF（最简单）")
    print("=" * 50)

    try:
        download_url = client.convert_local_pdf(PDF_FILE)
        print(f"✓ 成功！下载 URL: {download_url}")
    except FileNotFoundError:
        print(f"✗ 文件未找到: {PDF_FILE}")
        print("请修改 PDF_FILE 变量为实际的 PDF 文件路径")
        return
    except Exception as e:
        print(f"✗ 错误: {e}")
        return

    # 示例 2: 带进度显示
    print("\n" + "=" * 50)
    print("示例 2: 带进度显示的上传")
    print("=" * 50)

    def show_progress(progress: UploadProgress):
        bar_length = 40
        filled = int(bar_length * progress.percentage / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r上传进度: [{bar}] {progress.percentage:.1f}% "
              f"({progress.current_part}/{progress.total_parts} 分片)", end='')

    try:
        download_url = client.convert_local_pdf(
            PDF_FILE,
            progress_callback=show_progress
        )
        print(f"\n✓ 成功！下载 URL: {download_url}")
    except Exception as e:
        print(f"\n✗ 错误: {e}")

    # 示例 3: 仅上传文件
    print("\n" + "=" * 50)
    print("示例 3: 仅上传文件（不转换）")
    print("=" * 50)

    try:
        cache_url = client.upload_file(PDF_FILE)
        print(f"✓ 文件已上传到云端")
        print(f"缓存 URL: {cache_url}")
        print(f"您可以稍后使用此 URL 进行转换")
    except Exception as e:
        print(f"✗ 错误: {e}")

    # 示例 4: 转换为 EPUB 格式
    print("\n" + "=" * 50)
    print("示例 4: 上传并转换为 EPUB 格式")
    print("=" * 50)

    try:
        download_url = client.convert_local_pdf(
            PDF_FILE,
            format_type="epub",
            includes_footnotes=True,
            progress_callback=lambda p: print(f"上传: {p.percentage:.0f}%")
        )
        print(f"✓ EPUB 文件已生成: {download_url}")
    except Exception as e:
        print(f"✗ 错误: {e}")

    print("\n" + "=" * 50)
    print("所有示例完成！")
    print("=" * 50)
    print("\n更多用法请参考 UPLOAD_USAGE.md 文档")


if __name__ == "__main__":
    main()
