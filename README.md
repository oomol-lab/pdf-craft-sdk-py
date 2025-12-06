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

- `max_wait`: Maximum time (in seconds) to wait for the conversion. Default is 300.
- `model`: The model to use for conversion. Default is "gundam".

```python
# Example with custom timeout and model
download_url = client.convert(
    pdf_url="...", 
    model="gundam", 
    max_wait=600
)
```
