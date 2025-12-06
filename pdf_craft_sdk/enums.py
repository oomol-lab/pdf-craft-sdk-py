from enum import Enum

class FormatType(Enum):
    MARKDOWN = "markdown"
    EPUB = "epub"

class PollingStrategy(Enum):
    EXPONENTIAL = 1.5
    FIXED = 1.0
    AGGRESSIVE = 2.0
