import csv
import sys
from openpyxl import load_workbook
import pandas as pd
import xlsxwriter
import sys, os, traceback, types
import xlsxwriter
from csv import writer
import csv

import time
from datetime import datetime
from pytz import timezone


#============== ESTIMATE THE SPEED OF READING  MASTERSHEET XLSX FILE IN MY COMPUTER ================
start_time = time.perf_counter()

mastersheet = pd.read_excel ("TYPE0MASTERSHEET.xlsx")
records = mastersheet.to_records()

end_time = time.perf_counter()

print ("Reading one mastersheet file on my computer  :  ", end_time-start_time)

#============ ESTIMATE THE SPEED OF READING ONE SOURCE SVC FILE IN MY COMPUTER ===================

start_time = time.perf_counter()
with open("IndexValuePanelData_GBPCHF_H4.csv", mode='r') as csv_file:
	csv_reader = csv.reader(csv_file)
	line_cnt = 0
	for row in csv_reader :
	    last_row = row


end_time = time.perf_counter()

print ("Reading one csv file on my computer  :  ", end_time-start_time)


#============ ESTIMATE THE SPEED OF WRITING ONE RESULT SVC FILE IN MY COMPUTER ===================

end_time = time.perf_counter()

format = "%Y.%m.%d,%H:%M:%S"
# Current time in GMT
now_gmt = datetime.now(timezone('GMT'))
now_asia = now_gmt.astimezone(timezone('Europe/Moscow'))
date_str = now_asia.strftime(format)

data = ["GBPCHF,Date:2020.08.30,19:36:10,Type0:S"]

with open("Type0.csv", 'a+', newline='') as write_obj:
    # Create a writer object from csv module
    csv_writer = writer(write_obj)
    # Add contents of list as last row in the csv file
    csv_writer.writerow(data)

end_time = time.perf_counter()

print ("Writing one csv file on my computer  :  ", end_time-start_time)