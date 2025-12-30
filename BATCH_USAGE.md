# 批处理功能使用指南

本文档介绍如何使用 PDFCraft SDK Python 版本的批处理功能进行批量 PDF 转换。

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [API 参考](#api-参考)
- [示例代码](#示例代码)
- [常见问题](#常见问题)

## 安装

```bash
pip install pdf-craft-sdk
```

## 快速开始

批处理功能允许您一次性提交多个 PDF 文件进行转换,并提供进度追踪、暂停/恢复、重试等功能。

### 基本用法

```python
import os
from pdf_craft_sdk import PDFCraftClient, BatchFile, FormatType

# 初始化客户端
client = PDFCraftClient(api_key=os.getenv("PDF_CRAFT_API_KEY"))

# 准备文件列表
files = [
    BatchFile(
        url="https://example.com/doc1.pdf",
        file_name="document1.pdf"
    ),
    BatchFile(
        url="https://example.com/doc2.pdf",
        file_name="document2.pdf"
    )
]

# 创建批次
batch = client.create_batch(
    files=files,
    output_format=FormatType.MARKDOWN,
    includes_footnotes=False
)

print(f"批次 ID: {batch.batch_id}")

# 启动批次
result = client.start_batch(batch.batch_id)
print(f"已排队任务数: {result.queued_jobs}")

# 查询批次状态
batch_detail = client.get_batch(batch.batch_id)
print(f"进度: {batch_detail.progress}%")
```

## API 参考

### PDFCraftClient 批处理方法

#### create_batch()

创建新的批处理任务。

```python
def create_batch(
    files: List[Union[BatchFile, Dict[str, Any]]],
    output_format: Union[str, FormatType] = FormatType.MARKDOWN,
    includes_footnotes: bool = False
) -> CreateBatchResponse
```

**参数:**
- `files`: 文件列表,每个元素可以是 `BatchFile` 对象或包含 `url` 和 `fileName` 的字典
- `output_format`: 输出格式,可选 `"markdown"` 或 `"epub"` (默认: `"markdown"`)
- `includes_footnotes`: 是否包含脚注引用 (默认: `False`)

**返回:** `CreateBatchResponse` 对象,包含批次 ID、状态等信息

#### start_batch()

启动批次处理。

```python
def start_batch(batch_id: str) -> OperationResponse
```

**参数:**
- `batch_id`: 批次 ID

**返回:** `OperationResponse` 对象,包含排队任务数等信息

#### get_batch()

获取批次详情。

```python
def get_batch(batch_id: str) -> BatchDetail
```

**参数:**
- `batch_id`: 批次 ID

**返回:** `BatchDetail` 对象,包含批次状态、进度、完成数等详细信息

#### get_batches()

获取用户的所有批次列表。

```python
def get_batches(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = "all",
    sort_by: str = "createdAt",
    sort_order: str = "desc"
) -> GetBatchesResponse
```

**参数:**
- `page`: 页码 (默认: 1)
- `page_size`: 每页条数 (默认: 20)
- `status`: 状态筛选,可选 `"all"`, `"pending"`, `"processing"`, `"completed"`, `"failed"`, `"cancelled"`, `"paused"` (默认: `"all"`)
- `sort_by`: 排序字段,可选 `"createdAt"`, `"updatedAt"` (默认: `"createdAt"`)
- `sort_order`: 排序方向,可选 `"asc"`, `"desc"` (默认: `"desc"`)

**返回:** `GetBatchesResponse` 对象,包含批次列表和分页信息

#### get_batch_jobs()

获取批次的任务列表。

```python
def get_batch_jobs(
    batch_id: str,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = "all"
) -> GetJobsResponse
```

**参数:**
- `batch_id`: 批次 ID
- `page`: 页码 (默认: 1)
- `page_size`: 每页条数 (默认: 20)
- `status`: 状态筛选 (默认: `"all"`)

**返回:** `GetJobsResponse` 对象,包含任务列表和分页信息

#### pause_batch()

暂停批次处理。

```python
def pause_batch(batch_id: str) -> OperationResponse
```

#### resume_batch()

恢复批次处理。

```python
def resume_batch(batch_id: str) -> OperationResponse
```

#### cancel_batch()

取消批次处理。

```python
def cancel_batch(batch_id: str) -> OperationResponse
```

#### retry_failed_jobs()

重试批次中的所有失败任务。

```python
def retry_failed_jobs(batch_id: str) -> OperationResponse
```

#### retry_job()

重试单个失败任务。

```python
def retry_job(job_id: str) -> OperationResponse
```

#### cancel_job()

取消单个任务。

```python
def cancel_job(job_id: str) -> OperationResponse
```

#### get_concurrent_status()

获取用户并发状态。

```python
def get_concurrent_status() -> ConcurrentStatus
```

**返回:** `ConcurrentStatus` 对象,包含最大并发数、当前运行任务数等信息

## 示例代码

### 完整的批处理流程

```python
import os
import time
from pdf_craft_sdk import PDFCraftClient, BatchFile, FormatType

# 初始化客户端
client = PDFCraftClient(api_key=os.getenv("PDF_CRAFT_API_KEY"))

# 1. 创建批次
files = [
    BatchFile(url="https://example.com/doc1.pdf", file_name="doc1.pdf"),
    BatchFile(url="https://example.com/doc2.pdf", file_name="doc2.pdf"),
]

batch = client.create_batch(
    files=files,
    output_format=FormatType.MARKDOWN
)

batch_id = batch.batch_id
print(f"批次已创建: {batch_id}")

# 2. 启动批次
client.start_batch(batch_id)
print("批次已启动")

# 3. 轮询等待完成
while True:
    batch_detail = client.get_batch(batch_id)
    print(f"进度: {batch_detail.progress}% | "
          f"状态: {batch_detail.status} | "
          f"已完成: {batch_detail.completed_files}/{batch_detail.total_files}")

    # 检查是否完成
    if batch_detail.status in ["completed", "failed", "cancelled"]:
        break

    time.sleep(5)  # 等待 5 秒

# 4. 获取任务结果
jobs_result = client.get_batch_jobs(batch_id)
for job in jobs_result.jobs:
    if job.status == "completed":
        print(f"文件 {job.file_name} 转换成功: {job.result_url}")
    elif job.status == "failed":
        print(f"文件 {job.file_name} 转换失败: {job.error_message}")
```

### 使用字典格式创建批次

```python
# 使用字典格式而不是 BatchFile 对象
files = [
    {"url": "https://example.com/doc1.pdf", "fileName": "doc1.pdf"},
    {"url": "https://example.com/doc2.pdf", "fileName": "doc2.pdf"},
]

batch = client.create_batch(files=files)
```

### 批次控制操作

```python
# 暂停批次
result = client.pause_batch(batch_id)
print(f"已暂停 {result.paused_jobs} 个任务")

# 恢复批次
result = client.resume_batch(batch_id)
print(f"已恢复 {result.resumed_jobs} 个任务")

# 重试失败的任务
result = client.retry_failed_jobs(batch_id)
print(f"已重试 {result.retried_jobs} 个任务")

# 取消批次
result = client.cancel_batch(batch_id)
print(f"已取消 {result.cancelled_jobs} 个任务")
```

### 查询并发状态

```python
status = client.get_concurrent_status()
print(f"最大并发数: {status.max_concurrent_jobs}")
print(f"当前运行任务数: {status.current_running_jobs}")
print(f"可以提交新任务: {status.can_submit_new_job}")
```

## 数据类型

### BatchFile

批次文件信息。

**属性:**
- `url` (str): PDF 文件的云端 URL
- `file_name` (str): 文件名
- `file_size` (Optional[int]): 文件大小(字节)

### BatchDetail

批次详情。

**属性:**
- `id` (str): 批次 ID
- `status` (str): 批次状态
- `output_format` (str): 输出格式
- `includes_footnotes` (bool): 是否包含脚注引用
- `total_files` (int): 总文件数
- `completed_files` (int): 已完成文件数
- `failed_files` (int): 失败文件数
- `progress` (int): 进度百分比 (0-100)
- `created_at` (str): 创建时间
- `updated_at` (str): 更新时间

### JobDetail

任务详情。

**属性:**
- `id` (str): 任务 ID
- `batch_id` (str): 批次 ID
- `file_name` (str): 文件名
- `status` (str): 任务状态
- `result_url` (Optional[str]): 结果下载 URL
- `error_message` (Optional[str]): 错误信息
- `progress` (Optional[int]): 进度百分比
- 等...

## 常见问题

### Q: 批次最多可以包含多少个文件?

A: 建议单个批次不超过 30 个文件。如需转换更多文件,请创建多个批次。

### Q: 如何处理失败的任务?

A: 可以使用 `retry_failed_jobs()` 方法重试批次中的所有失败任务,或使用 `retry_job()` 重试单个任务。

### Q: 批次可以暂停吗?

A: 是的,使用 `pause_batch()` 方法可以暂停批次,使用 `resume_batch()` 恢复。

### Q: 如何获取转换结果?

A: 使用 `get_batch_jobs()` 获取任务列表,已完成的任务会有 `result_url` 字段,可以下载转换结果。

### Q: 批次状态有哪些?

A: 批次状态包括:
- `pending`: 待处理
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 失败
- `cancelled`: 已取消
- `paused`: 已暂停

## 更多示例

完整的示例代码请参考项目根目录的 [batch_example.py](./batch_example.py) 文件。
