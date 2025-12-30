"""
简单的上传功能单元测试
测试上传类型和 API 调用的基本逻辑
"""

import os
import sys
from pdf_craft_sdk import PDFCraftClient, UploadProgress

def test_upload_types():
    """测试上传类型定义"""
    print("=== 测试 1: UploadProgress 类型 ===")

    progress = UploadProgress(
        uploaded_bytes=5000,
        total_bytes=10000,
        current_part=1,
        total_parts=2
    )

    print(f"已上传字节: {progress.uploaded_bytes}")
    print(f"总字节数: {progress.total_bytes}")
    print(f"当前分片: {progress.current_part}")
    print(f"总分片数: {progress.total_parts}")
    print(f"百分比: {progress.percentage:.2f}%")

    assert progress.percentage == 50.0, "百分比计算错误"
    print("✓ UploadProgress 类型测试通过\n")


def test_client_initialization():
    """测试客户端初始化"""
    print("=== 测试 2: 客户端初始化 ===")

    # 使用默认 upload_base_url
    client = PDFCraftClient(api_key="test_key")
    print(f"默认上传 URL: {client.upload_base_url}")
    assert client.upload_base_url == "https://llm.oomol.com/api/tasks/files/remote-cache", "默认上传 URL 不正确"

    # 使用自定义 upload_base_url
    custom_url = "https://custom.example.com/upload"
    client2 = PDFCraftClient(api_key="test_key", upload_base_url=custom_url)
    print(f"自定义上传 URL: {client2.upload_base_url}")
    assert client2.upload_base_url == custom_url, "自定义上传 URL 不正确"

    print("✓ 客户端初始化测试通过\n")


def test_upload_methods_exist():
    """测试上传方法是否存在"""
    print("=== 测试 3: 上传方法存在性检查 ===")

    client = PDFCraftClient(api_key="test_key")

    # 检查方法是否存在
    assert hasattr(client, "_init_upload"), "缺少 _init_upload 方法"
    assert hasattr(client, "_upload_part"), "缺少 _upload_part 方法"
    assert hasattr(client, "_get_upload_url"), "缺少 _get_upload_url 方法"
    assert hasattr(client, "upload_file"), "缺少 upload_file 方法"
    assert hasattr(client, "convert_local_pdf"), "缺少 convert_local_pdf 方法"

    print("✓ 所有上传方法都已定义")
    print("✓ 上传方法存在性检查通过\n")


def test_file_not_found():
    """测试文件不存在的情况"""
    print("=== 测试 4: 文件不存在错误处理 ===")

    client = PDFCraftClient(api_key="test_key")

    try:
        client.upload_file("nonexistent_file.pdf")
        print("✗ 应该抛出 FileNotFoundError")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"✓ 正确捕获 FileNotFoundError: {e}")
        print("✓ 文件不存在错误处理测试通过\n")


def main():
    print("开始运行上传功能单元测试...\n")

    try:
        test_upload_types()
        test_client_initialization()
        test_upload_methods_exist()
        test_file_not_found()

        print("=" * 50)
        print("✓ 所有测试通过!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生意外错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
