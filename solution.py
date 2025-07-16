from collections import deque, defaultdict
from datetime import datetime
import re

#Match a single log in the log file
LOG_PATTERN = re.compile(
    r'(\S+)'                      # IP address
    r' - (\S+) - '                # Country code
    r'\[([^\]]+)\] '              # Timestamp 
    r'"([^"]+)" '                 # HTTP request 
    r'(\d{3}) '                   # HTTP status code 
    r'(\d+) '                     # Response size 
    r'"[^"]*" '                   # 
    r'"([^"]+)" '                 # 
    r'(\d+)'                      # response time
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
    """
    Represents the data that can be calculated from a window of time of logs
    """
    
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

    #for each line in the array
    for entry in arr:
        #identify the attributes
        ip_address = entry[0]
        country_code = entry[1]
        timestamp = entry[2]
        http_request = entry[3]
        http_status_code = entry[4]
        reponse_size = entry[5]
        device_details = entry[6]
        reponse_time = entry[7]
        
        #append a new LogData object with attributes to list
        cleaned_objects.append(LogData(ip_address, country_code, timestamp, http_request, http_status_code, reponse_size, device_details, reponse_time))
    
    return cleaned_objects


def GetLogWindows(logs, time_window):
    """
    groups sequences of logs into windows of time i.e 1 min interval of logs 

    Args:
        logs (LogData[]): list of LogData objects
        time_window (int): how big the time window should be

    Returns:
        Dictionary, with timestamp as key, logs within that timeframe as the values

    """
    log_windows = defaultdict(list)

    #iterate though logs
    for log in logs:
        #get current time stamp of log
        timestamp = datetime.strptime(log.timestamp, "%d/%m/%Y:%H:%M:%S")

        #get the window the log belongs to 
        window = floor_to_time_window(timestamp, time_window)

        #append log to dictionary with the key of the window
        log_windows[window].append(log)

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
    """
    Gets metrics from each time window of logs

    Args:
        log_window (dict(list)): the dictionary of logs, key being the timestamp the logs took place

    Returns:
        list of Metrics for each log window
    """
    window_metrics = []

    #iterate through the dictionary
    for window, logs in log_windows.items():
        #create a temporary WindowMetrics object
        metric = WindowMetrics(window)

        #timestamp is the current window being looked at
        metric.timestamp = window
        
        #set number of requests and failures
        metric.number_of_requests = len(logs)
        metric.number_of_failures = sum(1 for log in logs if 400 <= int(log.http_status_code) < 600)
        for log in logs:
            metric.total_response_time += int(log.response_time)

        #calculate average failures and response time
        metric.average_number_of_failures = metric.GetAverageFailures()
        metric.average_response_time = metric.GetAverageResponseTimes()
    
        window_metrics.append(metric)

    return window_metrics


def GetHighestAverageFailures(log_window_metrics):
    """
    Finds the window of time that has the higest average of failures

    Args:
        log_window_metrics (list(WindowMetrics)): list of all window metrics
    
    Returns:
        the window that has the highest average of failures
        
    """

    highest_failures = 0
    worst_window = WindowMetrics(None)

    #iterate through all the windows, find the window with the highest number of failures
    for window in log_window_metrics:
        if window.average_number_of_failures > highest_failures:
            highest_failures = window.average_number_of_failures
            worst_window = window

    return worst_window
        

def GetIPHighRequestRate(worst_window_logs):
    """
    Iterates through a timeframe, gets the top 5 IP addresses that have the highest number of requests in tha that time frame

    Args:
        worst_window_logs (LogData[]): list of logs
    
    Returns:
        list of ip addresses

    """
    ip_addresses = defaultdict(int)

    #if target address found, increase count by 1
    for log in worst_window_logs:
        ip_addresses[log.ip_address] += 1

    #get the top 5 addresses with the highest count
    top_5_ips = sorted(ip_addresses.items(), key=lambda x: x[1], reverse=True)[:5] 

    return top_5_ips


def PrintLogGivenIP(address, logs):
    """
    Prints out all the logs of a given address and a given log list

    Args:
        address(str): the specific address to look out for
        logs(LogData[]): the log list
    
    """
    #iterate through the logs, if the log came from the address, print out the request sent
    for log in logs:
        if log.ip_address == address:
            print(f"URL: {log.http_request} | STATUS CODE: {log.http_status_code}")





def main():
    #the log file to be looked at
    log_file = "sample-log.log"

    #clean the log file, cleaned_data is a list of list, inner list represents all the data from a single log
    cleaned_data = CleanData(log_file)

    #convert the inner list into an object, log_data is now a list of LogData objects
    log_data = ArrayToObjectArray(cleaned_data)

    #group timeframes of logs together, this variable is a dictionary, key being the timeframe, and the value being a list of logs in that timeframe
    one_minute_log_windows = GetLogWindows(log_data, 1)

    #calculate the metrics of each timeframe
    log_window_metrics = GetWindowMetrics(one_minute_log_windows)

    #get the timeframe with the highest average failures
    worst_window = GetHighestAverageFailures(log_window_metrics)

    #get the logs within the worst timeframe
    worst_window_logs = one_minute_log_windows[worst_window.timestamp]

    #Get the top 5 addresses of the sus ip addresses
    sus_ip_addressses = GetIPHighRequestRate(worst_window_logs)

    #for each sus address, get all their logs from the highest failure time frame
    for address, _ in sus_ip_addressses:
        print(address)
        PrintLogGivenIP(address, worst_window_logs)
        print()




    


if __name__ == "__main__":
    main()