""" Libraries """
from os import walk
from os.path import join
from datetime import datetime, timedelta

#>------------------------------------------ FUNCTION -------------------------------------------<#

def converttime(timestamp):
    """ IN: timestamp <str>: timestamp to be converted
        OUT: a time object <time>
        DO: convert a string in a time object """
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

def taketime(message):
    """ IN: message <str>: a message to take a string of time
        OUT: a string representing a time and a date <str>
        DO: take the time from a line of log """
    return (message[3:26] if message[2] == "[" else message[:23]) + "000"

def takeconvert(message):
    """ IN: message <str>: a message to take a string of time
        OUT: a time object <time>
        DO: execute converttime() and taketime() function togheder """
    return converttime(taketime(message))

def timediff(time1, time2):
    """ IN: time1 <str>: a message from log file, time2 <str>: same as time1
        OUT: a time difference object <timediff>
        DO: subtract time1 and time2 and apply absolute value """
    return abs(takeconvert(time1) - takeconvert(time2))

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

def match(source, message):
    """ IN: source [str]: source of the message (U1, U2, En), message [int]: part of the message
        DO: try to find couple of message with time deltas less than 1 minute"""

    line_list1, line_list2 = [], []

    if "U1" in source:
        u1_file = [join(root, name)
                   for root, dirs, files in walk(".\\u1")
                   for name in files
                   if name.endswith((".txt"))]

        u1_line = ["20" + log[5:13].replace("_", "-") + " " + line
                    for log in u1_file
                    for line in open(log, 'r')
                    if line.find(message[source.index("U1")]) >= 0]

        line_list1 = u1_line
        print("Searching " + message[source.index("U1")] + f" in U1: {len(u1_line)} results found")

    if "U2" in source:
        u2_file = [join(root, name)
                   for root, dirs, files in walk(".\\u2")
                   for name in files
                   if name.endswith((".txt"))]

        u2_line = ["20" + log[5:13].replace("_", "-") + " " + line
                    for log in u2_file
                    for line in open(log, 'r')
                    if line.find(message[source.index("U2")]) >= 0]

        if len(line_list1) == 0:
            line_list1 = u2_line
        else:
            line_list2 = u2_line
        print("Searching " + message[source.index("U2")] + f" in U2: {len(u2_line)} results found")

    if "En" in source:
        en_file = [join(root, name)
                   for root, dirs, files in walk(".\\")
                   for name in files
                   if name.endswith((".log"))]

        en_line = [line
                    for log in en_file
                    for line in open(log, 'r')
                    if line.find(message[source.index("En")]) >= 0]

        line_list2 = en_line
        print("Searching " + message[source.index("En")] + f" in En: {len(en_line)} results found")

    for item1 in line_list1:
        for item2 in line_list2:
            if timediff(item1, item2) < timedelta(minutes=1):
                print(f"Match found, time delta: {timediff(item1, item2)}")

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
