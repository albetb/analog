""" Libraries """
from os import walk
from os.path import join
from datetime import datetime, timedelta

#>------------------------------------------- CLASS ---------------------------------------------<#

class TimeLine:
    """ INPUT:
            line <str>: a log line to take a string of time
        ATTRIBUTES:
            line <str>: the original line
            time <time>: the timestamp as time object
        METHODS:
            __line_to_time: return timestamp of the line, used to set time
            __sub__: allow time subtraction between lines """

    def __init__(self, line):
        self.line = line                  # Original line
        self.time = self.__line_to_time() # Timestamp of the line

    def __line_to_time(self):
        """ IN: message <str>: a message to take a string of time
            OUT: a time object <time>
            DO: convert a string in a time object """

        timestamp = (self.line[3:26] if self.line[2] == "[" else self.line[:23]) + "000"
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

    def __sub__(self, other):
        """ IN: self <str>: a message from log file; other <str>: same as time1
            OUT: a time difference object <timediff>
            DO: subtract self.time and other.time and apply absolute value """

        return abs(self.time - other.time)

class SearchFile:
    """ INPUT:
            time_limit <int>: max time difference delta between message, default = 60
        ATTRIBUTES:
            time_limit <int>: max time difference in second
            logs [str]: list of all files
            file_XX [str]: list of files from a specific source
            line_XX [str]: list of all lines from a specific source
        METHODS:
            __build_line_list: used from match, make a list of lines with a specified message
            match: find two matching lines with time difference less than time_limit
            search: search a message in all files """

    def __init__(self, time_limit = 60):

        self.time_limit = time_limit # Time limit in second

        self.logs = [join(root, name) # List of all files, based on current directory
                    for root, dirs, files in walk(".\\")
                    for name in files
                    if name.endswith((".txt", ".log"))]

        self.file_u1 = [join(root, name) # List of log files from User Equipment 1
                        for root, dirs, files in walk(".\\u1")
                        for name in files
                        if name.endswith((".txt"))]

        self.line_u1 = ["20" + log[5:13].replace("_", "-") + " " + line
                        for log in self.file_u1
                        for line in open(log, 'r')]

        self.file_u2 = [join(root, name) # List of log files from User Equipment 2
                        for root, dirs, files in walk(".\\u2")
                        for name in files
                        if name.endswith((".txt"))]

        self.line_u2 = ["20" + log[5:13].replace("_", "-") + " " + line
                        for log in self.file_u2
                        for line in open(log, 'r')]

        self.file_en = [join(root, name) # List of log files from Enensys
                        for root, dirs, files in walk(".\\")
                        for name in files
                        if name.endswith((".log"))]

        self.line_en = [line
                        for log in self.file_en
                        for line in open(log, 'r')]

    def __build_line_list(self, src, msg):
        """ IN: src <str>: message source (u1, u2, en); msg <str>: part of the message
            OUT: list of lines from file source [str]
            DO: make a list of lines who contain message """

        line_list = self.line_u1 if src == "u1" else self.line_u2 if src == "u2" else self.line_en

        return [line
                for line in line_list
                if line.find(msg) >= 0]

    def match(self, src1, msg1, src2, msg2):
        """ IN: src1, src2 <str>: message source (u1, u2, en); msg1, msg2 <str>: part of the message
            DO: try to find couple of message with time deltas less than self.time_limit minute """

        line_list1 = self.__build_line_list(src1, msg1)
        print(f"\nSearching {msg1} in {src1}: {len(line_list1)} results")

        line_list2 = self.__build_line_list(src2, msg2)
        print(f"Searching {msg2} in {src2}: {len(line_list2)} results")

        for item1 in line_list1:
            for item2 in line_list2:
                time_difference = TimeLine(item1) - TimeLine(item2)
                if time_difference < timedelta(seconds = self.time_limit):
                    print(f"  Match found, time delta: {time_difference}")

    def search(self, msg, verbose = 0):
        """ IN: msg <str>: part of the message; verbose <int>: level of verbosity
            DO: search if a message is in the log file """

        file_count = 0
        for log_name in self.logs:

            line_count = 0
            for line in open(log_name, 'r'):

                if (line.lower()).find(msg.lower()) >= 0: # Line counter
                    line_count += 1
                    if verbose > 1:
                        print(line)

            if line_count > 0: # File counter
                file_count += 1
                if verbose > 0:
                    print(f"Found {msg} in {log_name}: {line_count} results found")

        print(f"Found {file_count}/{len(self.logs)} files containing {msg}")

#>-------------------------------------------- MAIN ---------------------------------------------<#

# This KPI have not message specified (11/21):
#     Speech Quality
#     Mouth-to-Ear Latency
#     Speech Service Interruption Time
#     Video Quality
#     Video Service Interruption Time
#     MCData Service Access Time
#     IP Service Access Time
#     IP Data Transfer Time
#     IP Delivery Time
#     IP Throughput
#     Data Service Interruption Time
#
# Log example (Enensys):
#     E [2021-02-23 14:28:47.406] Log file opened
#     I [2021-02-23 14:28:47.407] SetLocalAddress "0.0.0.0"
#     D [2021-02-23 14:28:47.407] [CRYUT] CryptsUtils test OK!
#     D [2021-02-23 14:28:47.407] [UTILS] TimeTest success.
#
# Log example (User Equipment):
#     10:50:34.195 - D - [JavaEngine] ACCOUNT M1
#     10:50:34.196 - D - [JavaEngine] Send SetConfigurationServer 192.168.0.13
#     10:50:34.197 - D - [JavaEngine] Send SetConfigurationCredentials

lines_list = [  "ATTACH REQUEST",       # Network Attach Time
                "ATTACH COMPLETE",
                "DETACH REQUEST",       # Network Re-Selection Time
                # "ATTACH COMPLETE",
                "SIP REGISTER",         # MCX Service Registration Time
                "SIP 200 OK",
                "Group Call Request",   # MCPTT Access Time - start group call
                "Group Call Response",
                "Floor Granted",
                "Floor Request",        # MCPTT Access Time - within group call
                # "Floor Granted",
                "SIP INVITE",           # End-to-End MCPTT Access Time
                # "Group Call Request",
                # "SIP INVITE",         # Late Call Entry Time
                "SIP CHANGE_CHANNEL",
                "SIP START_MONITORING",
                # "SIP INVITE",         # MCVideo Call Setup Time
                # "SIP 200 OK",
                "SIP MESSAGE",          # MCData Delivery Time
                "SIP MESSAGE RECEIVED",
                "SIP MESSAGE NOTIFIED",
                "ECHO REQUEST",         # Round Trip Time - for ping service
                "ECHO REPLY" ]

sf = SearchFile()

for item in lines_list:
    sf.search(item, 0)

print("\n" + "-" * 50)

sf.match("u1", "floor granted", "u2", "Floor Request")
sf.match("u2", "floor granted", "u1", "Floor Request")

#>-----------------------------------------------------------------------------------------------<#
