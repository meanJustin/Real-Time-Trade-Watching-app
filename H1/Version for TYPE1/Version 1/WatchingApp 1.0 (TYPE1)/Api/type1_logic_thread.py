import sys
from PyQt5.QtCore import QThread, pyqtSignal
from csv import writer
import csv

###progress bar
import time
from datetime import datetime
from pytz import timezone

import env as ENV


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

        if minute == 0 and second <= 5 and hour <= self.end_hour and hour >= self.start_hour:
            self.monitorIndexValues()

        cur_time = self.getCurrentGmtTime()
        minute = cur_time.minute

        #remain the next time
        return minute * 60 + cur_time.second

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
        print(data)

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
    def read_CUR_PREVIOUS_row (self, filename) :
        last_row = []
        previous_row = []
        last_3_row = []
        filename = ENV.FILEPATH + 'IndexValuePanelData_' + filename
        while(1):
            try :
                with open(filename, mode='r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    for row in csv_reader :
                        last_3_row = previous_row
                        previous_row = last_row
                        last_row = row
                if previous_row[2] == "Index 1" :
                    return [-1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

                data = {}
                data['last_row'] = previous_row
                data['previous_row'] = last_3_row

                return data
            except IOError as x:
                print  ("couldn't read this file on this spot")

    #read the last row from the csv file
    def read_last_row(self, filename) :
        last_row = []

        while(1):
            try :
                with open(filename, mode='r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    line_cnt = 0
                    for row in csv_reader :
                        last_row = row
                return last_row
            except IOError as x:
                print  ("couldn't read this file on this spot")


    # get the TVA infos from the last row of the source asset
    def monitorIndexValues(self) :

        self.first_flag = 0

        last_row = []
        previous_row = []
        last_3_row = []

        data = self.read_CUR_PREVIOUS_row(self.src_file_name)
        last_row = data['last_row']
        previous_row = data['previous_row']
        
        #change date values to 0 because of floating converting.
        last_row[0] = 0
        previous_row[0] = 0
        last_row[15] = 0
        previous_row[15] = 0

        #make an array which reflects the current TVA values and close price
        cur_row = []
        for item in last_row :
            cur_row.append(float(item))

        #make an array which reflects the last TVA values and close price
        past_row = []
        for item in previous_row :
            past_row.append(float(item))

        print (cur_row)
        print (past_row)

        if self.last_print == "C":

            #Printing B LOGIC
            if cur_row[4] + cur_row[5] >= 75 and cur_row[1] < 10:
                if cur_row[16] + cur_row[17] + cur_row[18] + cur_row[19] > 0 :
                    self.printBSC("B", cur_row, past_row)
                    return

            #Printing S LOGIC
            if cur_row[2] + cur_row[3] >= 75 and cur_row[1] < 10:
                if cur_row[16] + cur_row[17] + cur_row[18] + cur_row[19] < 0 :
                    self.printBSC("S", cur_row, past_row)
                    return

        elif self.last_print == "B" :
            if cur_row[16] + cur_row[17] + cur_row[18] + cur_row[19] <= 0 :
                self.printBSC("C", cur_row, past_row)
                return

        elif self.last_print == "S" :
            if cur_row[16] + cur_row[17] + cur_row[18] + cur_row[19] >= 0 :
                self.printBSC("C", cur_row, past_row)
                return
        
        self.printBSC("DO NOTHING", cur_row, past_row)
    
    def run(self):
        #initial datas
        self.initialData()

        #inital remaing time and monitor TVA with the rule
        time_cnt = self.getRemainTime_monitorTVA()
        
        while time_cnt < ENV.CYCLE_TIME:
            # get the start time perf_count
            start_time = time.perf_counter()

            self.countChanged.emit(time_cnt)

            # if self.first_flag == 0 and time_cnt % ENV.CHECK_INDEX_DURATION_TIME < ENV.REFRESH_TIME :
            #     self.monitorIndexValues()

            # get the end time perf_count
            end_time = time.perf_counter()
            time.sleep(ENV.REFRESH_TIME - (end_time - start_time))
            time_cnt += ENV.REFRESH_TIME

        self.run()
