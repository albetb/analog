""" Libraries """
from os import walk
from os.path import join
from datetime import datetime, timedelta

#>------------------------------------------ FUNCTION -------------------------------------------<#

class TimeLine:
    """ IN: message <str>: a message to take a string of time
        ATTRIBUTES: line <str>: the original line, time <time>: the timestamp as time object
        METHODS: line_to_time: return timestamp of the line, __sub__: allow subtraction """

    def __init__(self, line):
        self.line = line                # Original line
        self.time = self.line_to_time() # Timestamp of the line

    def line_to_time(self):
        """ IN: message <str>: a message to take a string of time
            OUT: a time object <time>
            DO: convert a string in a time object """

        timestamp = (self.line[3:26] if self.line[2] == "[" else self.line[:23]) + "000"
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

    def __sub__(self, other):
        """ IN: self <str>: a message from log file, other <str>: same as time1
            OUT: a time difference object <timediff>
            DO: subtract self.time and other.time and apply absolute value """

        return abs(self.time - other.time)

def search(message, verbose = 0):
    """ IN: message <str>: part of the message to be searched, verbose <int>: level of verbosity
        DO: search if a message is in the log file """

    logs_list = [join(root, name) # Build list of files, based on current directory
                 for root, dirs, files in walk(".\\")
                 for name in files
                 if name.endswith((".txt", ".log"))]

    file_count = 0

    for log_name in logs_list:

        line_count = 0

        for line in open(log_name, 'r'):

            if (line.lower()).find(message.lower()) >= 0: # Line counter
                line_count += 1
                if verbose > 1:
                    print(line)

        if line_count > 0: # File counter
            file_count += 1
            if verbose > 0:
                print(f"Found {message} in {log_name}: {line_count} results found")

    print(f"Found {file_count}/{len(logs_list)} files containing {message}")

def buildlinelist(source, message):
    """ IN: source <str>: source of the message (U1, U2, En), message <str>: part of the message
        OUT: list of lines from file source [str]
        DO: make a list of lines who contain message"""

    if source in ["U1", "U2"]:

        file_list = [join(root, name)
                     for root, dirs, files in walk(".\\" + source.lower())
                     for name in files
                     if name.endswith((".txt"))]

        return ["20" + log[5:13].replace("_", "-") + " " + line
                for log in file_list
                for line in open(log, 'r')
                if line.find(message) >= 0]

    file_list = [join(root, name)
                for root, dirs, files in walk(".\\")
                for name in files
                if name.endswith((".log"))]

    return [line
            for log in file_list
            for line in open(log, 'r')
            if line.find(message) >= 0]

def match(source, message):
    """ IN: source [str]: source of the message (U1, U2, En), message [str]: part of the message
        DO: try to find couple of message with time deltas less than 1 minute"""

    line_list1, line_list2 = [], []

    if "U1" in source:

        line_list1 = buildlinelist("U1", message[source.index("U1")])
        print("Searching " + message[source.index("U1")] + f" in U1: {len(line_list1)} results")

    if "U2" in source:

        if len(line_list1) == 0:
            line_list1 = buildlinelist("U2", message[source.index("U2")])
            print("Searching " + message[source.index("U2")] + f" in U2: {len(line_list1)} results")
        else:
            line_list2 = buildlinelist("U2", message[source.index("U2")])
            print("Searching " + message[source.index("U2")] + f" in U2: {len(line_list2)} results")

    if "En" in source:

        line_list2 = buildlinelist("En", source.index("En"))
        print("Searching " + message[source.index("En")] + f" in En: {len(line_list2)} results")

    for item1 in line_list1:
        t_item1 = TimeLine(item1)
        for item2 in line_list2:
            t_item2 = TimeLine(item2)
            # Evaluate time difference and print only match whose difference are less than 1 minute
            if t_item1 - t_item2 < timedelta(minutes = 1):
                print(f"Match found, time delta: {t_item1 - t_item2}")

#>-------------------------------------------- MAIN ---------------------------------------------<#

# This KPI have not message specified:
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

for element in lines_list:
    search(element, 0)

print("--------------------------------------------------")

match(["U1", "U2"], ["floor granted", "Floor Request"])
match(["U2", "U1"], ["floor granted", "Floor Request"])

#>-----------------------------------------------------------------------------------------------<#
