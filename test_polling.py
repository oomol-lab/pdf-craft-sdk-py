import time
import unittest
from unittest.mock import MagicMock
from pdf_craft_sdk.client import PDFCraftClient
from pdf_craft_sdk.enums import PollingStrategy, FormatType

class TestPolling(unittest.TestCase):
    def test_exponential_polling(self):
        client = PDFCraftClient("fake_key")
        
        # Mock get_conversion_result to return 'processing' a few times then 'completed'
        # We want to verify the intervals.
        # Intervals should be: 1, 2, 4, 5, 5...
        
        # Side effect: returns 'processing' 4 times, then 'completed'
        client.get_conversion_result = MagicMock(side_effect=[
            {"state": "processing"},
            {"state": "processing"},
            {"state": "processing"},
            {"state": "processing"},
            {"state": "completed", "data": {"downloadURL": "http://example.com/result.md"}}
        ])
        
        # We need to capture the time sleeps.
        original_sleep = time.sleep
        sleeps = []
        def mock_sleep(seconds):
            sleeps.append(seconds)
            
        time.sleep = mock_sleep
        
        try:
            client.wait_for_completion("task123", polling_strategy=PollingStrategy.EXPONENTIAL)
        finally:
            time.sleep = original_sleep
            
        # Expected sleeps: 1, 2, 4, 5
        self.assertEqual(sleeps, [1.0, 2.0, 4.0, 5.0])
        print("Exponential polling test passed with intervals:", sleeps)

    def test_fixed_polling(self):
        client = PDFCraftClient("fake_key")
        
        client.get_conversion_result = MagicMock(side_effect=[
            {"state": "processing"},
            {"state": "processing"},
            {"state": "completed", "data": {"downloadURL": "http://example.com/result.md"}}
        ])
        
        original_sleep = time.sleep
        sleeps = []
        def mock_sleep(seconds):
            sleeps.append(seconds)
            
        time.sleep = mock_sleep
        
        try:
            client.wait_for_completion("task123", polling_strategy=PollingStrategy.FIXED)
        finally:
            time.sleep = original_sleep
            
        # Expected sleeps: 3, 3
        self.assertEqual(sleeps, [3.0, 3.0])
        print("Fixed polling test passed with intervals:", sleeps)

if __name__ == "__main__":
    unittest.main()
