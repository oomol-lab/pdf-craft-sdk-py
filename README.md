# PDF Craft SDK

English | [简体中文](README_ZH.md)

A Python SDK for interacting with the PDF Craft API. It simplifies the process of converting PDFs to Markdown or EPUB by handling authentication, file upload, task submission, and result polling.

## Features

- 🚀 **Easy PDF Conversion**: Convert PDFs to Markdown or EPUB format
- 📤 **Local File Upload**: Upload and convert local PDF files with progress tracking
- 🔄 **Automatic Retry**: Built-in retry mechanism for robust operations
- ⏱️ **Flexible Polling**: Configurable polling strategies for task completion
- 📊 **Progress Tracking**: Monitor upload progress with callbacks
- 🔧 **Type Safe**: Full type hints support

## Installation

You can install the package from PyPI:

```bash
pip install pdf-craft-sdk
```

## Quick Start

### Converting Local PDF Files

The easiest way to convert a local PDF file:

```python
from pdf_craft_sdk import PDFCraftClient

# Initialize the client
client = PDFCraftClient(api_key="YOUR_API_KEY")

# Upload and convert a local PDF file
download_url = client.convert_local_pdf("document.pdf")
print(f"Conversion successful! Download URL: {download_url}")
```

> 💡 **See [examples.py](examples.py) for 10 complete usage examples covering all features!**

### Converting Remote PDF Files

If you already have a PDF URL from the upload API:

```python
from pdf_craft_sdk import PDFCraftClient, FormatType

client = PDFCraftClient(api_key="YOUR_API_KEY")

# Convert a PDF to Markdown and wait for the result
try:
    pdf_url = "https://oomol-file-cache.example.com/your-file.pdf"
    download_url = client.convert(pdf_url, format_type=FormatType.MARKDOWN)
    print(f"Conversion successful! Download URL: {download_url}")
except Exception as e:
    print(f"An error occurred: {e}")
```

### Advanced Usage

## Usage Examples

### Upload with Progress Tracking

Monitor the upload progress of large files:

```python
from pdf_craft_sdk import PDFCraftClient, UploadProgress

def on_progress(progress: UploadProgress):
    print(f"Upload progress: {progress.percentage:.2f}% "
          f"({progress.current_part}/{progress.total_parts} parts)")

client = PDFCraftClient(api_key="YOUR_API_KEY")

# Upload and convert with progress tracking
download_url = client.convert_local_pdf(
    "large_document.pdf",
    progress_callback=on_progress
)
```

### Convert to EPUB Format

```python
from pdf_craft_sdk import PDFCraftClient, FormatType

client = PDFCraftClient(api_key="YOUR_API_KEY")

# Convert to EPUB with footnotes
download_url = client.convert_local_pdf(
    "document.pdf",
    format_type=FormatType.EPUB,
    includes_footnotes=True
)
```

### Manual Upload and Conversion

If you prefer to handle the steps manually or asynchronously:

```python
from pdf_craft_sdk import PDFCraftClient, FormatType

client = PDFCraftClient(api_key="YOUR_API_KEY")

# Step 1: Upload local file
cache_url = client.upload_file("document.pdf")
print(f"Uploaded to: {cache_url}")

# Step 2: Submit conversion task
task_id = client.submit_conversion(cache_url, format_type=FormatType.MARKDOWN)
print(f"Task ID: {task_id}")

# Step 3: Wait for completion
download_url = client.wait_for_completion(task_id)
print(f"Download URL: {download_url}")
```

## Configuration

### Polling Strategies

The `convert` and `wait_for_completion` methods accept optional configuration for polling behavior:

- `max_wait_ms`: Maximum time (in milliseconds) to wait for the conversion. Default is 7200000 (2 hours).
- `check_interval_ms`: Initial polling interval (in milliseconds). Default is 1000 (1 second).
- `max_check_interval_ms`: Maximum polling interval (in milliseconds). Default is 5000 (5 seconds).
- `backoff_factor`: Multiplier for increasing interval after each check, or `PollingStrategy` enum. Default is `PollingStrategy.EXPONENTIAL` (1.5).

Available polling strategies:

- `PollingStrategy.EXPONENTIAL` (1.5): Default. Starts fast, slows down.
- `PollingStrategy.FIXED` (1.0): Polls at a fixed interval.
- `PollingStrategy.AGGRESSIVE` (2.0): Doubles the interval each time.

```python
from pdf_craft_sdk import PollingStrategy

# Example: Stable Polling (Every 3 seconds)
download_url = client.convert(
    pdf_url="https://oomol-file-cache.example.com/your-file.pdf",
    check_interval_ms=3000,
    max_check_interval_ms=3000,
    backoff_factor=PollingStrategy.FIXED
)

# Example: Long Running Task (Start slow, check infrequently)
download_url = client.convert(
    pdf_url="https://oomol-file-cache.example.com/your-file.pdf",
    check_interval_ms=5000,
    max_check_interval_ms=60000,  # 1 minute
    backoff_factor=PollingStrategy.AGGRESSIVE
)
```

## API Reference

### PDFCraftClient

#### Constructor

```python
PDFCraftClient(api_key, base_url=None, upload_base_url=None)
```

Initialize the PDF Craft client.

**Parameters:**

- `api_key` (str): Your API key
- `base_url` (str, optional): Custom API base URL
- `upload_base_url` (str, optional): Custom upload API base URL

#### Methods

##### `convert_local_pdf(file_path, **kwargs)`

Upload and convert a local PDF file in one step.

**Parameters:**

- `file_path` (str): Path to the local PDF file
- `format_type` (str | FormatType): Output format, "markdown" or "epub" (default: "markdown")
- `model` (str): Model to use (default: "gundam")
- `includes_footnotes` (bool): Include footnotes (default: False)
- `ignore_pdf_errors` (bool): Ignore PDF parsing errors (default: True)
- `ignore_ocr_errors` (bool): Ignore OCR errors (default: True)
- `wait` (bool): Wait for completion (default: True)
- `max_wait_ms` (int): Max wait time in milliseconds (default: 7200000)
- `check_interval_ms` (int): Initial polling interval in milliseconds (default: 1000)
- `max_check_interval_ms` (int): Max polling interval in milliseconds (default: 5000)
- `backoff_factor` (float | PollingStrategy): Polling backoff factor (default: PollingStrategy.EXPONENTIAL)
- `progress_callback` (callable): Upload progress callback function
- `upload_max_retries` (int): Max upload retries per part (default: 3)

**Returns:** Download URL (str) if `wait=True`, else task ID (str)

##### `upload_file(file_path, progress_callback=None, max_retries=3)`

Upload a local PDF file to cloud cache.

**Parameters:**

- `file_path` (str): Path to the local PDF file
- `progress_callback` (callable): Progress callback function
- `max_retries` (int): Max retries per upload part (default: 3)

**Returns:** Cache URL (str)

##### `convert(pdf_url, **kwargs)`

Convert a PDF from URL.

**Parameters:**

- `pdf_url` (str): PDF URL to convert (HTTPS URL from upload API)
- `format_type` (str | FormatType): Output format (default: "markdown")
- Other parameters same as `convert_local_pdf`

**Returns:** Download URL (str)

##### `submit_conversion(pdf_url, **kwargs)`

Submit a conversion task without waiting.

**Parameters:**

- `pdf_url` (str): PDF URL to convert
- `format_type` (str | FormatType): Output format
- `model` (str): Model to use
- `includes_footnotes` (bool): Include footnotes
- `ignore_pdf_errors` (bool): Ignore PDF parsing errors
- `ignore_ocr_errors` (bool): Ignore OCR errors

**Returns:** Task ID (str)

##### `wait_for_completion(task_id, **kwargs)`

Wait for a conversion task to complete.

**Parameters:**

- `task_id` (str): Task ID from `submit_conversion`
- Polling parameters same as `convert_local_pdf`

**Returns:** Download URL (str)

### UploadProgress

Progress information for file uploads.

**Attributes:**

- `uploaded_bytes` (int): Bytes uploaded so far
- `total_bytes` (int): Total bytes to upload
- `current_part` (int): Current part number being uploaded
- `total_parts` (int): Total number of parts
- `percentage` (float): Progress percentage (0-100)

**Example:**

```python
def on_progress(progress):
    print(f"{progress.percentage:.1f}% - Part {progress.current_part}/{progress.total_parts}")
```

## Error Handling

The SDK raises the following exceptions:

- `FileNotFoundError`: When the specified file doesn't exist
- `APIError`: When API requests fail
- `TimeoutError`: When conversion exceeds max wait time

**Example:**

```python
from pdf_craft_sdk import PDFCraftClient
from pdf_craft_sdk.exceptions import APIError

client = PDFCraftClient(api_key="YOUR_API_KEY")

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

## Advanced Features

### Custom Upload Endpoint

If you need to use a custom upload API endpoint:

```python
client = PDFCraftClient(
    api_key="YOUR_API_KEY",
    upload_base_url="https://custom.example.com/upload"
)
```

Default upload endpoint: `https://llm.oomol.com/api/tasks/files/remote-cache`

### Batch Processing

Process multiple files:

```python
import os
from pdf_craft_sdk import PDFCraftClient

client = PDFCraftClient(api_key="YOUR_API_KEY")

pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

for pdf_file in pdf_files:
    try:
        print(f"Processing {pdf_file}...")
        download_url = client.convert_local_pdf(pdf_file, wait=False)
        print(f"Task submitted: {download_url}")
    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")
```

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit our [GitHub repository](https://github.com/your-repo/pdf-craft-sdk).

## Complete Examples

See [examples.py](examples.py) for complete, runnable examples including:

1. ✅ Basic local PDF conversion
2. 📊 Upload with progress tracking
3. 📖 EPUB format conversion
4. 🔧 Manual step-by-step upload and conversion
5. 🌐 Remote PDF conversion
6. ⚙️ Custom polling strategies
7. 🛡️ Proper error handling
8. 📦 Batch processing multiple files
9. 🔌 Custom upload endpoint
10. ⏱️ Async workflow (submit now, check later)

Run examples:

```bash
# Get your API key from https://console.oomol.com/api-key
# Then edit examples.py and replace 'your_api_key_here' with your actual API key

# Run examples
python examples.py

# Choose a specific example (1-10) or 'all' to run all examples
```

## Changelog

### Version 0.4.0

- ✨ Added local file upload functionality
- ✨ Added `convert_local_pdf()` convenience method
- ✨ Added upload progress tracking with callbacks
- 🐛 Fixed null `uploaded_parts` handling in upload response
- 📝 Improved documentation and examples

### Version 0.3.0

- Initial public release
- Basic PDF to Markdown/EPUB conversion
- Configurable polling strategies
