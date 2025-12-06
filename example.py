import os
from pdf_craft_sdk import PDFCraftClient, FormatType

# It is recommended to get the API Key from environment variables, or replace the string below directly
API_KEY = os.getenv("PDF_CRAFT_API_KEY", "YOUR_API_KEY_HERE")
# Example PDF: Attention Is All You Need paper
PDF_URL = "https://arxiv.org/pdf/1706.03762.pdf"

def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please set your API Key first. You can set the environment variable PDF_CRAFT_API_KEY or modify the API_KEY variable in the script directly.")
        return

    # Initialize the client
    client = PDFCraftClient(api_key=API_KEY)

    print(f"Preparing to convert PDF: {PDF_URL}")

    # Example 1: Basic Usage (Synchronous wait) - Convert to Markdown
    print("\n--- Example 1: Basic Usage (Convert to Markdown) ---")
    try:
        # Use FormatType enum to specify format
        print("Starting Markdown conversion (synchronous wait)...")
        markdown_url = client.convert(
            pdf_url=PDF_URL,
            format_type=FormatType.MARKDOWN,
            # Optional: Customize polling
            check_interval_ms=2000,
            backoff_factor=1.2
        )
        print(f"✅ Conversion successful! Markdown Download URL: {markdown_url}")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")

    # Example 2: Advanced Usage (Manual submission and polling) - Convert to EPUB
    print("\n--- Example 2: Advanced Usage (Convert to EPUB) ---")
    try:
        # 1. Submit task
        print("1. Submitting EPUB conversion task...")
        task_id = client.submit_conversion(
            pdf_url=PDF_URL,
            format_type=FormatType.EPUB
        )
        print(f"   Task submitted. Task ID: {task_id}")

        # 2. Wait for result
        print("2. Polling for result...")
        epub_url = client.wait_for_completion(
            task_id=task_id,
            format_type=FormatType.EPUB,
            max_wait_ms=600000  # Set max wait time to 600 seconds (10 mins)
        )
        print(f"✅ Conversion successful! EPUB Download URL: {epub_url}")

    except Exception as e:
        print(f"❌ Error during conversion: {e}")

if __name__ == "__main__":
    main()
