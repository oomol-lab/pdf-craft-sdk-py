class PDFCraftError(Exception):
    """Base exception for PDF Craft SDK"""
    pass

class APIError(PDFCraftError):
    """Raised when API returns an error"""
    pass

class TimeoutError(PDFCraftError):
    """Raised when conversion times out"""
    pass
