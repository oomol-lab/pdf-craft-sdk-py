#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Craft SDK - Usage Examples
Complete examples demonstrating all major features

Get your API key from: https://console.oomol.com/api-key
"""

from pdf_craft_sdk import PDFCraftClient, FormatType, UploadProgress, PollingStrategy
from pdf_craft_sdk.exceptions import APIError

# Replace with your API key from https://console.oomol.com/api-key
API_KEY = "your_api_key_here"


def example_1_basic_conversion():
    """Example 1: Basic local PDF conversion"""
    print("\n" + "="*60)
    print("Example 1: Basic Local PDF Conversion")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # Simple one-line conversion
    download_url = client.convert_local_pdf("document.pdf")
    print(f"✅ Conversion successful! Download URL: {download_url}")


def example_2_with_progress():
    """Example 2: Upload with progress tracking"""
    print("\n" + "="*60)
    print("Example 2: Upload with Progress Tracking")
    print("="*60)

    def on_progress(progress: UploadProgress):
        print(f"📤 Upload progress: {progress.percentage:.2f}% "
              f"({progress.current_part}/{progress.total_parts} parts)")

    client = PDFCraftClient(api_key=API_KEY)

    download_url = client.convert_local_pdf(
        "large_document.pdf",
        progress_callback=on_progress
    )
    print(f"✅ Download URL: {download_url}")


def example_3_epub_conversion():
    """Example 3: Convert to EPUB format"""
    print("\n" + "="*60)
    print("Example 3: Convert to EPUB Format")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    download_url = client.convert_local_pdf(
        "document.pdf",
        format_type=FormatType.EPUB,
        includes_footnotes=True
    )
    print(f"✅ EPUB file ready: {download_url}")


def example_4_manual_steps():
    """Example 4: Manual upload and conversion (step by step)"""
    print("\n" + "="*60)
    print("Example 4: Manual Upload and Conversion")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # Step 1: Upload file
    print("Step 1: Uploading file...")
    cache_url = client.upload_file("document.pdf")
    print(f"✅ Uploaded to: {cache_url}")

    # Step 2: Submit conversion task
    print("\nStep 2: Submitting conversion task...")
    task_id = client.submit_conversion(cache_url, format_type=FormatType.MARKDOWN)
    print(f"✅ Task ID: {task_id}")

    # Step 3: Wait for completion
    print("\nStep 3: Waiting for completion...")
    download_url = client.wait_for_completion(task_id)
    print(f"✅ Download URL: {download_url}")


def example_5_remote_pdf():
    """Example 5: Convert remote PDF (HTTPS URL)"""
    print("\n" + "="*60)
    print("Example 5: Convert Remote PDF")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # If you already have a HTTPS URL from upload API
    pdf_url = "https://oomol-file-cache.example.com/your-file.pdf"

    download_url = client.convert(pdf_url, format_type=FormatType.MARKDOWN)
    print(f"✅ Download URL: {download_url}")


def example_6_custom_polling():
    """Example 6: Custom polling strategy"""
    print("\n" + "="*60)
    print("Example 6: Custom Polling Strategy")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # Stable polling every 3 seconds
    download_url = client.convert_local_pdf(
        "document.pdf",
        check_interval_ms=3000,
        max_check_interval_ms=3000,
        backoff_factor=PollingStrategy.FIXED
    )
    print(f"✅ Download URL: {download_url}")

    # For long-running tasks
    download_url = client.convert_local_pdf(
        "large_document.pdf",
        check_interval_ms=5000,
        max_check_interval_ms=60000,  # 1 minute
        backoff_factor=PollingStrategy.AGGRESSIVE
    )
    print(f"✅ Download URL: {download_url}")


def example_7_error_handling():
    """Example 7: Proper error handling"""
    print("\n" + "="*60)
    print("Example 7: Error Handling")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    try:
        download_url = client.convert_local_pdf("document.pdf")
        print(f"✅ Success: {download_url}")
    except FileNotFoundError:
        print("❌ File not found!")
    except APIError as e:
        print(f"❌ API error: {e}")
    except TimeoutError:
        print("❌ Conversion timed out")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_8_batch_processing():
    """Example 8: Batch processing multiple files"""
    print("\n" + "="*60)
    print("Example 8: Batch Processing")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

    # Submit all tasks without waiting
    task_ids = []
    for pdf_file in pdf_files:
        try:
            print(f"📄 Processing {pdf_file}...")
            task_id = client.convert_local_pdf(pdf_file, wait=False)
            task_ids.append((pdf_file, task_id))
            print(f"✅ Task submitted: {task_id}")
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {e}")

    # Wait for all tasks to complete
    print("\n⏳ Waiting for all tasks to complete...")
    for pdf_file, task_id in task_ids:
        try:
            download_url = client.wait_for_completion(task_id)
            print(f"✅ {pdf_file}: {download_url}")
        except Exception as e:
            print(f"❌ {pdf_file} failed: {e}")


def example_9_custom_endpoint():
    """Example 9: Using custom upload endpoint"""
    print("\n" + "="*60)
    print("Example 9: Custom Upload Endpoint")
    print("="*60)

    client = PDFCraftClient(
        api_key=API_KEY,
        upload_base_url="https://custom.example.com/upload"
    )

    download_url = client.convert_local_pdf("document.pdf")
    print(f"✅ Download URL: {download_url}")


def example_10_async_workflow():
    """Example 10: Async workflow (submit now, check later)"""
    print("\n" + "="*60)
    print("Example 10: Async Workflow")
    print("="*60)

    client = PDFCraftClient(api_key=API_KEY)

    # Submit and get task ID immediately
    task_id = client.convert_local_pdf("document.pdf", wait=False)
    print(f"✅ Task submitted: {task_id}")
    print("💡 You can now do other work...")

    # Later, check the result
    print("\n⏳ Checking result...")
    download_url = client.wait_for_completion(task_id)
    print(f"✅ Download URL: {download_url}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("PDF Craft SDK - Complete Usage Examples")
    print("="*60)

    # Check API key
    if API_KEY == "your_api_key_here":
        print("\n❌ Error: Please set your API key in the script")
        print("   Get your API key from: https://console.oomol.com/api-key")
        print("   Then replace 'your_api_key_here' with your actual API key")
        return

    examples = [
        ("Basic Conversion", example_1_basic_conversion),
        ("Progress Tracking", example_2_with_progress),
        ("EPUB Conversion", example_3_epub_conversion),
        ("Manual Steps", example_4_manual_steps),
        ("Remote PDF", example_5_remote_pdf),
        ("Custom Polling", example_6_custom_polling),
        ("Error Handling", example_7_error_handling),
        ("Batch Processing", example_8_batch_processing),
        ("Custom Endpoint", example_9_custom_endpoint),
        ("Async Workflow", example_10_async_workflow),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n" + "="*60)
    choice = input("\nEnter example number (1-10) or 'all' to run all: ").strip().lower()

    if choice == 'all':
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n❌ Example failed: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        try:
            examples[int(choice) - 1][1]()
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
    else:
        print("❌ Invalid choice")

    print("\n" + "="*60)
    print("Done!")
    print("="*60)


if __name__ == "__main__":
    main()
