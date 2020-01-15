""""
Here, the code reads the log file of the FASTEN server to measure how many call graphs is generated per seconds
or minutes .
"""

from datetime import datetime

log_file = open("fasten_server_logs_jan14_2020.txt", 'r')

produced_cg = 0
log_lines = []

for line in log_file.readlines():

    if "eu.fasten.analyzer.javacgopal.OPALPlugin" in line:

        if "Generating" in line:
            log_lines.append(line)
            print(line)

        elif "Producing" in line:
            log_lines.append(line)
            produced_cg += 1
            print(line)

print("Number of generated call graphs: %s" % produced_cg)

# Approximation of how many call graphs were generated per second
first_line, last_line = log_lines[0], log_lines[-1]

start_time = datetime.strptime(first_line.split(" ")[0].split(".")[0], "%H:%M:%S")
finished_time = datetime.strptime(last_line.split(" ")[0].split(".")[0], "%H:%M:%S")

print("Finished in %s seconds" % (finished_time - start_time).seconds)
print("Number of call graphs per second: %s" % (produced_cg / (finished_time - start_time).seconds))

