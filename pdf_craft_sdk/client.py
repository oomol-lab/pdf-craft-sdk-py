import time
import requests
from typing import Optional, Dict, Any, Union
from .exceptions import APIError, TimeoutError
from .enums import FormatType, PollingStrategy

class PDFCraftClient:
    def __init__(self, api_key: str, base_url: str = "https://fusion-api.oomol.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _ensure_format_type(self, format_type: Union[str, FormatType]) -> str:
        if isinstance(format_type, FormatType):
            return format_type.value
        if format_type not in [t.value for t in FormatType]:
            raise ValueError(f"format_type must be one of {[t.value for t in FormatType]}")
        return format_type

    def submit_conversion(self,
                          pdf_url: str,
                          format_type: Union[str, FormatType] = FormatType.MARKDOWN,
                          model: str = "gundam",
                          includes_footnotes: bool = False,
                          ignore_pdf_errors: bool = True,
                          ignore_ocr_errors: bool = True) -> str:
        """
        Submit PDF conversion task

        Args:
            pdf_url: URL of the PDF file
            format_type: 'markdown' or 'epub' or FormatType
            model: Model to use, default is 'gundam'
            includes_footnotes: Whether to process footnotes, default is False
            ignore_pdf_errors: Whether to ignore PDF parsing errors, default is True
            ignore_ocr_errors: Whether to ignore OCR recognition errors, default is True

        Returns:
            sessionID (str): The ID of the submitted task
        """
        format_type_str = self._ensure_format_type(format_type)

        endpoint = f"{self.base_url}/pdf-transform-{format_type_str}/submit"
        data = {
            "pdfURL": pdf_url,
            "model": model,
            "includesFootnotes": includes_footnotes,
            "ignorePDFErrors": ignore_pdf_errors,
            "ignoreOCRErrors": ignore_ocr_errors
        }

        response = requests.post(endpoint, json=data, headers=self.headers)
        
        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
             raise APIError(f"HTTP {response.status_code}: {response.text}")

        if result.get("success"):
            return result["sessionID"]
        else:
            raise APIError(f"Failed to submit task: {result.get('error', 'Unknown error')}")

    def get_conversion_result(self, task_id: str, format_type: Union[str, FormatType] = FormatType.MARKDOWN) -> Dict[str, Any]:
        """
        Query conversion result

        Args:
            task_id: The sessionID of the task
            format_type: 'markdown' or 'epub' or FormatType

        Returns:
            dict: The result dictionary
        """
        format_type_str = self._ensure_format_type(format_type)
        endpoint = f"{self.base_url}/pdf-transform-{format_type_str}/result/{task_id}"
        response = requests.get(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
             raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        return result

    def wait_for_completion(self, 
                            task_id: str, 
                            format_type: Union[str, FormatType] = FormatType.MARKDOWN, 
                            max_wait_ms: int = 7200000, 
                            check_interval_ms: int = 1000,
                            max_check_interval_ms: int = 5000,
                            backoff_factor: Union[float, PollingStrategy] = PollingStrategy.EXPONENTIAL) -> str:
        """
        Poll until conversion completes
        
        Args:
            task_id: The sessionID of the task
            format_type: 'markdown' or 'epub' or FormatType
            max_wait_ms: Maximum wait time in milliseconds (default 2 hours)
            check_interval_ms: Initial interval in milliseconds (default 1000)
            max_check_interval_ms: Maximum interval in milliseconds (default 5000)
            backoff_factor: Multiplier for increasing interval or PollingStrategy enum (default 1.5)
            
        Returns:
            download_url (str): The URL to download the result
        """
        start_time = time.time()
        timeout_sec = max_wait_ms / 1000.0
        
        # Determine backoff factor value
        if isinstance(backoff_factor, PollingStrategy):
            factor = backoff_factor.value
        else:
            factor = float(backoff_factor)

        current_interval_sec = check_interval_ms / 1000.0
        max_interval_sec = max_check_interval_ms / 1000.0

        while time.time() - start_time < timeout_sec:
            result = self.get_conversion_result(task_id, format_type)

            state = result.get("state")
            if state == "completed":
                # Check if data exists and has downloadURL
                data = result.get("data")
                if data and "downloadURL" in data:
                    return data["downloadURL"]
                else:
                     raise APIError(f"Task completed but downloadURL missing in response: {result}")
            elif state == "failed":
                raise APIError(f"Conversion failed: {result.get('error', 'Unknown error')}")
            
            time.sleep(current_interval_sec)
            
            # Update interval
            current_interval_sec = min(current_interval_sec * factor, max_interval_sec)

        raise TimeoutError("Conversion timeout")

    def convert(self,
                pdf_url: str,
                format_type: Union[str, FormatType] = FormatType.MARKDOWN,
                model: str = "gundam",
                includes_footnotes: bool = False,
                ignore_pdf_errors: bool = True,
                ignore_ocr_errors: bool = True,
                wait: bool = True,
                max_wait_ms: int = 7200000,
                check_interval_ms: int = 1000,
                max_check_interval_ms: int = 5000,
                backoff_factor: Union[float, PollingStrategy] = PollingStrategy.EXPONENTIAL) -> Union[str, Dict[str, Any]]:
        """
        High-level method to convert PDF.

        Args:
            pdf_url: URL of the PDF file
            format_type: 'markdown' or 'epub' or FormatType
            model: Model to use, default is 'gundam'
            includes_footnotes: Whether to process footnotes, default is False
            ignore_pdf_errors: Whether to ignore PDF parsing errors, default is True
            ignore_ocr_errors: Whether to ignore OCR recognition errors, default is True
            wait: Whether to wait for completion, default is True
            max_wait_ms: Maximum wait time in milliseconds (default 2 hours)
            check_interval_ms: Initial interval in milliseconds (default 1000)
            max_check_interval_ms: Maximum interval in milliseconds (default 5000)
            backoff_factor: Multiplier for increasing interval or PollingStrategy enum (default exponential)

        Returns:
            If wait is True, returns download URL (str)
            If wait is False, returns task ID (str)
        """
        task_id = self.submit_conversion(pdf_url, format_type, model, includes_footnotes, ignore_pdf_errors, ignore_ocr_errors)

        if wait:
            return self.wait_for_completion(task_id, format_type, max_wait_ms, check_interval_ms, max_check_interval_ms, backoff_factor)
        else:
            return task_id
