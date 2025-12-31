# PDF Craft SDK - TypeScript Migration Guide

English | [简体中文](MIGRATION_GUIDE_ZH.md)

This guide helps TypeScript SDK developers implement equivalent features based on the Python SDK's latest updates.

## Table of Contents

- [Overview](#overview)
- [Core Changes](#core-changes)
- [1. Client Initialization](#1-client-initialization)
- [2. File Upload Functionality](#2-file-upload-functionality)
- [3. Batch Processing API](#3-batch-processing-api)
- [4. Type Definitions](#4-type-definitions)
- [5. Error Handling](#5-error-handling)
- [6. API Examples](#6-api-examples)

## Overview

The Python SDK has been updated to version 0.4.0+ with the following major features:

1. **Local File Upload**: Support for uploading local PDF files with progress tracking
2. **Batch Processing**: API for creating and managing batch conversion jobs
3. **Enhanced Type Safety**: Comprehensive type definitions and enums
4. **Improved Error Handling**: Better exception handling and HTTP status checks

## Core Changes

### New Base URLs

The client now supports three configurable base URLs:

```python
# Python
client = PDFCraftClient(
    api_key="YOUR_API_KEY",
    base_url="https://fusion-api.oomol.com/v1",  # Conversion API
    batch_base_url="https://pdf-server.oomol.com/api/v1/conversion",  # Batch API
    upload_base_url="https://llm.oomol.com/api/tasks/files/remote-cache"  # Upload API
)
```

```typescript
// TypeScript Implementation
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

## 1. Client Initialization

### Python Implementation

```python
from pdf_craft_sdk import PDFCraftClient

# Basic initialization
client = PDFCraftClient(api_key="YOUR_API_KEY")

# With custom endpoints
client = PDFCraftClient(
    api_key="YOUR_API_KEY",
    base_url="https://custom.api.com/v1",
    upload_base_url="https://custom.upload.com"
)
```

### TypeScript Implementation

```typescript
import { PDFCraftClient } from 'pdf-craft-sdk';

// Basic initialization
const client = new PDFCraftClient({ apiKey: 'YOUR_API_KEY' });

// With custom endpoints
const client = new PDFCraftClient({
  apiKey: 'YOUR_API_KEY',
  baseUrl: 'https://custom.api.com/v1',
  uploadBaseUrl: 'https://custom.upload.com'
});
```

## 2. File Upload Functionality

### 2.1 Upload Progress Tracking

#### Python Implementation

```python
from pdf_craft_sdk import PDFCraftClient, UploadProgress

def on_progress(progress: UploadProgress):
    print(f"Upload progress: {progress.percentage:.2f}% "
          f"({progress.current_part}/{progress.total_parts} parts)")

client = PDFCraftClient(api_key="YOUR_API_KEY")

# Upload file with progress tracking
cache_url = client.upload_file(
    "document.pdf",
    progress_callback=on_progress,
    max_retries=3
)
```

#### TypeScript Implementation

```typescript
interface UploadProgress {
  uploadedBytes: number;
  totalBytes: number;
  currentPart: number;
  totalParts: number;
  percentage: number;
}

type ProgressCallback = (progress: UploadProgress) => void;

// In PDFCraftClient class
async uploadFile(
  filePath: string,
  progressCallback?: ProgressCallback,
  maxRetries: number = 3
): Promise<string> {
  // Implementation
  const fileSize = await fs.stat(filePath).then(stats => stats.size);
  const fileExtension = path.extname(filePath);

  // Initialize upload
  const initResponse = await this.initUpload(fileSize, fileExtension);

  // Upload parts with progress
  let uploadedBytes = 0;
  const fileStream = fs.createReadStream(filePath, {
    highWaterMark: initResponse.partSize
  });

  for (let partNumber = 1; partNumber <= initResponse.totalParts; partNumber++) {
    // Skip already uploaded parts
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

  // Get final URL
  return await this.getUploadUrl(initResponse.uploadId);
}
```

### 2.2 Convert Local PDF

#### Python Implementation

```python
# Simple one-line conversion
download_url = client.convert_local_pdf("document.pdf")

# With options
download_url = client.convert_local_pdf(
    "document.pdf",
    format_type=FormatType.EPUB,
    includes_footnotes=True,
    progress_callback=on_progress
)
```

#### TypeScript Implementation

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
  // Upload file first
  const cacheUrl = await this.uploadFile(
    filePath,
    options?.progressCallback,
    options?.uploadMaxRetries ?? 3
  );

  // Convert
  return await this.convert(cacheUrl, options);
}
```

### 2.3 Internal Upload Methods

#### Python Implementation

```python
# Initialize upload
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

# Upload part with retry
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
            time.sleep(2 ** attempt)  # Exponential backoff

# Get upload URL
def _get_upload_url(self, upload_id: str) -> str:
    endpoint = f"{self.upload_base_url}/{upload_id}/url"
    response = requests.get(endpoint, headers=self.headers)
    result = response.json()
    data_result = result.get("data", result)
    return data_result["url"]
```

#### TypeScript Implementation

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
        throw new APIError(`Failed to upload part after ${maxRetries} attempts`);
      }
    } catch (error) {
      if (attempt === maxRetries - 1) {
        throw new APIError(`Failed to upload part: ${error.message}`);
      }
      // Exponential backoff
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

## 3. Batch Processing API

### 3.1 Create Batch

#### Python Implementation

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
print(f"Batch ID: {batch.batch_id}")
```

#### TypeScript Implementation

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

### 3.2 Batch Operations

#### Python Implementation

```python
# Start batch
result = client.start_batch("019aa097-f28d-7000-8d56-6a2987a7b144")
print(f"Queued jobs: {result.queued_jobs}")

# Get batch details
batch = client.get_batch("019aa097-f28d-7000-8d56-6a2987a7b144")
print(f"Progress: {batch.progress}%")

# Get batch jobs
jobs = client.get_batch_jobs("019aa097-f28d-7000-8d56-6a2987a7b144", status="failed")
print(f"Failed jobs: {len(jobs.jobs)}")

# Pause/Resume/Cancel batch
client.pause_batch(batch_id)
client.resume_batch(batch_id)
client.cancel_batch(batch_id)

# Retry failed jobs
result = client.retry_failed_jobs(batch_id)
print(f"Retried jobs: {result.retried_jobs}")

# Get concurrent status
status = client.get_concurrent_status()
print(f"Can submit new: {status.can_submit_new_job}")
```

#### TypeScript Implementation

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

## 4. Type Definitions

### Enums

#### Python Implementation

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

#### TypeScript Implementation

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

### Additional Types

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

## 5. Error Handling

### Python Implementation

```python
from pdf_craft_sdk.exceptions import APIError, TimeoutError

try:
    download_url = client.convert_local_pdf("document.pdf")
    print(f"Success: {download_url}")
except FileNotFoundError:
    print("File not found!")
except APIError as e:
    print(f"API error: {e}")
except TimeoutError:
    print("Conversion timed out")
```

### TypeScript Implementation

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

// Usage
try {
  const downloadUrl = await client.convertLocalPdf('document.pdf');
  console.log(`Success: ${downloadUrl}`);
} catch (error) {
  if (error.code === 'ENOENT') {
    console.log('File not found!');
  } else if (error instanceof APIError) {
    console.log(`API error: ${error.message}`);
  } else if (error instanceof TimeoutError) {
    console.log('Conversion timed out');
  }
}
```

## 6. API Examples

### Complete Usage Example

```typescript
import {
  PDFCraftClient,
  FormatType,
  PollingStrategy,
  UploadProgress
} from 'pdf-craft-sdk';

// Initialize client
const client = new PDFCraftClient({ apiKey: 'YOUR_API_KEY' });

// Example 1: Simple conversion
const downloadUrl = await client.convertLocalPdf('document.pdf');

// Example 2: With progress tracking
const onProgress = (progress: UploadProgress) => {
  console.log(`Upload: ${progress.percentage.toFixed(2)}% ` +
              `(${progress.currentPart}/${progress.totalParts})`);
};

const url = await client.convertLocalPdf('large.pdf', {
  progressCallback: onProgress
});

// Example 3: Manual steps
const cacheUrl = await client.uploadFile('document.pdf', onProgress);
const taskId = await client.submitConversion(cacheUrl, {
  formatType: FormatType.MARKDOWN
});
const result = await client.waitForCompletion(taskId);

// Example 4: Batch processing
const batch = await client.createBatch([
  { url: 'cache://file1.pdf', fileName: 'doc1.pdf' },
  { url: 'cache://file2.pdf', fileName: 'doc2.pdf' }
], FormatType.MARKDOWN);

await client.startBatch(batch.batchId);

// Poll for batch completion
const batchDetails = await client.getBatch(batch.batchId);
console.log(`Progress: ${batchDetails.progress}%`);

// Get job results
const jobs = await client.getBatchJobs(batch.batchId);
for (const job of jobs.jobs) {
  if (job.status === 'completed') {
    console.log(`${job.fileName}: ${job.resultUrl}`);
  }
}
```

## Key Implementation Notes

1. **Async/Await**: All API methods should be async in TypeScript
2. **File Reading**: Use Node.js `fs` module or browser File API depending on environment
3. **Streaming**: Consider using streams for large file uploads
4. **Progress Tracking**: Implement callbacks similar to Python's approach
5. **Error Handling**: Wrap API calls in try-catch blocks
6. **Type Safety**: Leverage TypeScript's type system for better IDE support
7. **Response Handling**: Always check for both `data` wrapper and direct response format

## Testing Recommendations

1. Test file upload with various file sizes
2. Test progress callback functionality
3. Test batch operations with multiple files
4. Test error scenarios (network failures, invalid files, etc.)
5. Test concurrent status and rate limiting
6. Verify exponential backoff in retry logic

## Additional Resources

- Python SDK Repository: [GitHub Link]
- API Documentation: [API Docs Link]
- TypeScript SDK Repository: [GitHub Link]

## Support

For questions or issues, please open an issue on the TypeScript SDK repository.
