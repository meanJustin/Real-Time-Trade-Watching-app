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
    countChanged_FOR_0_24 = pyqtSignal(int)
    countChanged_FOR_1_23 = pyqtSignal(int)
    printChanged = pyqtSignal(str)

    src_file_name = " "
    last_print = "C"
    first_flag = 1
    start_hour = 0
    end_hour = 24

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
        hour = cur_time.hour
        minute = cur_time.minute
        second = cur_time.second

        if (hour - self.start_hour) % 4 == 0 and hour >= self.start_hour and hour <= self.end_hour :
            if minute == 0 :
                if second >= 5 and second <= 10 :
                    self.monitorAssetsData()

        #remain the next time
        return ((hour - self.start_hour) * 3600 + minute * 60 + second - 5) % ENV.CYCLE_TIME

    def log_detail(self, detailData) :
        file_name = ENV.MASTERFILEPATH + 'TypeX' + '_info.csv'
        #represent the writed data into the console
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
        file = open(ENV.MASTERFILEPATH + ENV.TYPEX_PRINT, "r+")
        lines = file.readlines()
        lines.pop()
        file = open(ENV.MASTERFILEPATH + ENV.TYPEX_PRINT, "w+")
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
            ',TypeX' + ':'+ print_char
        ]

        logData = [
            self.src_file_name[0:self.src_file_name.find("_")] + 
            ','+ 'Date:'+ date_str +
            ',TypeX' + ':'+ print_char + "  " + 
            "Current Row : " + str(cur_row) + " " +
            "Previous Row : " + str(past_row)
        ]

        if print_char == "B" or print_char == "S" :
            logData = [
                self.src_file_name[0:self.src_file_name.find("_")] + 
                ','+ 'Date:'+ date_str +
                ',TypeX' + ':'+ print_char + "  " + 
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
        file_name = ENV.MASTERFILEPATH + 'TypeX' + '.csv'

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

    def B_Checking_Algo(self, cur_row, data_rows) :
        if cur_row[19] <= 0 :
            return False
        self.current_Price = cur_row[9]

        total_Sum_Low_Price = 0
        for row in data_rows :
            total_Sum_Low_Price += data_rows[8]

        if total_Sum_Low_Price / 15 <= self.current_Price :
            return False
        return True

    def S_Checking_Algo(self, cur_row, data_rows) :
        if cur_row[19] >= 0 :
            return False
        self.current_Price = cur_row[9]

        total_Sum_High_Price = 0
        for row in data_rows :
            total_Sum_High_Price += data_rows[7]

        if total_Sum_High_Price / 15 >= self.current_Price :
            return False
        return True

    # get the TVA infos from the last row of the source asset
    def monitorAssetsData(self) :

        self.first_flag = 0

        data = self.read_csv_rows(16)
        data_rows = data['data']
        cur_row = data_rows.pop()

        cur_time = self.getCurrentGmtTime()
        hour = cur_time.hour

        cur_TVA = (hour + 24 - self.start_hour) % 4
        # when we are on TVA4 then we should watch the previous and the past of previous line
        if  cur_TVA == 0:
            cur_TVA += 4

        if self.last_print == "C":
            #Printing B LOGIC
            if self.B_Checking_Algo(cur_row, data_rows):
                self.printBSC("B", cur_row, [])
                return
            #Printing S LOGIC
            if self.S_Checking_Algo(cur_row, data_rows):
                self.printBSC("S", cur_row, [])
                return

        elif self.last_print == "B" :
            #Printing C Logic
            if cur_row[cur_TVA + 15] < 0 or cur_row[9] > self.current_Price:
                self.printBSC("C", cur_row, [])

                if self.S_Checking_Algo(cur_row, data_rows):
                    self.printBSC("S", cur_row, [])
                    return
                return
        elif self.last_print == "S" :
            #Printing C Logic
            if cur_row[cur_TVA + 15] > 0 or cur_row[9] < self.current_Price:
                self.printBSC("C", cur_row, [])

                if self.B_Checking_Algo(cur_row, data_rows):
                    self.printBSC("B", cur_row, [])
                    return
                return
        self.printBSC("DO NOTHING", cur_row, [])


    def run(self):
        #initial datas
        self.initialData()

        #inital remaing time and monitor TVA with the rule
        time_cnt = self.getRemainTime_monitorTVA()
        
        while time_cnt < ENV.CYCLE_TIME:
            # get the start time perf_count
            start_time = time.perf_counter()

            if self.start_hour == 0 :
                self.countChanged_FOR_0_24.emit(time_cnt)

            if self.start_hour == 1 :
                self.countChanged_FOR_1_23.emit(time_cnt)

            # get the end time perf_count
            end_time = time.perf_counter()
            time.sleep(ENV.REFRESH_TIME - (end_time - start_time))
            time_cnt += ENV.REFRESH_TIME

        self.run()
