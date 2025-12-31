# PDF Craft SDK

[English](README.md) | 简体中文

一个用于与 PDF Craft API 交互的 Python SDK。它简化了将 PDF 转换为 Markdown 或 EPUB 的过程,处理身份验证、文件上传、任务提交和结果轮询。

## 功能特性

- 🚀 **简单的 PDF 转换**: 将 PDF 转换为 Markdown 或 EPUB 格式
- 📤 **本地文件上传**: 上传并转换本地 PDF 文件,支持进度追踪
- 🔄 **自动重试**: 内置重试机制确保操作稳定
- ⏱️ **灵活的轮询策略**: 可配置的任务完成轮询策略
- 📊 **进度追踪**: 通过回调函数监控上传进度
- 🔧 **类型安全**: 完整的类型提示支持

## 安装

从 PyPI 安装:

```bash
pip install pdf-craft-sdk
```

## 快速开始

### 转换本地 PDF 文件

转换本地 PDF 文件最简单的方式:

```python
from pdf_craft_sdk import PDFCraftClient

# 初始化客户端
client = PDFCraftClient(api_key="YOUR_API_KEY")

# 上传并转换本地 PDF 文件
download_url = client.convert_local_pdf("document.pdf")
print(f"转换成功! 下载链接: {download_url}")
```

> 💡 **查看 [examples_zh.py](examples_zh.py) 获取涵盖所有功能的 10 个完整使用示例!**

### 转换远程 PDF 文件

如果你已经有来自上传 API 的 PDF URL:

```python
from pdf_craft_sdk import PDFCraftClient, FormatType

client = PDFCraftClient(api_key="YOUR_API_KEY")

# 转换 PDF 为 Markdown 并等待结果
try:
    pdf_url = "https://oomol-file-cache.example.com/your-file.pdf"
    download_url = client.convert(pdf_url, format_type=FormatType.MARKDOWN)
    print(f"转换成功! 下载链接: {download_url}")
except Exception as e:
    print(f"发生错误: {e}")
```

## 使用示例

### 带进度追踪的上传

监控大文件的上传进度:

```python
from pdf_craft_sdk import PDFCraftClient, UploadProgress

def on_progress(progress: UploadProgress):
    print(f"上传进度: {progress.percentage:.2f}% "
          f"({progress.current_part}/{progress.total_parts} 分片)")

client = PDFCraftClient(api_key="YOUR_API_KEY")

# 上传并转换,显示进度
download_url = client.convert_local_pdf(
    "large_document.pdf",
    progress_callback=on_progress
)
```

### 转换为 EPUB 格式

```python
from pdf_craft_sdk import PDFCraftClient, FormatType

client = PDFCraftClient(api_key="YOUR_API_KEY")

# 转换为 EPUB 格式并包含脚注
download_url = client.convert_local_pdf(
    "document.pdf",
    format_type=FormatType.EPUB,
    includes_footnotes=True
)
```

### 手动上传和转换

如果你希望手动处理各个步骤或进行异步处理:

```python
from pdf_craft_sdk import PDFCraftClient, FormatType

client = PDFCraftClient(api_key="YOUR_API_KEY")

# 步骤 1: 上传本地文件
cache_url = client.upload_file("document.pdf")
print(f"已上传到: {cache_url}")

# 步骤 2: 提交转换任务
task_id = client.submit_conversion(cache_url, format_type=FormatType.MARKDOWN)
print(f"任务 ID: {task_id}")

# 步骤 3: 等待完成
download_url = client.wait_for_completion(task_id)
print(f"下载链接: {download_url}")
```

## 配置

### 轮询策略

`convert` 和 `wait_for_completion` 方法接受可选的轮询行为配置:

- `max_wait_ms`: 等待转换的最大时间(毫秒)。默认 7200000 (2 小时)
- `check_interval_ms`: 初始轮询间隔(毫秒)。默认 1000 (1 秒)
- `max_check_interval_ms`: 最大轮询间隔(毫秒)。默认 5000 (5 秒)
- `backoff_factor`: 每次检查后增加间隔的乘数,或 `PollingStrategy` 枚举。默认 `PollingStrategy.EXPONENTIAL` (1.5)

可用的轮询策略:

- `PollingStrategy.EXPONENTIAL` (1.5): 默认。快速开始,逐渐减慢
- `PollingStrategy.FIXED` (1.0): 固定间隔轮询
- `PollingStrategy.AGGRESSIVE` (2.0): 每次间隔加倍

```python
from pdf_craft_sdk import PollingStrategy

# 示例: 稳定轮询 (每 3 秒)
download_url = client.convert(
    pdf_url="https://oomol-file-cache.example.com/your-file.pdf",
    check_interval_ms=3000,
    max_check_interval_ms=3000,
    backoff_factor=PollingStrategy.FIXED
)

# 示例: 长时间运行任务 (慢速开始,不频繁检查)
download_url = client.convert(
    pdf_url="https://oomol-file-cache.example.com/your-file.pdf",
    check_interval_ms=5000,
    max_check_interval_ms=60000,  # 1 分钟
    backoff_factor=PollingStrategy.AGGRESSIVE
)
```

## API 参考

### PDFCraftClient

#### 构造函数

```python
PDFCraftClient(api_key, base_url=None, upload_base_url=None)
```

初始化 PDF Craft 客户端。

**参数:**

- `api_key` (str): 你的 API 密钥
- `base_url` (str, 可选): 自定义 API 基础 URL
- `upload_base_url` (str, 可选): 自定义上传 API 基础 URL

#### 方法

##### `convert_local_pdf(file_path, **kwargs)`

一步完成上传和转换本地 PDF 文件。

**参数:**

- `file_path` (str): 本地 PDF 文件路径
- `format_type` (str | FormatType): 输出格式,"markdown" 或 "epub" (默认: "markdown")
- `model` (str): 使用的模型 (默认: "gundam")
- `includes_footnotes` (bool): 包含脚注 (默认: False)
- `ignore_pdf_errors` (bool): 忽略 PDF 解析错误 (默认: True)
- `ignore_ocr_errors` (bool): 忽略 OCR 错误 (默认: True)
- `wait` (bool): 等待完成 (默认: True)
- `max_wait_ms` (int): 最大等待时间(毫秒) (默认: 7200000)
- `check_interval_ms` (int): 初始轮询间隔(毫秒) (默认: 1000)
- `max_check_interval_ms` (int): 最大轮询间隔(毫秒) (默认: 5000)
- `backoff_factor` (float | PollingStrategy): 轮询退避因子 (默认: PollingStrategy.EXPONENTIAL)
- `progress_callback` (callable): 上传进度回调函数
- `upload_max_retries` (int): 每个分片的最大上传重试次数 (默认: 3)

**返回:** 如果 `wait=True` 返回下载 URL (str),否则返回任务 ID (str)

##### `upload_file(file_path, progress_callback=None, max_retries=3)`

上传本地 PDF 文件到云端缓存。

**参数:**

- `file_path` (str): 本地 PDF 文件路径
- `progress_callback` (callable): 进度回调函数
- `max_retries` (int): 每个分片的最大重试次数 (默认: 3)

**返回:** 缓存 URL (str)

##### `convert(pdf_url, **kwargs)`

从 URL 转换 PDF。

**参数:**

- `pdf_url` (str): 要转换的 PDF URL (来自上传 API 的 HTTPS URL)
- `format_type` (str | FormatType): 输出格式 (默认: "markdown")
- 其他参数与 `convert_local_pdf` 相同

**返回:** 下载 URL (str)

##### `submit_conversion(pdf_url, **kwargs)`

提交转换任务而不等待。

**参数:**

- `pdf_url` (str): 要转换的 PDF URL
- `format_type` (str | FormatType): 输出格式
- `model` (str): 使用的模型
- `includes_footnotes` (bool): 包含脚注
- `ignore_pdf_errors` (bool): 忽略 PDF 解析错误
- `ignore_ocr_errors` (bool): 忽略 OCR 错误

**返回:** 任务 ID (str)

##### `wait_for_completion(task_id, **kwargs)`

等待转换任务完成。

**参数:**

- `task_id` (str): 从 `submit_conversion` 获取的任务 ID
- 轮询参数与 `convert_local_pdf` 相同

**返回:** 下载 URL (str)

### UploadProgress

文件上传的进度信息。

**属性:**

- `uploaded_bytes` (int): 已上传的字节数
- `total_bytes` (int): 总字节数
- `current_part` (int): 当前正在上传的分片编号
- `total_parts` (int): 总分片数
- `percentage` (float): 进度百分比 (0-100)

**示例:**

```python
def on_progress(progress):
    print(f"{progress.percentage:.1f}% - 分片 {progress.current_part}/{progress.total_parts}")
```

## 错误处理

SDK 会抛出以下异常:

- `FileNotFoundError`: 指定的文件不存在
- `APIError`: API 请求失败
- `TimeoutError`: 转换超过最大等待时间

**示例:**

```python
from pdf_craft_sdk import PDFCraftClient
from pdf_craft_sdk.exceptions import APIError

client = PDFCraftClient(api_key="YOUR_API_KEY")

try:
    download_url = client.convert_local_pdf("document.pdf")
    print(f"成功: {download_url}")
except FileNotFoundError:
    print("文件未找到!")
except APIError as e:
    print(f"API 错误: {e}")
except TimeoutError:
    print("转换超时")
```

## 高级功能

### 自定义上传端点

如果需要使用自定义的上传 API 端点:

```python
client = PDFCraftClient(
    api_key="YOUR_API_KEY",
    upload_base_url="https://custom.example.com/upload"
)
```

默认上传端点: `https://llm.oomol.com/api/tasks/files/remote-cache`

### 批量处理

处理多个文件:

```python
from pdf_craft_sdk import PDFCraftClient

client = PDFCraftClient(api_key="YOUR_API_KEY")

pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

for pdf_file in pdf_files:
    try:
        print(f"正在处理 {pdf_file}...")
        download_url = client.convert_local_pdf(pdf_file, wait=False)
        print(f"任务已提交: {download_url}")
    except Exception as e:
        print(f"处理 {pdf_file} 时出错: {e}")
```

## 许可证

本项目采用 MIT 许可证。

## 支持

如有问题、疑问或想要贡献,请访问我们的 [GitHub 仓库](https://github.com/your-repo/pdf-craft-sdk)。

## 完整示例

查看 [examples_zh.py](examples_zh.py) 获取完整的可运行示例,包括:

1. ✅ 基础本地 PDF 转换
2. 📊 带进度追踪的上传
3. 📖 EPUB 格式转换
4. 🔧 手动分步上传和转换
5. 🌐 远程 PDF 转换
6. ⚙️ 自定义轮询策略
7. 🛡️ 正确的错误处理
8. 📦 批量处理多个文件
9. 🔌 自定义上传端点
10. ⏱️ 异步工作流 (现在提交,稍后检查)

运行示例:

```bash
# 从 https://console.oomol.com/api-key 获取你的 API 密钥
# 然后编辑 examples_zh.py 并将 'your_api_key_here' 替换为你的实际 API 密钥

# 运行示例
python examples_zh.py

# 选择特定示例 (1-10) 或 'all' 运行所有示例
```

## 更新日志

### 版本 0.4.0

- ✨ 添加本地文件上传功能
- ✨ 添加 `convert_local_pdf()` 便捷方法
- ✨ 添加上传进度追踪回调功能
- 🐛 修复上传响应中 `uploaded_parts` 为 null 的处理
- 📝 改进文档和示例

### 版本 0.3.0

- 初始公开发布
- 基本的 PDF 到 Markdown/EPUB 转换
- 可配置的轮询策略
