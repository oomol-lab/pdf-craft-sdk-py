"""批处理相关的数据类型定义"""
from typing import Optional, List
from dataclasses import dataclass
from .enums import BatchStatus, JobStatus, FormatType


@dataclass
class BatchFile:
    """批次文件信息"""
    url: str
    """PDF 文件的云端 URL"""

    file_name: str
    """文件名"""

    file_size: Optional[int] = None
    """文件大小（字节）"""


@dataclass
class CreateBatchResponse:
    """创建批次响应"""
    batch_id: str
    """批次 ID"""

    total_files: int
    """总文件数"""

    status: str
    """批次状态"""

    output_format: str
    """输出格式"""

    created_at: str
    """创建时间"""


@dataclass
class BatchDetail:
    """批次详情"""
    id: str
    """批次 ID"""

    user_id: str
    """用户 ID"""

    status: str
    """批次状态"""

    output_format: str
    """输出格式"""

    includes_footnotes: bool
    """是否包含脚注引用"""

    total_files: int
    """总文件数"""

    completed_files: int
    """已完成文件数"""

    failed_files: int
    """失败文件数"""

    progress: int
    """进度百分比 (0-100)"""

    created_at: str
    """创建时间"""

    updated_at: str
    """更新时间"""


@dataclass
class JobDetail:
    """任务详情"""
    id: str
    """任务 ID"""

    batch_id: str
    """批次 ID"""

    user_id: str
    """用户 ID"""

    output_format: str
    """输出格式"""

    source_url: str
    """文件 URL"""

    file_name: str
    """文件名"""

    file_size: Optional[int]
    """文件大小"""

    status: str
    """任务状态"""

    result_url: Optional[str]
    """结果下载 URL"""

    error_message: Optional[str]
    """错误信息"""

    progress: Optional[int]
    """进度百分比 (0-100)"""

    retry_count: Optional[int]
    """重试次数"""

    task_id: Optional[str]
    """Fusion API 任务 ID"""

    started_at: Optional[str]
    """开始时间"""

    completed_at: Optional[str]
    """完成时间"""

    created_at: str
    """创建时间"""

    updated_at: str
    """更新时间"""


@dataclass
class Pagination:
    """分页信息"""
    page: int
    """当前页码"""

    page_size: int
    """每页条数"""

    total: int
    """总条数"""

    total_pages: int
    """总页数"""


@dataclass
class GetBatchesResponse:
    """获取批次列表响应"""
    batches: List[dict]
    """批次列表"""

    pagination: Pagination
    """分页信息"""


@dataclass
class GetJobsResponse:
    """获取任务列表响应"""
    jobs: List[JobDetail]
    """任务列表"""

    pagination: Pagination
    """分页信息"""


@dataclass
class ConcurrentStatus:
    """用户并发状态"""
    max_concurrent_jobs: int
    """最大并发数"""

    current_running_jobs: int
    """当前运行的任务数"""

    can_submit_new_job: bool
    """是否可以提交新任务 (别名: canStartNew)"""

    available_slots: Optional[int] = None
    """可用槽位数"""

    queued_jobs: Optional[int] = None
    """排队中的任务数"""


@dataclass
class OperationResponse:
    """操作响应"""
    batch_id: Optional[str] = None
    """批次 ID"""

    job_id: Optional[str] = None
    """任务 ID"""

    queued_jobs: Optional[int] = None
    """队列中的任务数"""

    cancelled_jobs: Optional[int] = None
    """取消的任务数"""

    retried_jobs: Optional[int] = None
    """重试的任务数"""

    paused_jobs: Optional[int] = None
    """暂停的任务数"""

    resumed_jobs: Optional[int] = None
    """恢复的任务数"""

    status: Optional[str] = None
    """任务状态"""
