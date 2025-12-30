# PDF 上传功能使用说明

本文档介绍如何使用 Python SDK 的 PDF 上传功能来转换本地 PDF 文件。

## 功能概述

上传功能允许您将本地 PDF 文件上传到云端缓存，然后使用转换 API 进行处理。支持的主要功能：

- 分片上传大文件
- 上传进度跟踪
- 自动重试机制
- 便捷的本地文件转换方法

## 安装

确保已安装 pdf-craft-sdk：

```bash
pip install pdf-craft-sdk
```

## 基本用法

### 1. 仅上传文件

如果您只需要上传文件并获取云端 URL：

```python
from pdf_craft_sdk import PDFCraftClient

client = PDFCraftClient(api_key="your_api_key")

# 上传文件
cache_url = client.upload_file("document.pdf")
print(f"文件已上传: {cache_url}")

# 之后可以使用 cache_url 进行转换
task_id = client.submit_conversion(cache_url, format_type="markdown")
```

### 2. 上传并转换（推荐）

使用便捷方法 `convert_local_pdf` 一次完成上传和转换：

```python
from pdf_craft_sdk import PDFCraftClient

client = PDFCraftClient(api_key="your_api_key")

# 上传并转换为 Markdown
download_url = client.convert_local_pdf("document.pdf")
print(f"转换完成: {download_url}")
```

### 3. 带进度回调的上传

监控上传进度：

```python
from pdf_craft_sdk import PDFCraftClient, UploadProgress

def on_progress(progress: UploadProgress):
    print(f"上传进度: {progress.percentage:.2f}% "
          f"({progress.current_part}/{progress.total_parts} 分片)")

client = PDFCraftClient(api_key="your_api_key")

# 上传文件并显示进度
cache_url = client.upload_file(
    "large_document.pdf",
    progress_callback=on_progress
)
```

### 4. 完整示例：上传并转换为 EPUB

```python
from pdf_craft_sdk import PDFCraftClient, UploadProgress, FormatType

def on_upload_progress(progress: UploadProgress):
    print(f"上传: {progress.percentage:.2f}%")

client = PDFCraftClient(api_key="your_api_key")

# 上传并转换为 EPUB 格式
download_url = client.convert_local_pdf(
    file_path="document.pdf",
    format_type=FormatType.EPUB,
    includes_footnotes=True,
    progress_callback=on_upload_progress,
    wait=True
)

print(f"EPUB 文件已生成: {download_url}")
```

## API 参考

### `upload_file()`

上传本地 PDF 文件到云端。

**参数：**

- `file_path` (str): 本地 PDF 文件路径（必需）
- `progress_callback` (ProgressCallback, 可选): 进度回调函数
- `max_retries` (int, 可选): 每个分片的最大重试次数，默认 3

**返回：** `str` - 文件的云端缓存 URL（例如 "cache://xxx.pdf"）

**异常：**

- `FileNotFoundError`: 文件不存在
- `APIError`: 上传失败

### `convert_local_pdf()`

上传本地 PDF 文件并进行转换的便捷方法。

**参数：**

- `file_path` (str): 本地 PDF 文件路径（必需）
- `format_type` (str | FormatType): 输出格式，默认 "markdown"
- `model` (str): 使用的模型，默认 "gundam"
- `includes_footnotes` (bool): 是否处理脚注，默认 False
- `ignore_pdf_errors` (bool): 是否忽略 PDF 解析错误，默认 True
- `ignore_ocr_errors` (bool): 是否忽略 OCR 识别错误，默认 True
- `wait` (bool): 是否等待转换完成，默认 True
- `max_wait_ms` (int): 最大等待时间（毫秒），默认 7200000（2 小时）
- `check_interval_ms` (int): 初始轮询间隔（毫秒），默认 1000
- `max_check_interval_ms` (int): 最大轮询间隔（毫秒），默认 5000
- `backoff_factor` (float | PollingStrategy): 轮询间隔增长因子，默认指数增长
- `progress_callback` (ProgressCallback, 可选): 上传进度回调函数
- `upload_max_retries` (int): 上传分片的最大重试次数，默认 3

**返回：**

- 如果 `wait=True`：返回下载 URL (str)
- 如果 `wait=False`：返回任务 ID (str)

**异常：**

- `FileNotFoundError`: 文件不存在
- `APIError`: 上传或转换失败
- `TimeoutError`: 转换超时

### `UploadProgress` 类

上传进度信息对象。

**属性：**

- `uploaded_bytes` (int): 已上传的字节数
- `total_bytes` (int): 总字节数
- `current_part` (int): 当前分片编号
- `total_parts` (int): 总分片数
- `percentage` (float): 上传进度百分比（0-100）

## 高级配置

### 自定义上传 API 端点

如果需要使用自定义的上传 API 端点：

```python
client = PDFCraftClient(
    api_key="your_api_key",
    upload_base_url="https://custom.example.com/upload"
)
```

默认的上传 API 端点是：`https://llm.oomol.com/api/tasks/files/remote-cache`

### 调整重试策略

```python
# 上传时使用更多重试次数
cache_url = client.upload_file(
    "document.pdf",
    max_retries=5  # 每个分片最多重试 5 次
)

# 转换时使用自定义轮询策略
from pdf_craft_sdk import PollingStrategy

download_url = client.convert_local_pdf(
    "document.pdf",
    check_interval_ms=2000,        # 初始间隔 2 秒
    max_check_interval_ms=10000,   # 最大间隔 10 秒
    backoff_factor=PollingStrategy.LINEAR,  # 使用线性增长
    upload_max_retries=5
)
```

## 技术细节

### 分片上传机制

SDK 使用分片上传来处理大文件：

1. **初始化上传**：调用 `/init` 端点获取上传 ID 和预签名 URL
2. **分片上传**：将文件分成多个分片，并行上传到预签名 URL
3. **获取 URL**：调用 `/{upload_id}/url` 端点获取最终的缓存 URL

分片大小由服务器自动确定，通常为 5MB。

### 错误处理

上传过程中的错误会自动重试：

- 网络错误：使用指数退避策略自动重试
- HTTP 错误：根据 `max_retries` 参数重试
- 超时错误：在转换阶段根据 `max_wait_ms` 参数判断

### API 端点

上传功能使用以下 API 端点（基于 `upload_base_url`）：

- `POST {upload_base_url}/init` - 初始化分片上传
- `PUT {presigned_url}` - 上传单个分片
- `GET {upload_base_url}/{upload_id}/url` - 获取最终文件 URL

## 常见问题

### Q: 支持的最大文件大小是多少？

A: 理论上没有限制，但建议单个文件不超过 200MB。更大的文件会自动分片上传。

### Q: 上传的文件会保存多久？

A: 上传的文件作为临时缓存保存，具体保留时间取决于服务器配置。建议上传后尽快进行转换。

### Q: 可以上传非 PDF 文件吗？

A: SDK 主要设计用于 PDF 文件。虽然技术上可以上传其他文件，但转换 API 只支持 PDF 格式。

### Q: 如何处理上传失败？

A: SDK 会自动重试失败的分片上传。如果仍然失败，会抛出 `APIError` 异常。您可以捕获异常并进行自定义处理。

## 示例代码

完整的示例代码请参考：

- `test_upload.py` - 功能测试示例
- `test_upload_unit.py` - 单元测试示例

## 支持

如有问题或建议，请联系技术支持或查看 SDK 文档。
