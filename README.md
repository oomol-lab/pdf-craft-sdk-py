# PDF Craft SDK

A Python SDK for interacting with the PDF Craft API. It simplifies the process of converting PDFs to Markdown or EPUB by handling authentication, task submission, and result polling.

## Installation

You can install the package from PyPI:

```bash
pip install pdf-craft-sdk
```

## Usage

### Basic Usage

The SDK provides a high-level `convert` method that handles everything for you (submission + polling).

```python
from pdf_craft_sdk import PDFCraftClient, FormatType

# Initialize the client
client = PDFCraftClient(api_key="YOUR_API_KEY")

# Convert a PDF to Markdown and wait for the result
try:
    pdf_url = "cache://your-pdf-file.pdf"
    download_url = client.convert(pdf_url, format_type=FormatType.MARKDOWN)
    print(f"Conversion successful! Download URL: {download_url}")
except Exception as e:
    print(f"An error occurred: {e}")
```

### Advanced Usage

If you prefer to handle the steps manually or asynchronously:

```python
from pdf_craft_sdk import PDFCraftClient, FormatType

client = PDFCraftClient(api_key="YOUR_API_KEY")

# 1. Submit task
task_id = client.submit_conversion(
    pdf_url="cache://your-pdf-file.pdf",
    format_type=FormatType.MARKDOWN
)
print(f"Task submitted. ID: {task_id}")

# 2. Wait for completion explicitly
try:
    download_url = client.wait_for_completion(task_id, format_type=FormatType.MARKDOWN)
    print(f"Download URL: {download_url}")
except Exception as e:
    print(f"Conversion failed or timed out: {e}")
```

### Configuration

The `convert` and `wait_for_completion` methods accept optional configuration for polling behavior:

- `max_wait_ms`: Maximum time (in milliseconds) to wait for the conversion. Default is 7200000 (2 hours).
- `check_interval_ms`: Initial polling interval (in milliseconds). Default is 1000 (1 second).
- `max_check_interval_ms`: Maximum polling interval (in milliseconds). Default is 5000 (5 seconds).
- `backoff_factor`: Multiplier for increasing interval after each check, or `PollingStrategy` enum. Default is `PollingStrategy.EXPONENTIAL` (1.5).

#### Polling Strategies

You can use `PollingStrategy` enum for `backoff_factor`:

- `PollingStrategy.EXPONENTIAL` (1.5): Default. Starts fast, slows down.
- `PollingStrategy.FIXED` (1.0): Polls at a fixed interval.
- `PollingStrategy.AGGRESSIVE` (2.0): Doubles the interval each time.

```python
from pdf_craft_sdk import PollingStrategy

# Example: Stable Polling (Every 3 seconds)
download_url = client.convert(
    pdf_url="...", 
    check_interval_ms=3000,
    max_check_interval_ms=3000,
    backoff_factor=PollingStrategy.FIXED
)

# Example: Long Running Task (Start slow, check infrequently)
download_url = client.convert(
    pdf_url="...", 
    check_interval_ms=5000,
    max_check_interval_ms=60000, # 1 minute
    backoff_factor=2.0 # or PollingStrategy.AGGRESSIVE
)
```
