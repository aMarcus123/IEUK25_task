import unittest
from datetime import datetime

from solution import (CleanData, ArrayToObjectArray, GetLogWindows, floor_to_time_window, GetWindowMetrics, GetHighestAverageFailures, GetIPHighRequestRate, PrintLogGivenIP, LogData, WindowMetrics)

class TestSolution(unittest.TestCase):

    def setUp(self):
        self.raw_file = "sample-log.log"
    
    def test_clean_data(self):
        entry = '100.34.17.233 - NO - [01/07/2025:06:00:02] "GET /news/grammy-nominations-2024 HTTP/1.1" 302 1234 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" 269'
        cleaned = CleanData(self.raw_file)
        first_entry = cleaned[0]
        self.assertEqual(first_entry, ["100.34.17.233", "NO", "[01/07/2025:06:00:02]", "GET /news/grammy-nominations-2024 HTTP/1.1", "302", "1234", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "269"])



if __name__ == '__main__':
    unittest.main()