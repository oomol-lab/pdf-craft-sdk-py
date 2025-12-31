import time
import os
import requests
from typing import Optional, Dict, Any, Union, List, BinaryIO
from .exceptions import APIError, TimeoutError
from .enums import FormatType, PollingStrategy, BatchStatus, JobStatus
from .batch_types import (
    BatchFile, CreateBatchResponse, BatchDetail, JobDetail,
    GetBatchesResponse, GetJobsResponse, ConcurrentStatus, OperationResponse, Pagination
)
from .upload_types import InitUploadResponse, GetUploadUrlResponse, UploadProgress, ProgressCallback

class PDFCraftClient:
    def __init__(self, api_key: str, base_url: str = "https://fusion-api.oomol.com/v1", batch_base_url: Optional[str] = None, upload_base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        # 批处理 API 基础 URL，默认使用 https://pdf-server.oomol.com/api/v1/conversion
        self.batch_base_url = (batch_base_url or "https://pdf-server.oomol.com/api/v1/conversion").rstrip('/')
        # 上传 API 基础 URL，默认使用 https://llm.oomol.com/api/tasks/files/remote-cache
        self.upload_base_url = (upload_base_url or "https://llm.oomol.com/api/tasks/files/remote-cache").rstrip('/')
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

    # ==================== 批处理 API 方法 ====================

    def create_batch(
        self,
        files: List[Union[BatchFile, Dict[str, Any]]],
        output_format: Union[str, FormatType] = FormatType.MARKDOWN,
        includes_footnotes: bool = False
    ) -> CreateBatchResponse:
        """
        创建批次

        Args:
            files: 待转换的文件列表，每个元素可以是 BatchFile 对象或包含 url 和 fileName 的字典
            output_format: 输出格式（默认 "markdown"）
            includes_footnotes: 是否包含脚注引用（默认 False）

        Returns:
            CreateBatchResponse: 批次信息

        Example:
            ```python
            batch = client.create_batch(
                files=[
                    {"url": "cache://abc.pdf", "fileName": "document.pdf"}
                ],
                output_format="markdown",
                includes_footnotes=False
            )
            print("Batch ID:", batch.batch_id)
            ```
        """
        format_type_str = self._ensure_format_type(output_format)

        # 转换文件列表为字典格式
        files_data = []
        for file in files:
            if isinstance(file, BatchFile):
                file_dict = {
                    "url": file.url,
                    "fileName": file.file_name
                }
                if file.file_size is not None:
                    file_dict["fileSize"] = file.file_size
                files_data.append(file_dict)
            elif isinstance(file, dict):
                files_data.append(file)
            else:
                raise ValueError("Each file must be a BatchFile object or a dictionary")

        endpoint = f"{self.batch_base_url}/batches"
        data = {
            "files": files_data,
            "outputFormat": format_type_str,
            "includesFootnotes": includes_footnotes
        }

        response = requests.post(endpoint, json=data, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return CreateBatchResponse(
            batch_id=data_result["batchId"],
            total_files=data_result["totalFiles"],
            status=data_result["status"],
            output_format=data_result["outputFormat"],
            created_at=data_result["createdAt"]
        )

    def start_batch(self, batch_id: str) -> OperationResponse:
        """
        启动批次处理

        Args:
            batch_id: 批次 ID

        Returns:
            OperationResponse: 操作结果

        Example:
            ```python
            result = client.start_batch("019aa097-f28d-7000-8d56-6a2987a7b144")
            print("Queued jobs:", result.queued_jobs)
            ```
        """
        endpoint = f"{self.batch_base_url}/batches/{batch_id}/start"
        response = requests.post(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return OperationResponse(
            batch_id=data_result.get("batchId"),
            queued_jobs=data_result.get("queuedJobs")
        )

    def get_batch(self, batch_id: str) -> BatchDetail:
        """
        获取批次详情

        Args:
            batch_id: 批次 ID

        Returns:
            BatchDetail: 批次详情

        Example:
            ```python
            batch = client.get_batch("019aa097-f28d-7000-8d56-6a2987a7b144")
            print("Progress:", batch.progress)
            ```
        """
        endpoint = f"{self.batch_base_url}/batches/{batch_id}"
        response = requests.get(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return BatchDetail(
            id=data_result["id"],
            user_id=data_result["userId"],
            status=data_result["status"],
            output_format=data_result["outputFormat"],
            includes_footnotes=data_result["includesFootnotes"],
            total_files=data_result["totalFiles"],
            completed_files=data_result["completedFiles"],
            failed_files=data_result["failedFiles"],
            progress=data_result["progress"],
            created_at=data_result["createdAt"],
            updated_at=data_result["updatedAt"]
        )

    def get_batches(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = "all",
        sort_by: str = "createdAt",
        sort_order: str = "desc"
    ) -> GetBatchesResponse:
        """
        获取用户的批次列表

        Args:
            page: 页码（默认 1）
            page_size: 每页条数（默认 20）
            status: 状态筛选（默认 "all"）
            sort_by: 排序字段（默认 "createdAt"）
            sort_order: 排序方向（默认 "desc"）

        Returns:
            GetBatchesResponse: 批次列表和分页信息

        Example:
            ```python
            result = client.get_batches(page=1, page_size=20, status="all")
            print("Total batches:", result.pagination.total)
            ```
        """
        params = {
            "page": str(page),
            "pageSize": str(page_size),
            "status": status,
            "sortBy": sort_by,
            "sortOrder": sort_order
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        endpoint = f"{self.batch_base_url}/batches?{query_string}"

        response = requests.get(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        pagination = Pagination(
            page=data_result["pagination"]["page"],
            page_size=data_result["pagination"]["pageSize"],
            total=data_result["pagination"]["total"],
            total_pages=data_result["pagination"]["totalPages"]
        )

        return GetBatchesResponse(
            batches=data_result["batches"],
            pagination=pagination
        )

    def get_batch_jobs(
        self,
        batch_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = "all"
    ) -> GetJobsResponse:
        """
        获取批次的任务列表

        Args:
            batch_id: 批次 ID
            page: 页码（默认 1）
            page_size: 每页条数（默认 20）
            status: 状态筛选（默认 "all"）

        Returns:
            GetJobsResponse: 任务列表和分页信息

        Example:
            ```python
            result = client.get_batch_jobs("019aa097-f28d-7000-8d56-6a2987a7b144", status="failed")
            print("Failed jobs:", len(result.jobs))
            ```
        """
        params = {
            "page": str(page),
            "pageSize": str(page_size)
        }
        if status:
            params["status"] = status

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        endpoint = f"{self.batch_base_url}/batches/{batch_id}/jobs?{query_string}"

        response = requests.get(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        jobs = [
            JobDetail(
                id=job["id"],
                batch_id=job["batchId"],
                user_id=job["userId"],
                output_format=job["outputFormat"],
                source_url=job["sourceUrl"],
                file_name=job["fileName"],
                file_size=job.get("fileSize"),
                status=job["status"],
                result_url=job.get("resultUrl"),
                error_message=job.get("errorMessage"),
                progress=job.get("progress"),
                retry_count=job.get("retryCount"),
                task_id=job.get("taskId"),
                started_at=job.get("startedAt"),
                completed_at=job.get("completedAt"),
                created_at=job["createdAt"],
                updated_at=job["updatedAt"]
            )
            for job in data_result["jobs"]
        ]

        pagination = Pagination(
            page=data_result["pagination"]["page"],
            page_size=data_result["pagination"]["pageSize"],
            total=data_result["pagination"]["total"],
            total_pages=data_result["pagination"]["totalPages"]
        )

        return GetJobsResponse(
            jobs=jobs,
            pagination=pagination
        )

    def cancel_batch(self, batch_id: str) -> OperationResponse:
        """
        取消批次

        Args:
            batch_id: 批次 ID

        Returns:
            OperationResponse: 操作结果

        Example:
            ```python
            result = client.cancel_batch("019aa097-f28d-7000-8d56-6a2987a7b144")
            print("Cancelled jobs:", result.cancelled_jobs)
            ```
        """
        endpoint = f"{self.batch_base_url}/batches/{batch_id}/cancel"
        response = requests.post(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return OperationResponse(
            batch_id=data_result.get("batchId"),
            cancelled_jobs=data_result.get("cancelledJobs")
        )

    def pause_batch(self, batch_id: str) -> OperationResponse:
        """
        暂停批次

        Args:
            batch_id: 批次 ID

        Returns:
            OperationResponse: 操作结果

        Example:
            ```python
            result = client.pause_batch("019aa097-f28d-7000-8d56-6a2987a7b144")
            print("Paused jobs:", result.paused_jobs)
            ```
        """
        endpoint = f"{self.batch_base_url}/batches/{batch_id}/pause"
        response = requests.post(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return OperationResponse(
            batch_id=data_result.get("batchId"),
            paused_jobs=data_result.get("pausedJobs")
        )

    def resume_batch(self, batch_id: str) -> OperationResponse:
        """
        恢复批次

        Args:
            batch_id: 批次 ID

        Returns:
            OperationResponse: 操作结果

        Example:
            ```python
            result = client.resume_batch("019aa097-f28d-7000-8d56-6a2987a7b144")
            print("Resumed jobs:", result.resumed_jobs)
            ```
        """
        endpoint = f"{self.batch_base_url}/batches/{batch_id}/resume"
        response = requests.post(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return OperationResponse(
            batch_id=data_result.get("batchId"),
            resumed_jobs=data_result.get("resumedJobs")
        )

    def retry_job(self, job_id: str) -> OperationResponse:
        """
        重试单个失败任务

        Args:
            job_id: 任务 ID

        Returns:
            OperationResponse: 操作结果

        Example:
            ```python
            result = client.retry_job("job-123")
            print("Job status:", result.status)
            ```
        """
        endpoint = f"{self.batch_base_url}/jobs/{job_id}/retry?force=true"
        response = requests.post(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return OperationResponse(
            job_id=data_result.get("jobId"),
            status=data_result.get("status")
        )

    def retry_failed_jobs(self, batch_id: str) -> OperationResponse:
        """
        批量重试批次中的失败任务

        Args:
            batch_id: 批次 ID

        Returns:
            OperationResponse: 操作结果

        Example:
            ```python
            result = client.retry_failed_jobs("019aa097-f28d-7000-8d56-6a2987a7b144")
            print("Retried jobs:", result.retried_jobs)
            ```
        """
        endpoint = f"{self.batch_base_url}/batches/{batch_id}/retry-failed?force=true"
        response = requests.post(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return OperationResponse(
            batch_id=data_result.get("batchId"),
            retried_jobs=data_result.get("retriedJobs")
        )

    def cancel_job(self, job_id: str) -> OperationResponse:
        """
        取消单个任务

        Args:
            job_id: 任务 ID

        Returns:
            OperationResponse: 操作结果

        Example:
            ```python
            result = client.cancel_job("job-123")
            print("Job status:", result.status)
            ```
        """
        endpoint = f"{self.batch_base_url}/jobs/{job_id}/cancel"
        response = requests.post(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return OperationResponse(
            job_id=data_result.get("jobId"),
            status=data_result.get("status")
        )

    def get_concurrent_status(self) -> ConcurrentStatus:
        """
        获取用户并发状态

        Returns:
            ConcurrentStatus: 并发状态信息

        Example:
            ```python
            status = client.get_concurrent_status()
            print("Can submit:", status.can_submit_new_job)
            ```
        """
        endpoint = f"{self.batch_base_url}/concurrent-status"
        response = requests.get(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return ConcurrentStatus(
            max_concurrent_jobs=data_result["maxConcurrentJobs"],
            current_running_jobs=data_result["currentRunningJobs"],
            can_submit_new_job=data_result.get("canStartNew", data_result.get("canSubmitNewJob", False)),
            available_slots=data_result.get("availableSlots"),
            queued_jobs=data_result.get("queuedJobs")
        )

    # ==================== 文件上传 API 方法 ====================

    def _init_upload(self, file_size: int, file_extension: str) -> InitUploadResponse:
        """
        初始化分片上传

        Args:
            file_size: 文件大小（字节）
            file_extension: 文件扩展名（例如 ".pdf"）

        Returns:
            InitUploadResponse: 初始化上传响应
        """
        endpoint = f"{self.upload_base_url}/init"
        data = {
            "file_extension": file_extension,
            "size": file_size
        }

        response = requests.post(endpoint, json=data, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return InitUploadResponse(
            upload_id=data_result["upload_id"],
            part_size=data_result["part_size"],
            total_parts=data_result["total_parts"],
            uploaded_parts=data_result.get("uploaded_parts", []),
            presigned_urls=data_result["presigned_urls"]
        )

    def _upload_part(self, presigned_url: str, part_data: bytes, max_retries: int = 3) -> None:
        """
        上传单个分片

        Args:
            presigned_url: 预签名 URL
            part_data: 分片数据
            max_retries: 最大重试次数（默认 3）

        Raises:
            APIError: 上传失败
        """
        headers = {
            "Content-Type": "application/octet-stream"
        }

        for attempt in range(max_retries):
            try:
                response = requests.put(presigned_url, data=part_data, headers=headers)
                if response.ok:
                    return
                elif attempt == max_retries - 1:
                    raise APIError(f"Failed to upload part after {max_retries} attempts: HTTP {response.status_code}")
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise APIError(f"Failed to upload part after {max_retries} attempts: {str(e)}")
                # 指数退避
                time.sleep(2 ** attempt)

    def _get_upload_url(self, upload_id: str) -> str:
        """
        获取上传文件的最终 URL

        Args:
            upload_id: 上传任务 ID

        Returns:
            str: 文件的云端缓存 URL（例如 "cache://xxx.pdf"）
        """
        endpoint = f"{self.upload_base_url}/{upload_id}/url"
        response = requests.get(endpoint, headers=self.headers)

        try:
            result = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            raise APIError(f"HTTP {response.status_code}: {response.text}")

        # 处理包装在 data 字段中的响应
        data_result = result.get("data", result)

        return data_result["url"]

    def upload_file(self,
                    file_path: str,
                    progress_callback: ProgressCallback = None,
                    max_retries: int = 3) -> str:
        """
        上传 PDF 文件到云端

        Args:
            file_path: 本地 PDF 文件路径
            progress_callback: 进度回调函数，接收 UploadProgress 对象
            max_retries: 每个分片的最大重试次数（默认 3）

        Returns:
            str: 文件的云端缓存 URL（例如 "cache://xxx.pdf"），可用于后续的转换任务

        Raises:
            APIError: 上传失败
            FileNotFoundError: 文件不存在

        Example:
            ```python
            # 无进度回调
            cache_url = client.upload_file("document.pdf")

            # 带进度回调
            def on_progress(progress: UploadProgress):
                print(f"Progress: {progress.percentage:.2f}% ({progress.current_part}/{progress.total_parts})")

            cache_url = client.upload_file("document.pdf", progress_callback=on_progress)
            print(f"Upload complete: {cache_url}")
            ```
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 获取文件信息
        file_size = os.path.getsize(file_path)
        file_extension = os.path.splitext(file_path)[1]
        if not file_extension:
            file_extension = ".pdf"

        # 初始化上传
        init_response = self._init_upload(file_size, file_extension)

        # 上传分片
        uploaded_bytes = 0
        with open(file_path, 'rb') as f:
            for part_number in range(1, init_response.total_parts + 1):
                # 跳过已上传的分片
                if init_response.uploaded_parts and part_number in init_response.uploaded_parts:
                    uploaded_bytes += init_response.part_size
                    continue

                # 读取分片数据
                part_data = f.read(init_response.part_size)
                if not part_data:
                    break

                # 上传分片
                presigned_url = init_response.presigned_urls.get(str(part_number))
                if not presigned_url:
                    raise APIError(f"Missing presigned URL for part {part_number}")

                self._upload_part(presigned_url, part_data, max_retries)

                # 更新进度
                uploaded_bytes += len(part_data)
                if progress_callback:
                    progress = UploadProgress(
                        uploaded_bytes=uploaded_bytes,
                        total_bytes=file_size,
                        current_part=part_number,
                        total_parts=init_response.total_parts
                    )
                    progress_callback(progress)

        # 获取最终 URL
        cache_url = self._get_upload_url(init_response.upload_id)
        return cache_url

    def convert_local_pdf(self,
                         file_path: str,
                         format_type: Union[str, FormatType] = FormatType.MARKDOWN,
                         model: str = "gundam",
                         includes_footnotes: bool = False,
                         ignore_pdf_errors: bool = True,
                         ignore_ocr_errors: bool = True,
                         wait: bool = True,
                         max_wait_ms: int = 7200000,
                         check_interval_ms: int = 1000,
                         max_check_interval_ms: int = 5000,
                         backoff_factor: Union[float, PollingStrategy] = PollingStrategy.EXPONENTIAL,
                         progress_callback: ProgressCallback = None,
                         upload_max_retries: int = 3) -> Union[str, Dict[str, Any]]:
        """
        上传本地 PDF 文件并进行转换（便捷方法）

        Args:
            file_path: 本地 PDF 文件路径
            format_type: 输出格式（'markdown' 或 'epub' 或 FormatType）
            model: 使用的模型，默认是 'gundam'
            includes_footnotes: 是否处理脚注，默认 False
            ignore_pdf_errors: 是否忽略 PDF 解析错误，默认 True
            ignore_ocr_errors: 是否忽略 OCR 识别错误，默认 True
            wait: 是否等待转换完成，默认 True
            max_wait_ms: 最大等待时间（毫秒），默认 2 小时
            check_interval_ms: 初始轮询间隔（毫秒），默认 1000
            max_check_interval_ms: 最大轮询间隔（毫秒），默认 5000
            backoff_factor: 轮询间隔增长因子或 PollingStrategy，默认指数增长
            progress_callback: 上传进度回调函数
            upload_max_retries: 上传分片的最大重试次数，默认 3

        Returns:
            如果 wait 为 True，返回下载 URL (str)
            如果 wait 为 False，返回任务 ID (str)

        Raises:
            FileNotFoundError: 文件不存在
            APIError: 上传或转换失败

        Example:
            ```python
            # 快速转换本地 PDF
            download_url = client.convert_local_pdf("document.pdf")

            # 带上传进度回调
            def on_upload_progress(progress):
                print(f"Uploading: {progress.percentage:.2f}%")

            download_url = client.convert_local_pdf(
                "document.pdf",
                format_type="markdown",
                progress_callback=on_upload_progress
            )
            print(f"Download URL: {download_url}")
            ```
        """
        # 先上传文件
        cache_url = self.upload_file(file_path, progress_callback, upload_max_retries)

        # 然后调用转换
        return self.convert(
            pdf_url=cache_url,
            format_type=format_type,
            model=model,
            includes_footnotes=includes_footnotes,
            ignore_pdf_errors=ignore_pdf_errors,
            ignore_ocr_errors=ignore_ocr_errors,
            wait=wait,
            max_wait_ms=max_wait_ms,
            check_interval_ms=check_interval_ms,
            max_check_interval_ms=max_check_interval_ms,
            backoff_factor=backoff_factor
        )
