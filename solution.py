from collections import deque, defaultdict
from datetime import datetime
import re

#Match a single log in the log file
LOG_PATTERN = re.compile(
    r'(\S+)'                      # IP address
    r' - (\S+) - '                # Country code
    r'\[([^\]]+)\] '              # Timestamp inside []
    r'"([^"]+)" '                 # HTTP request inside ""
    r'(\d{3}) '                   # HTTP status code (3 digits)
    r'(\d+) '                     # Response size (digits)
    r'"[^"]*" '                   # Referrer (can be empty)
    r'"([^"]+)" '                 # User agent string inside ""
    r'(\d+)'                      # Final number (e.g. duration)
)


class LogData:
    """
    Represents all the data of a single log
    """

    def __init__(self, ip_address, country_code, timestamp, http_request, http_status_code, response_size, device_details, response_time):
        self.ip_address = ip_address
        self.country_code = country_code
        self.timestamp = timestamp
        self.http_request = http_request
        self.http_status_code = http_status_code
        self.response_size = response_size
        self.device_details = device_details
        self.response_time = response_time
    
    def PrintData(self):
        print("IP Address: " + str(self.ip_address))
        print("Country Code: " + str(self.country_code))
        print("Timestamp: " + str(self.timestamp))

class WindowMetrics:
    
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.number_of_requests = 0
        self.number_of_failures = 0
        self.average_number_of_failures = 0
        self.total_response_time = 0
        self.average_response_time = 0
    
    def GetAverageFailures(self):
        return self.number_of_failures / self.number_of_requests

    def GetAverageResponseTimes(self):
        return self.total_response_time / self.number_of_requests


def CleanData(file):
    """
    Takes a raw file, matches the line to a regular expression, cleans up the line

    Args:
        file (str): the filename of the raw data
    
    Returns:
        a list of cleaned data
    """
    cleaned_data = []

    with open(file, "r") as file:
        for line in file:
            match = LOG_PATTERN.match(line)
            if match:
                cleaned_data.append(list(match.groups()))
    
    return cleaned_data


def ArrayToObjectArray(arr):
    """
    Converts an 2d array of data into an array of objects

    Args:
        arr (string[]): the array to be converted
    
    Returns:
        Array of objects
    """

    cleaned_objects = []

    for entry in arr:
        ip_address = entry[0]
        country_code = entry[1]
        timestamp = entry[2]
        http_request = entry[3]
        http_status_code = entry[4]
        reponse_size = entry[5]
        device_details = entry[6]
        reponse_time = entry[7]
        
        cleaned_objects.append(LogData(ip_address, country_code, timestamp, http_request, http_status_code, reponse_size, device_details, reponse_time))
    
    return cleaned_objects


def GetLogWindows(logs, time_window):
    log_windows = defaultdict(list)

    for log in logs:
        timestamp = datetime.strptime(log.timestamp, "%d/%m/%Y:%H:%M:%S")
        window = floor_to_time_window(timestamp, time_window)
        log_windows[window].append(log)
    
    """
    for k,vs in log_windows.items():
        print("Time Window: " + str(k.strftime('%d/%m/%Y %H:%M:%S')))
        for v in vs:
            print(f"  IP: {v.ip_address} | Status: {v.http_status_code} | URL: {v.http_request}")
        print()
    """

    return log_windows

def floor_to_time_window(timestamp, time_window):
    """
    Helper function to GetLogWindows, floors a datetime object to the nearest lower time window interval

    Args:
        timestamp (datetime): the datetime object to floor
        timeWindow (int): the size of the time window

    Return:

    """
    floored_minute = timestamp.minute - (timestamp.minute % time_window)
    # Replace minutes and seconds to floor the timestamp to the window
    return timestamp.replace(minute=floored_minute, second=0, microsecond=0)


def GetWindowMetrics(log_windows):
    window_metrics = []

    for window, logs in log_windows.items():
        metric = WindowMetrics(window)
        metric.timestamp = window
        metric.number_of_requests = len(logs)
        metric.number_of_failures = sum(1 for log in logs if 400 <= int(log.http_status_code) < 600)
        for log in logs:
            metric.total_response_time += int(log.response_time)

        metric.average_number_of_failures = metric.GetAverageFailures()
        metric.average_response_time = metric.GetAverageResponseTimes()
    
        window_metrics.append(metric)
    
    highest_failures = 0
    worst_window = WindowMetrics(None)

    for window in window_metrics:
        if window.average_number_of_failures > highest_failures:
            highest_failures = window.average_number_of_failures
            worst_window = window
        
    if worst_window:
        print(str(worst_window.timestamp.strftime('%d/%m/%Y %H:%M:%S')))
        print("Number of crashes: " + str(worst_window.number_of_failures))
        print("Number of requests: " + str(worst_window.number_of_requests))
        print("Average failures: " + str(worst_window.average_number_of_failures))
        print()

    ip_addresses = defaultdict(LogData)

    print("Logs")
    for log in log_windows[worst_window.timestamp]:
        #if 400 <= int(log.http_status_code) < 600:
        #    print(f"  IP: {log.ip_address} | Status: {log.http_status_code} | URL: {log.http_request}")









def main():
    
    log_file = "sample-log.log"
    cleaned_data = CleanData(log_file)
    log_data = ArrayToObjectArray(cleaned_data)


    one_minute_log_windows = GetLogWindows(log_data, 5)

    GetWindowMetrics(one_minute_log_windows)


    """
    CountryWhereDown = {}

    for log in log_data:
        if 400 <= int(log.http_status_code) < 600:
            if log.country_code not in CountryWhereDown:
                CountryWhereDown[log.country_code] = 1
            else:
                CountryWhereDown[log.country_code] += 1


    for k,v in CountryWhereDown.items():
        print(k + ": " + str(v))
    """
    


if __name__ == "__main__":
    main()