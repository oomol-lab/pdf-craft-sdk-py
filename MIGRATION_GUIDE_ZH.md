# PDF Craft SDK - TypeScript 迁移指南

[English](MIGRATION_GUIDE.md) | 简体中文

本指南帮助 TypeScript SDK 开发者基于 Python SDK 的最新更新实现相应功能。

## 目录

- [概述](#概述)
- [核心变更](#核心变更)
- [1. 客户端初始化](#1-客户端初始化)
- [2. 文件上传功能](#2-文件上传功能)
- [3. 批处理 API](#3-批处理-api)
- [4. 类型定义](#4-类型定义)
- [5. 错误处理](#5-错误处理)
- [6. API 示例](#6-api-示例)

## 概述

Python SDK 已更新到 0.4.0+ 版本,包含以下主要功能:

1. **本地文件上传**: 支持上传本地 PDF 文件并显示进度追踪
2. **批处理**: 用于创建和管理批量转换任务的 API
3. **增强的类型安全**: 全面的类型定义和枚举
4. **改进的错误处理**: 更好的异常处理和 HTTP 状态检查

## 核心变更

### 新的基础 URL

客户端现在支持三个可配置的基础 URL:

```python
# Python
client = PDFCraftClient(
    api_key="YOUR_API_KEY",
    base_url="https://fusion-api.oomol.com/v1",  # 转换 API
    batch_base_url="https://pdf-server.oomol.com/api/v1/conversion",  # 批处理 API
    upload_base_url="https://llm.oomol.com/api/tasks/files/remote-cache"  # 上传 API
)
```

```typescript
// TypeScript 实现
interface PDFCraftClientOptions {
  apiKey: string;
  baseUrl?: string;
  batchBaseUrl?: string;
  uploadBaseUrl?: string;
}

class PDFCraftClient {
  constructor(options: PDFCraftClientOptions) {
    this.apiKey = options.apiKey;
    this.baseUrl = options.baseUrl || 'https://fusion-api.oomol.com/v1';
    this.batchBaseUrl = options.batchBaseUrl || 'https://pdf-server.oomol.com/api/v1/conversion';
    this.uploadBaseUrl = options.uploadBaseUrl || 'https://llm.oomol.com/api/tasks/files/remote-cache';
  }
}
```

## 1. 客户端初始化

### Python 实现

```python
from pdf_craft_sdk import PDFCraftClient

# 基础初始化
client = PDFCraftClient(api_key="YOUR_API_KEY")

# 使用自定义端点
client = PDFCraftClient(
    api_key="YOUR_API_KEY",
    base_url="https://custom.api.com/v1",
    upload_base_url="https://custom.upload.com"
)
```

### TypeScript 实现

```typescript
import { PDFCraftClient } from 'pdf-craft-sdk';

// 基础初始化
const client = new PDFCraftClient({ apiKey: 'YOUR_API_KEY' });

// 使用自定义端点
const client = new PDFCraftClient({
  apiKey: 'YOUR_API_KEY',
  baseUrl: 'https://custom.api.com/v1',
  uploadBaseUrl: 'https://custom.upload.com'
});
```

## 2. 文件上传功能

### 2.1 上传进度追踪

#### Python 实现

```python
from pdf_craft_sdk import PDFCraftClient, UploadProgress

def on_progress(progress: UploadProgress):
    print(f"上传进度: {progress.percentage:.2f}% "
          f"({progress.current_part}/{progress.total_parts} 分片)")

client = PDFCraftClient(api_key="YOUR_API_KEY")

# 上传文件并追踪进度
cache_url = client.upload_file(
    "document.pdf",
    progress_callback=on_progress,
    max_retries=3
)
```

#### TypeScript 实现

```typescript
interface UploadProgress {
  uploadedBytes: number;
  totalBytes: number;
  currentPart: number;
  totalParts: number;
  percentage: number;
}

type ProgressCallback = (progress: UploadProgress) => void;

// 在 PDFCraftClient 类中
async uploadFile(
  filePath: string,
  progressCallback?: ProgressCallback,
  maxRetries: number = 3
): Promise<string> {
  // 实现
  const fileSize = await fs.stat(filePath).then(stats => stats.size);
  const fileExtension = path.extname(filePath);

  // 初始化上传
  const initResponse = await this.initUpload(fileSize, fileExtension);

  // 上传分片并显示进度
  let uploadedBytes = 0;
  const fileStream = fs.createReadStream(filePath, {
    highWaterMark: initResponse.partSize
  });

  for (let partNumber = 1; partNumber <= initResponse.totalParts; partNumber++) {
    // 跳过已上传的分片
    if (initResponse.uploadedParts?.includes(partNumber)) {
      uploadedBytes += initResponse.partSize;
      continue;
    }

    const partData = await this.readChunk(fileStream, initResponse.partSize);
    await this.uploadPart(
      initResponse.presignedUrls[partNumber],
      partData,
      maxRetries
    );

    uploadedBytes += partData.length;

    if (progressCallback) {
      progressCallback({
        uploadedBytes,
        totalBytes: fileSize,
        currentPart: partNumber,
        totalParts: initResponse.totalParts,
        percentage: (uploadedBytes / fileSize) * 100
      });
    }
  }

  // 获取最终 URL
  return await this.getUploadUrl(initResponse.uploadId);
}
```

### 2.2 转换本地 PDF

#### Python 实现

```python
# 简单的一行转换
download_url = client.convert_local_pdf("document.pdf")

# 带选项
download_url = client.convert_local_pdf(
    "document.pdf",
    format_type=FormatType.EPUB,
    includes_footnotes=True,
    progress_callback=on_progress
)
```

#### TypeScript 实现

```typescript
interface ConvertLocalPdfOptions {
  formatType?: FormatType | string;
  model?: string;
  includesFootnotes?: boolean;
  ignorePdfErrors?: boolean;
  ignoreOcrErrors?: boolean;
  wait?: boolean;
  maxWaitMs?: number;
  checkIntervalMs?: number;
  maxCheckIntervalMs?: number;
  backoffFactor?: number | PollingStrategy;
  progressCallback?: ProgressCallback;
  uploadMaxRetries?: number;
}

async convertLocalPdf(
  filePath: string,
  options?: ConvertLocalPdfOptions
): Promise<string> {
  // 先上传文件
  const cacheUrl = await this.uploadFile(
    filePath,
    options?.progressCallback,
    options?.uploadMaxRetries ?? 3
  );

  // 然后转换
  return await this.convert(cacheUrl, options);
}
```

### 2.3 内部上传方法

#### Python 实现

```python
# 初始化上传
def _init_upload(self, file_size: int, file_extension: str) -> InitUploadResponse:
    endpoint = f"{self.upload_base_url}/init"
    data = {
        "file_extension": file_extension,
        "size": file_size
    }
    response = requests.post(endpoint, json=data, headers=self.headers)
    result = response.json()
    data_result = result.get("data", result)

    return InitUploadResponse(
        upload_id=data_result["upload_id"],
        part_size=data_result["part_size"],
        total_parts=data_result["total_parts"],
        uploaded_parts=data_result.get("uploaded_parts", []),
        presigned_urls=data_result["presigned_urls"]
    )

# 上传分片并重试
def _upload_part(self, presigned_url: str, part_data: bytes, max_retries: int = 3) -> None:
    headers = {"Content-Type": "application/octet-stream"}

    for attempt in range(max_retries):
        try:
            response = requests.put(presigned_url, data=part_data, headers=headers)
            if response.ok:
                return
            elif attempt == max_retries - 1:
                raise APIError(f"Failed to upload part after {max_retries} attempts")
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise APIError(f"Failed to upload part: {str(e)}")
            time.sleep(2 ** attempt)  # 指数退避

# 获取上传 URL
def _get_upload_url(self, upload_id: str) -> str:
    endpoint = f"{self.upload_base_url}/{upload_id}/url"
    response = requests.get(endpoint, headers=self.headers)
    result = response.json()
    data_result = result.get("data", result)
    return data_result["url"]
```

#### TypeScript 实现

```typescript
interface InitUploadResponse {
  uploadId: string;
  partSize: number;
  totalParts: number;
  uploadedParts?: number[];
  presignedUrls: Record<string, string>;
}

private async initUpload(
  fileSize: number,
  fileExtension: string
): Promise<InitUploadResponse> {
  const endpoint = `${this.uploadBaseUrl}/init`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`
    },
    body: JSON.stringify({
      file_extension: fileExtension,
      size: fileSize
    })
  });

  if (!response.ok) {
    throw new APIError(`HTTP ${response.status}: ${await response.text()}`);
  }

  const result = await response.json();
  const data = result.data || result;

  return {
    uploadId: data.upload_id,
    partSize: data.part_size,
    totalParts: data.total_parts,
    uploadedParts: data.uploaded_parts || [],
    presignedUrls: data.presigned_urls
  };
}

private async uploadPart(
  presignedUrl: string,
  partData: Buffer,
  maxRetries: number = 3
): Promise<void> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(presignedUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/octet-stream'
        },
        body: partData
      });

      if (response.ok) {
        return;
      }

      if (attempt === maxRetries - 1) {
        throw new APIError(`上传分片失败,已重试 ${maxRetries} 次`);
      }
    } catch (error) {
      if (attempt === maxRetries - 1) {
        throw new APIError(`上传分片失败: ${error.message}`);
      }
      // 指数退避
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
    }
  }
}

private async getUploadUrl(uploadId: string): Promise<string> {
  const endpoint = `${this.uploadBaseUrl}/${uploadId}/url`;
  const response = await fetch(endpoint, {
    headers: {
      'Authorization': `Bearer ${this.apiKey}`
    }
  });

  if (!response.ok) {
    throw new APIError(`HTTP ${response.status}: ${await response.text()}`);
  }

  const result = await response.json();
  const data = result.data || result;
  return data.url;
}
```

## 3. 批处理 API

### 3.1 创建批次

#### Python 实现

```python
from pdf_craft_sdk import PDFCraftClient, FormatType

batch = client.create_batch(
    files=[
        {"url": "cache://abc.pdf", "fileName": "document.pdf"},
        {"url": "cache://def.pdf", "fileName": "report.pdf"}
    ],
    output_format=FormatType.MARKDOWN,
    includes_footnotes=False
)
print(f"批次 ID: {batch.batch_id}")
```

#### TypeScript 实现

```typescript
interface BatchFile {
  url: string;
  fileName: string;
  fileSize?: number;
}

interface CreateBatchResponse {
  batchId: string;
  totalFiles: number;
  status: string;
  outputFormat: string;
  createdAt: string;
}

async createBatch(
  files: BatchFile[],
  outputFormat: FormatType | string = FormatType.MARKDOWN,
  includesFootnotes: boolean = false
): Promise<CreateBatchResponse> {
  const endpoint = `${this.batchBaseUrl}/batches`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`
    },
    body: JSON.stringify({
      files,
      outputFormat: this.ensureFormatType(outputFormat),
      includesFootnotes
    })
  });

  if (!response.ok) {
    throw new APIError(`HTTP ${response.status}: ${await response.text()}`);
  }

  const result = await response.json();
  const data = result.data || result;

  return {
    batchId: data.batchId,
    totalFiles: data.totalFiles,
    status: data.status,
    outputFormat: data.outputFormat,
    createdAt: data.createdAt
  };
}
```

### 3.2 批次操作

#### Python 实现

```python
# 启动批次
result = client.start_batch("019aa097-f28d-7000-8d56-6a2987a7b144")
print(f"已排队任务: {result.queued_jobs}")

# 获取批次详情
batch = client.get_batch("019aa097-f28d-7000-8d56-6a2987a7b144")
print(f"进度: {batch.progress}%")

# 获取批次任务
jobs = client.get_batch_jobs("019aa097-f28d-7000-8d56-6a2987a7b144", status="failed")
print(f"失败任务: {len(jobs.jobs)}")

# 暂停/恢复/取消批次
client.pause_batch(batch_id)
client.resume_batch(batch_id)
client.cancel_batch(batch_id)

# 重试失败任务
result = client.retry_failed_jobs(batch_id)
print(f"已重试任务: {result.retried_jobs}")

# 获取并发状态
status = client.get_concurrent_status()
print(f"可以提交新任务: {status.can_submit_new_job}")
```

#### TypeScript 实现

```typescript
interface OperationResponse {
  batchId?: string;
  jobId?: string;
  queuedJobs?: number;
  pausedJobs?: number;
  resumedJobs?: number;
  cancelledJobs?: number;
  retriedJobs?: number;
  status?: string;
}

interface BatchDetail {
  id: string;
  userId: string;
  status: string;
  outputFormat: string;
  includesFootnotes: boolean;
  totalFiles: number;
  completedFiles: number;
  failedFiles: number;
  progress: number;
  createdAt: string;
  updatedAt: string;
}

interface JobDetail {
  id: string;
  batchId: string;
  userId: string;
  outputFormat: string;
  sourceUrl: string;
  fileName: string;
  fileSize?: number;
  status: string;
  resultUrl?: string;
  errorMessage?: string;
  progress?: number;
  retryCount?: number;
  taskId?: string;
  startedAt?: string;
  completedAt?: string;
  createdAt: string;
  updatedAt: string;
}

interface GetJobsResponse {
  jobs: JobDetail[];
  pagination: Pagination;
}

interface ConcurrentStatus {
  maxConcurrentJobs: number;
  currentRunningJobs: number;
  canSubmitNewJob: boolean;
  availableSlots?: number;
  queuedJobs?: number;
}

async startBatch(batchId: string): Promise<OperationResponse> {
  return await this.batchOperation(`/batches/${batchId}/start`);
}

async getBatch(batchId: string): Promise<BatchDetail> {
  const endpoint = `${this.batchBaseUrl}/batches/${batchId}`;
  const response = await fetch(endpoint, {
    headers: { 'Authorization': `Bearer ${this.apiKey}` }
  });

  if (!response.ok) {
    throw new APIError(`HTTP ${response.status}: ${await response.text()}`);
  }

  const result = await response.json();
  return result.data || result;
}

async getBatchJobs(
  batchId: string,
  page: number = 1,
  pageSize: number = 20,
  status?: string
): Promise<GetJobsResponse> {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: String(pageSize)
  });
  if (status) params.set('status', status);

  const endpoint = `${this.batchBaseUrl}/batches/${batchId}/jobs?${params}`;
  const response = await fetch(endpoint, {
    headers: { 'Authorization': `Bearer ${this.apiKey}` }
  });

  if (!response.ok) {
    throw new APIError(`HTTP ${response.status}: ${await response.text()}`);
  }

  const result = await response.json();
  const data = result.data || result;

  return {
    jobs: data.jobs,
    pagination: data.pagination
  };
}

async pauseBatch(batchId: string): Promise<OperationResponse> {
  return await this.batchOperation(`/batches/${batchId}/pause`);
}

async resumeBatch(batchId: string): Promise<OperationResponse> {
  return await this.batchOperation(`/batches/${batchId}/resume`);
}

async cancelBatch(batchId: string): Promise<OperationResponse> {
  return await this.batchOperation(`/batches/${batchId}/cancel`);
}

async retryFailedJobs(batchId: string): Promise<OperationResponse> {
  return await this.batchOperation(`/batches/${batchId}/retry-failed?force=true`);
}

async retryJob(jobId: string): Promise<OperationResponse> {
  return await this.batchOperation(`/jobs/${jobId}/retry?force=true`);
}

async cancelJob(jobId: string): Promise<OperationResponse> {
  return await this.batchOperation(`/jobs/${jobId}/cancel`);
}

async getConcurrentStatus(): Promise<ConcurrentStatus> {
  const endpoint = `${this.batchBaseUrl}/concurrent-status`;
  const response = await fetch(endpoint, {
    headers: { 'Authorization': `Bearer ${this.apiKey}` }
  });

  if (!response.ok) {
    throw new APIError(`HTTP ${response.status}: ${await response.text()}`);
  }

  const result = await response.json();
  const data = result.data || result;

  return {
    maxConcurrentJobs: data.maxConcurrentJobs,
    currentRunningJobs: data.currentRunningJobs,
    canSubmitNewJob: data.canStartNew ?? data.canSubmitNewJob ?? false,
    availableSlots: data.availableSlots,
    queuedJobs: data.queuedJobs
  };
}

private async batchOperation(path: string): Promise<OperationResponse> {
  const endpoint = `${this.batchBaseUrl}${path}`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${this.apiKey}` }
  });

  if (!response.ok) {
    throw new APIError(`HTTP ${response.status}: ${await response.text()}`);
  }

  const result = await response.json();
  return result.data || result;
}
```

## 4. 类型定义

### 枚举

#### Python 实现

```python
from enum import Enum

class FormatType(str, Enum):
    MARKDOWN = "markdown"
    EPUB = "epub"

class PollingStrategy(Enum):
    FIXED = 1.0
    EXPONENTIAL = 1.5
    AGGRESSIVE = 2.0

class BatchStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

#### TypeScript 实现

```typescript
export enum FormatType {
  MARKDOWN = 'markdown',
  EPUB = 'epub'
}

export enum PollingStrategy {
  FIXED = 1.0,
  EXPONENTIAL = 1.5,
  AGGRESSIVE = 2.0
}

export enum BatchStatus {
  DRAFT = 'draft',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  PAUSED = 'paused'
}

export enum JobStatus {
  PENDING = 'pending',
  QUEUED = 'queued',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}
```

### 其他类型

```typescript
interface Pagination {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

interface GetBatchesResponse {
  batches: BatchDetail[];
  pagination: Pagination;
}
```

## 5. 错误处理

### Python 实现

```python
from pdf_craft_sdk.exceptions import APIError, TimeoutError

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

### TypeScript 实现

```typescript
class APIError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'APIError';
  }
}

class TimeoutError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TimeoutError';
  }
}

// 使用
try {
  const downloadUrl = await client.convertLocalPdf('document.pdf');
  console.log(`成功: ${downloadUrl}`);
} catch (error) {
  if (error.code === 'ENOENT') {
    console.log('文件未找到!');
  } else if (error instanceof APIError) {
    console.log(`API 错误: ${error.message}`);
  } else if (error instanceof TimeoutError) {
    console.log('转换超时');
  }
}
```

## 6. API 示例

### 完整使用示例

```typescript
import {
  PDFCraftClient,
  FormatType,
  PollingStrategy,
  UploadProgress
} from 'pdf-craft-sdk';

// 初始化客户端
const client = new PDFCraftClient({ apiKey: 'YOUR_API_KEY' });

// 示例 1: 简单转换
const downloadUrl = await client.convertLocalPdf('document.pdf');

// 示例 2: 带进度追踪
const onProgress = (progress: UploadProgress) => {
  console.log(`上传: ${progress.percentage.toFixed(2)}% ` +
              `(${progress.currentPart}/${progress.totalParts})`);
};

const url = await client.convertLocalPdf('large.pdf', {
  progressCallback: onProgress
});

// 示例 3: 手动分步操作
const cacheUrl = await client.uploadFile('document.pdf', onProgress);
const taskId = await client.submitConversion(cacheUrl, {
  formatType: FormatType.MARKDOWN
});
const result = await client.waitForCompletion(taskId);

// 示例 4: 批量处理
const batch = await client.createBatch([
  { url: 'cache://file1.pdf', fileName: 'doc1.pdf' },
  { url: 'cache://file2.pdf', fileName: 'doc2.pdf' }
], FormatType.MARKDOWN);

await client.startBatch(batch.batchId);

// 轮询批次完成状态
const batchDetails = await client.getBatch(batch.batchId);
console.log(`进度: ${batchDetails.progress}%`);

// 获取任务结果
const jobs = await client.getBatchJobs(batch.batchId);
for (const job of jobs.jobs) {
  if (job.status === 'completed') {
    console.log(`${job.fileName}: ${job.resultUrl}`);
  }
}
```

## 关键实现要点

1. **异步/等待**: TypeScript 中所有 API 方法都应该是异步的
2. **文件读取**: 根据环境使用 Node.js `fs` 模块或浏览器 File API
3. **流式处理**: 考虑使用流来处理大文件上传
4. **进度追踪**: 实现类似 Python 的回调方法
5. **错误处理**: 用 try-catch 块包装 API 调用
6. **类型安全**: 利用 TypeScript 的类型系统获得更好的 IDE 支持
7. **响应处理**: 始终检查 `data` 包装器和直接响应格式

## 测试建议

1. 测试各种文件大小的文件上传
2. 测试进度回调功能
3. 测试多文件批量操作
4. 测试错误场景(网络故障、无效文件等)
5. 验证并发状态和速率限制
6. 验证重试逻辑中的指数退避

## 其他资源

- Python SDK 仓库: [GitHub 链接]
- API 文档: [API 文档链接]
- TypeScript SDK 仓库: [GitHub 链接]

## 支持

如有问题或疑问,请在 TypeScript SDK 仓库中开启 issue。
