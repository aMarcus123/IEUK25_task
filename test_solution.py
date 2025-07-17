import unittest
from datetime import datetime

from solution import (CleanData, ArrayToObjectArray, GetLogWindows, floor_to_time_window, GetWindowMetrics, GetHighestAverageFailures, GetIPHighRequestRate, PrintLogGivenIP, LogData, WindowMetrics)

class TestSolution(unittest.TestCase):

    def setUp(self):
        self.raw_file = "sample-log.log"
        self.cleaned_data = CleanData(self.raw_file)
        self.object_data = ArrayToObjectArray(self.cleaned_data)

        
    
    def test_clean_data(self):
        first_entry = self.cleaned_data[0]
        self.assertEqual(first_entry, ["100.34.17.233", "NO", "01/07/2025:06:00:02", "GET /news/grammy-nominations-2024 HTTP/1.1", "302", "1234", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "269"])

    def test_array_to_object_array(self):
        first_entry = self.object_data[0]

        test_object = LogData("100.34.17.233", "NO", "01/07/2025:06:00:02", "GET /news/grammy-nominations-2024 HTTP/1.1", "302", "1234", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "269" )
        self.assertEqual(first_entry, test_object)






if __name__ == '__main__':
    unittest.main()