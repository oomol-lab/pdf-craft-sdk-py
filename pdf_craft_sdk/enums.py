from enum import Enum

class FormatType(Enum):
    MARKDOWN = "markdown"
    EPUB = "epub"

class PollingStrategy(Enum):
    EXPONENTIAL = 1.5
    FIXED = 1.0
    AGGRESSIVE = 2.0

class BatchStatus(Enum):
    """批次状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    PAUSED = "paused"

class JobStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
