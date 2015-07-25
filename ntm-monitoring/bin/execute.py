#!/usr/bin/python
import psutil,os
from functions import *
from checks import *
from conf import *
import argparse
from logging.handlers import RotatingFileHandler
import datetime

#Set Format and DateTime
format = "%a,%b %d,%H:%M:%S,%Y"
today = datetime.datetime.today()
s = today.strftime(format)
i = datetime.datetime.now()

#Set HostName and HostIp
host_name = socket.gethostname()
host_ip = socket.gethostbyname(socket.gethostname()) 

def main() :

   #Key Function to present
   parser = argparse.ArgumentParser()
   parser.add_argument("--cpu", action="store_true", help="verify the cpu usage")
   parser.add_argument("--disk", action="store_true", help="verify the disk usage")
   parser.add_argument("--mem", action="store_true", help="verify the mem usage")
   parser.add_argument("--load", action="store_true", help="verify the load usage")
   parser.add_argument("--all", action="store_true", help="verify the all server usage")
   args = parser.parse_args()

   TEST_NAME="ntm-monitoring-report"
   EXIT_CODE=0

   #Creating the log file
   LOG_NAME=""+ TEST_NAME  #Log file name
   LOG_FILE=LOG_BASE_DIR + "/" + LOG_NAME + ".log" #LOG file name
   CSV_FILE=LOG_BASE_DIR + "/" + LOG_NAME + ".csv" #CSV file name

   startScript(TEST_NAME,LOG_FILE)
   #Start Log file.
   (origStdout,log_file)=setLogFile(LOG_FILE)

   
   #DISK
   disk_usage=""
   disk_free=""
   exit_code_current=""
   if args.disk or args.all :
     (exit_code_current,disk_usage, disk_free)=checkDisk()
     if exit_code_current > EXIT_CODE:
       EXIT_CODE=exit_code_current

   #CPU
   cpu_usage=""
   if args.cpu or args.all :
     (exit_code_current,cpu_usage)=checkCpu()
     if exit_code_current > EXIT_CODE:
       EXIT_CODE=exit_code_current

   #MEMO
   memo_usage=""
   if args.mem or args.all:
     (exit_code_current,memo_usage)=checkMemo()
     if exit_code_current > EXIT_CODE:
       EXIT_CODE=exit_code_current

   #LOAD
   uptime_usage=""
   if args.load or args.all:
     (exit_code_current,uptime_usage)=checkLoad()
     if exit_code_current > EXIT_CODE:
       EXIT_CODE=exit_code_current

   #Print Sum:
   csvLine=[i.year,i.month,i.day,i.hour,i.second,str(EXIT_CODE),disk_usage,disk_free,cpu_usage,memo_usage,uptime_usage,host_name,host_ip]
   for ndx, member in enumerate(csvLine):
     csvLine[ndx] = str(member)+','
   writeToFile("".join(csvLine)+"\n",CSV_FILE)
   print ("%s,%s,%s,%s:%s,%d,%s,%s,%s,%s,%s,%s,%s" %(i.year,i.month,i.day,i.hour,i.second,EXIT_CODE,disk_usage,disk_free,cpu_usage,memo_usage,uptime_usage,host_name,host_ip))
   
  
   #Send severity mail alert
   if EXIT_CODE >= 1:
      create_Alert(ALERT_TYPE_CRITICAL,TEST_NAME,[LOG_FILE,CSV_FILE])
   elif EXIT_CODE >= 2:
       create_Alert(ALERT_TYPE_WARNING,TEST_NAME,[LOG_FILE,CSV_FILE])

   #End Log file.
   unsetLogFile(origStdout,log_file)
   endScript(EXIT_CODE)


if __name__ == "__main__":
   main()
