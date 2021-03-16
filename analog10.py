from os import walk
from os.path import join

def search(quote, verbose = 0):
    """ IN: quote <str>: part of the quote to be searched, verbose <int>: level of verbosity
        DO: search if a quote is in the log file """

    logs_list = [join(root, name) # Build list of files, based on current directory
                 for root, dirs, files in walk(".\\")
                 for name in files
                 if name.endswith((".txt", ".log"))]

    file_count = 0

    for log_name in logs_list:

        log_data = open(log_name, 'r')
        line_count = 0

        for line in log_data:
            try:
                if log_name.endswith(".log"): # if line[2] == "[":
                    text = line[29:].split('] ')[1] if line[28] == "[" else line[28:]
                else:
                    text = line.split('] ')[1] if line[19] == "[" else line[19:]
            except IndexError:
                continue

            text, quote = text.lower(), quote.lower() # Needed for some message

            if text.find(quote) >= 0: # Line counter
                line_count += 1
                if verbose > 1:
                    print(line)

        if line_count > 0: # File counter
            file_count += 1
            if verbose > 0:
                print(f"Found {quote} in {log_name}: {line_count} results found")

        log_data.close()

    print(f"Found {file_count}/{len(logs_list)} files containing {quote}")

#>-----------------------------------------------------------------------------------------------<#

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
                # "SIP INVITE",           # Late Call Entry Time
                "SIP CHANGE_CHANNEL",
                "SIP START_MONITORING",
                # "SIP INVITE",           # MCVideo Call Setup Time
                # "SIP 200 OK",
                "SIP MESSAGE",          # MCData Delivery Time
                "SIP MESSAGE RECEIVED",
                "SIP MESSAGE NOTIFIED",
                "ECHO REQUEST",         # Round Trip Time - for ping service
                "ECHO REPLY" ]

for element in lines_list:
    search(element, 1)

#>-----------------------------------------------------------------------------------------------<#
