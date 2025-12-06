import time
import requests
from typing import Optional, Dict, Any, Union
from .exceptions import APIError, TimeoutError
from .enums import FormatType

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

    def submit_conversion(self, pdf_url: str, format_type: Union[str, FormatType] = FormatType.MARKDOWN, model: str = "gundam") -> str:
        """
        Submit PDF conversion task
        
        Args:
            pdf_url: URL of the PDF file
            format_type: 'markdown' or 'epub' or FormatType
            model: Model to use, default is 'gundam'
            
        Returns:
            sessionID (str): The ID of the submitted task
        """
        format_type_str = self._ensure_format_type(format_type)
            
        endpoint = f"{self.base_url}/pdf-transform-{format_type_str}/submit"
        data = {
            "pdfURL": pdf_url,
            "model": model
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
            return response.json()
        except ValueError:
             raise APIError(f"Invalid JSON response: {response.text}")

    def wait_for_completion(self, task_id: str, format_type: Union[str, FormatType] = FormatType.MARKDOWN, max_wait: int = 300, check_interval: int = 5) -> str:
        """
        Poll until conversion completes
        
        Args:
            task_id: The sessionID of the task
            format_type: 'markdown' or 'epub' or FormatType
            max_wait: Maximum wait time in seconds
            check_interval: Interval between checks in seconds
            
        Returns:
            download_url (str): The URL to download the result
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
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
            
            time.sleep(check_interval)

        raise TimeoutError("Conversion timeout")

    def convert(self, pdf_url: str, format_type: Union[str, FormatType] = FormatType.MARKDOWN, model: str = "gundam", wait: bool = True, max_wait: int = 300) -> Union[str, Dict[str, Any]]:
        """
        High-level method to convert PDF.
        
        If wait is True (default), submits and waits for completion, returning the download URL.
        If wait is False, submits and returns the task ID.
        """
        task_id = self.submit_conversion(pdf_url, format_type, model)
        
        if wait:
            return self.wait_for_completion(task_id, format_type, max_wait)
        else:
            return task_id
