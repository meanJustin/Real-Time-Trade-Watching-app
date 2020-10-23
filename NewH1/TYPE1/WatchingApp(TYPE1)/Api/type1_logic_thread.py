from PyQt5.QtCore import QThread, pyqtSignal
from collections import deque
from csv import writer
import sys
import csv

###progress bar
from datetime import datetime
from pytz import timezone
import env as ENV
import time



class External(QThread):
    """
    Runs a time_cnter thread.
    """
    countChanged = pyqtSignal(int)
    printChanged = pyqtSignal(str)

    src_file_name = " "
    last_print = "C"
    first_flag = 1
    start_hour = 0
    end_hour = 24

    back_count = -5
    previous_printing = "0"

    #initial the data before start new cycle
    def initialData(self) :
        return

    # return current GMT+3 time
    def getCurrentGmtTime(self) :
        # Current time in GMT+3
        now_gmt = datetime.now(timezone('GMT'))
        return now_gmt.astimezone(timezone('Europe/Moscow'))

    # monitor the cycle time monitora and return the remain time
    def getRemainTime_monitorTVA(self) -> float:
        #determine whether TVA is on right now
        cur_time = self.getCurrentGmtTime()
        minute = cur_time.minute
        hour = cur_time.hour
        second = cur_time.second

        #remain the next time
        return minute * 60 + second

    def log_detail(self, detailData) :
        file_name = ENV.MASTERFILEPATH + 'Type1' + '_info.csv'
        #represent the writed data into the console
        print(detailData)

        while(1):
            try :
                with open(file_name, 'a+', newline='') as write_obj:
                    # Create a writer object from csv module
                    csv_writer = writer(write_obj)
                    # Add contents of list as last row in the csv file
                    csv_writer.writerow(detailData)
                return
            except IOError as x:
                print  ("couldn't read this file on this spot")

    # remove one last row for printing some thing like (BB, SS)
    def remove_last_row(self) :
        file = open(ENV.MASTERFILEPATH + ENV.TYPE1_PRINT, "r+")
        lines = file.readlines()
        lines.pop()
        file = open(ENV.MASTERFILEPATH + ENV.TYPE1_PRINT, "w+")
        file.writelines(lines)

    #print B on the log and csv and write the log into the info
    def printBSC(self, print_char, cur_row, past_row) :

        if self.last_print == print_char :
            return

        str_data = " "
        format = "%Y.%m.%d,%H:%M:%S"
        # Current time in GMT
        now_gmt = datetime.now(timezone('GMT'))
        gmt_time = now_gmt.astimezone(timezone('Europe/Moscow'))
        date_str = gmt_time.strftime(format)

        printData = [
            self.src_file_name[0:self.src_file_name.find("_")] + 
            ','+ 'Date:'+ date_str+
            ',Type1' + ':'+ print_char
        ]

        logData = [
            self.src_file_name[0:self.src_file_name.find("_")] + 
            ','+ 'Date:'+ date_str +
            ',Type1' + ':'+ print_char + "  " + 
            "Current Row : " + str(cur_row) + " " +
            "Previous Row : " + str(past_row)
        ]

        if print_char == "B" or print_char == "S" :
            logData = [
                self.src_file_name[0:self.src_file_name.find("_")] + 
                ','+ 'Date:'+ date_str +
                ',Type1' + ':'+ print_char + "  " + 
                "Current Row : " + str(cur_row) + " " +
                "Previous Row : " + str(past_row)
            ]

        # Appending a row to csv with missing entries
        if print_char != "DO NOTHING":
            self.last_print = print_char
            self.append_list_as_row(printData)

        self.printChanged.emit(str_data.join(printData))
        self.log_detail(logData)


    #write the new data on the last row of the data
    def append_list_as_row(self, data):
        # Open file in append mode
        file_name = ENV.MASTERFILEPATH + 'Type1' + '.csv'

        #represent the writed data into the console
        while(1):
            try :
                with open(file_name, 'a+', newline='') as write_obj:
                    # Create a writer object from csv module
                    csv_writer = writer(write_obj)
                    # Add contents of list as last row in the csv file
                    csv_writer.writerow(data)
                return
            except IOError as x:
                print  ("couldn't read this file on this spot")

    #read the previous row from the csv file
    #read the previous row from the csv file
    def rowToFloat(self, row) :
        #change every element to real float number
        temp_date = row[0]
        temp_time = row[15]
        row[0] = 0
        row[15] = 0
        data_row = []
        for item in row :
            data_row.append(float(item))
        data_row[0] = temp_date
        data_row[15] = temp_time

        return data_row

    def read_csv_rows (self, numberOf_Last) :
        last_row = [-1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        filename = ENV.FILEPATH + 'IndexValuePanelData_' + "USDCAD_H4.csv"
        while(1):
            try :
                data = []
                with open(filename, mode='r') as csv_file:
                    last_number_rows = deque(csv_file, numberOf_Last + 1)
                    for row in last_number_rows :
                        data_row = self.rowToFloat(row.split(","))
                        data.append(data_row)
                last_row = data.pop()
                if last_row[16] + last_row[17] + last_row[18] + last_row[19] >= 95.99 :
                    data.append(last_row)
                return {'last_row' : last_row, 'data' : data}
            except IOError as x:
                print  ("couldn't read this file on this spot")

    # get the TVA infos from the last row of the source asset
    def monitorTVA(self) :

        self.first_flag = 0

        data = self.read_csv_rows(2)
        cur_row = data['data'].pop()
        past_row = data['data'].pop()

        print (self.src_file_name, "CURRENT_ROW", cur_row[16])

        if self.last_print == "C":
            #Printing B LOGIC
            if cur_row[16] > 0:
                self.printBSC("B", cur_row, past_row)
                return
            if cur_row[16] < 0:
                self.printBSC("S", cur_row, past_row)
                return

        elif self.last_print == "B" :
            if cur_row[16] < 0:
                self.back_count = 10
                self.previous_printing = "B"
                self.printBSC("C", cur_row, past_row)
                return

        elif self.last_print == "S" :
            if cur_row[16] > 0:
                self.back_count = 10
                self.previous_printing = "S"
                self.printBSC("C", cur_row, past_row)
                return

        self.printBSC("DO NOTHING", cur_row, past_row)

    def run(self):
        #initial datas
        self.initialData()

        #inital remaing time and monitor TVA with the rule
        time_cnt = self.getRemainTime_monitorTVA()
        

        while time_cnt < ENV.CYCLE_TIME:
            cur_time = self.getCurrentGmtTime()
            minute = cur_time.minute
            hour = cur_time.hour
            second = cur_time.second
            # get the start time perf_count
            start_time = time.perf_counter()

            self.countChanged.emit(time_cnt)

            # if self.first_flag == 0 and time_cnt % ENV.CHECK_INDEX_DURATION_TIME < ENV.REFRESH_TIME :
            #     self.monitorIndexValues()
            time_tmp = (minute * 60 + second) % ENV.CYCLE_TIME - (ENV.CYCLE_TIME / 4)
            if time_tmp >= 5 and time_tmp <= 10 and hour <= self.end_hour and hour >= self.start_hour:
                self.monitorTVA()


            if self.back_count >= 0 :
                self.back_count -= ENV.REFRESH_TIME

            if self.back_count < 0 :
                if self.previous_printing == "S" :
                    self.printBSC("B", ["Printing B after S"], [])
                if self.previous_printing == "B" :
                    self.printBSC("S", ["Printing S after B"], [])

            # get the end time perf_count
            end_time = time.perf_counter()
            time.sleep(ENV.REFRESH_TIME - (end_time - start_time))
            time_cnt += ENV.REFRESH_TIME

        self.run()
