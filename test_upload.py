"""
测试上传功能的示例脚本
"""

import os
from pdf_craft_sdk import PDFCraftClient, UploadProgress

def test_upload():
    # 从环境变量获取 API key
    api_key = os.getenv("PDF_CRAFT_API_KEY")
    if not api_key:
        print("请设置 PDF_CRAFT_API_KEY 环境变量")
        return

    # 创建客户端
    client = PDFCraftClient(api_key=api_key)

    # 测试文件路径 - 请修改为实际的 PDF 文件路径
    test_file = "test.pdf"

    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        print("请创建一个测试 PDF 文件或修改 test_file 变量")
        return

    print(f"开始上传文件: {test_file}")
    print(f"文件大小: {os.path.getsize(test_file)} 字节")

    # 定义进度回调函数
    def on_progress(progress: UploadProgress):
        print(f"上传进度: {progress.percentage:.2f}% "
              f"({progress.current_part}/{progress.total_parts} 分片, "
              f"{progress.uploaded_bytes}/{progress.total_bytes} 字节)")

    try:
        # 测试 1: 仅上传文件
        print("\n=== 测试 1: 上传文件 ===")
        cache_url = client.upload_file(test_file, progress_callback=on_progress)
        print(f"✓ 上传成功!")
        print(f"缓存 URL: {cache_url}")

        # 测试 2: 上传并转换
        print("\n=== 测试 2: 上传并转换为 Markdown ===")

        def on_upload_progress(progress: UploadProgress):
            print(f"上传: {progress.percentage:.2f}%")

        print("开始上传和转换...")
        download_url = client.convert_local_pdf(
            test_file,
            format_type="markdown",
            progress_callback=on_upload_progress,
            wait=True
        )
        print(f"✓ 转换成功!")
        print(f"下载 URL: {download_url}")

    except FileNotFoundError as e:
        print(f"✗ 文件未找到: {e}")
    except Exception as e:
        print(f"✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_upload()
