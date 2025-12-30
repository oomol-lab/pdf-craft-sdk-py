"""上传相关的类型定义"""

from typing import Dict, Optional, Callable
from dataclasses import dataclass


@dataclass
class InitUploadResponse:
    """初始化上传响应"""
    upload_id: str
    part_size: int
    total_parts: int
    uploaded_parts: list
    presigned_urls: Dict[int, str]


@dataclass
class GetUploadUrlResponse:
    """获取上传文件 URL 响应"""
    url: str


@dataclass
class UploadProgress:
    """上传进度信息"""
    uploaded_bytes: int
    total_bytes: int
    current_part: int
    total_parts: int

    @property
    def percentage(self) -> float:
        """返回上传进度百分比 (0-100)"""
        if self.total_bytes == 0:
            return 0.0
        return (self.uploaded_bytes / self.total_bytes) * 100


# 进度回调函数类型
ProgressCallback = Optional[Callable[[UploadProgress], None]]
