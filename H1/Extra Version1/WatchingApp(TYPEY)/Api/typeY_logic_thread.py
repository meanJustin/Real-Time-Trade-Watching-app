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
        second = cur_time.second

        if minute == 0 and second <= 5:
            self.monitorTVA(4)

        if minute == 15 and second <= 5:
            self.monitorTVA(1)

        if minute == 30 and second <= 5:
            self.monitorTVA(2)

        if minute == 45 and second <= 5:
            self.monitorTVA(3)

        cur_time = self.getCurrentGmtTime()
        minute = cur_time.minute % 15

        #remain the next time
        return minute * 60 + cur_time.second


    def log_detail(self, detailData) :
        file_name = ENV.MASTERFILEPATH + 'TypeY' + '_info.csv'
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
        file = open(ENV.MASTERFILEPATH + ENV.TYPEY_PRINT, "r+")
        lines = file.readlines()
        lines.pop()
        file = open(ENV.MASTERFILEPATH + ENV.TYPEY_PRINT, "w+")
        file.writelines(lines)

    #print B on the log and csv and write the log into the info
    def printBSC(self, print_char, cur_TVAs, past_TVAs) :

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
            ',TypeY' + ':'+ print_char
        ]

        logData = [
            self.src_file_name[0:self.src_file_name.find("_")] + 
            ','+ 'Date:'+ date_str +
            ',TypeY' + ':'+ print_char + "  " + 
            "Current Row : " + str(cur_TVAs) + " " +
            "Previous Row : " + str(past_TVAs)
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
        file_name = ENV.MASTERFILEPATH + 'TypeY' + '.csv'

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
    def read_Previous_row (self, filename) :
        last_row = []
        previous_row = []
        while(1):
            try :
                with open(filename, mode='r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    line_cnt = 0
                    for row in csv_reader :
                        previous_row = last_row
                        last_row = row
                if previous_row[2] == "Index 1" :
                    return [-1, 0,0,0,0,0,0,0,0,0,0,0,0]
                return previous_row
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
    def monitorTVA(self, cur_TVA) :

        print ("CURRENT TVA : ", cur_TVA)
        cur_TVA += 15

        last_row = []
        previous_row = []
        last_3_row = []
        while(1):
            try :
                with open(ENV.FILEPATH + 'IndexValuePanelData_' + self.src_file_name, mode='r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    line_cnt = 0
                    for row in csv_reader :
                        last_3_row = previous_row
                        previous_row = last_row
                        last_row = row
                if previous_row[2] == "Index 1" :
                    last_3_row = [-1, 0,0,0,0,0,0,0,0,0,0,0,0]
                    previous_row = [-1, 0,0,0,0,0,0,0,0,0,0,0,0]
                break
            except IOError as x:
                print (ENV.FILEPATH + 'IndexValuePanelData_' + self.src_file_name)
                print  ("couldn't read this file on this spot")


        bottom_row = last_row
        last_row = previous_row
        previous_row = last_3_row

        last_row.pop(15)
        bottom_row.pop(15)
        previous_row.pop(15)
        last_row.pop(0)
        previous_row.pop(0)
        bottom_row.pop(0)

        last_row.insert(0, 0)
        previous_row.insert(0, 0)
        bottom_row.insert(0, 0)
        last_row.insert(15, 0)
        previous_row.insert(15, 0)
        bottom_row.insert(15, 0)

        #make an array which reflects the current TVA values and close price
        cur_TVAs = []
        for item in last_row :
            cur_TVAs.append(float(item))

        #make an array which reflects the last TVA values and close price
        past_TVAs = []
        for item in previous_row :
            past_TVAs.append(float(item))

        #make an array which reflects the last TVA values and close price
        bottom_TVAs = []
        for item in bottom_row :
            bottom_TVAs.append(float(item))

        print (cur_TVAs)
        print (past_TVAs)


        if self.last_print == "C" and cur_TVA == 19:

            # There is 0 so we failed
            if cur_TVAs[16] == 0 or cur_TVAs[17] == 0 or cur_TVAs[18] == 0 or cur_TVAs[19] == 0 :
                return
            if past_TVAs[16] == 0 or past_TVAs[17] == 0 or past_TVAs[18] == 0 or past_TVAs[19] == 0 :
                return

            #Printing B LOGIC
            if cur_TVAs[4] >= 80 or cur_TVAs[5] >= 80 or cur_TVAs[4] + cur_TVAs[5] >= 80:
                if cur_TVAs[16] > past_TVAs[16] and cur_TVAs[17] > past_TVAs[17] and cur_TVAs[18] > past_TVAs[18] and cur_TVAs[19] > past_TVAs[19] :
                    if cur_TVAs[7] > past_TVAs[7] and cur_TVAs[8] > past_TVAs[8] and cur_TVAs[9] > past_TVAs[9] :
                        self.printBSC("B", cur_TVAs, past_TVAs)
                        return

            if cur_TVAs[2] >= 80 or cur_TVAs[3] >= 80 or cur_TVAs[3] + cur_TVAs[2] >= 80:
                if cur_TVAs[16] > past_TVAs[16] and cur_TVAs[17] > past_TVAs[17] and cur_TVAs[18] > past_TVAs[18] and cur_TVAs[19] > past_TVAs[19] :
                    if cur_TVAs[7] > past_TVAs[7] and cur_TVAs[8] > past_TVAs[8] and cur_TVAs[9] > past_TVAs[9] :
                        self.printBSC("B", cur_TVAs, past_TVAs)
                        return

            #Printing S LOGIC
            if cur_TVAs[4] >= 80 or cur_TVAs[5] >= 80 or cur_TVAs[4] + cur_TVAs[5] >= 80:
                if cur_TVAs[16] < past_TVAs[16] and cur_TVAs[17] < past_TVAs[17] and cur_TVAs[18] < past_TVAs[18] and cur_TVAs[19] < past_TVAs[19] :
                    if cur_TVAs[7] < past_TVAs[7] and cur_TVAs[8] < past_TVAs[8] and cur_TVAs[9] < past_TVAs[9] :
                        self.printBSC("S", cur_TVAs, past_TVAs)
                        return

            if cur_TVAs[2] >= 80 or cur_TVAs[3] >= 80 or cur_TVAs[3] + cur_TVAs[2] >= 80:
                if cur_TVAs[16] < past_TVAs[16] and cur_TVAs[17] < past_TVAs[17] and cur_TVAs[18] < past_TVAs[18] and cur_TVAs[19] < past_TVAs[19] :
                    if cur_TVAs[7] < past_TVAs[7] and cur_TVAs[8] < past_TVAs[8] and cur_TVAs[9] < past_TVAs[9] :
                        self.printBSC("S", cur_TVAs, past_TVAs)
                        return


        elif self.last_print == "B":
            #PRINTING C and DO NOTHING LOGIC
            if bottom_TVAs[cur_TVA] > 0 and cur_TVAs[cur_TVA] > 0 and bottom_TVAs[cur_TVA] < cur_TVAs[cur_TVA] :
                self.printBSC("C", bottom_TVAs, cur_TVAs)
            elif bottom_TVAs[cur_TVA] < 0 and cur_TVAs[cur_TVA] < 0 and bottom_TVAs[cur_TVA] < cur_TVAs[cur_TVA] :
                self.printBSC("C", bottom_TVAs, cur_TVAs)
            elif bottom_TVAs[cur_TVA] < 0 and cur_TVAs[cur_TVA] > 0 :
                self.printBSC("C", bottom_TVAs, cur_TVAs)
            elif bottom_TVAs[cur_TVA] == 0 or cur_TVAs[cur_TVA] == 0 :
                self.printBSC("C", bottom_TVAs, cur_TVAs)
            else : 
                self.printBSC("DO NOTHING", bottom_TVAs, cur_TVAs)


        elif self.last_print == "S":
            #PRINTING C and DO NOTHING LOGIC
            if bottom_TVAs[cur_TVA] > 0 and cur_TVAs[cur_TVA] > 0 and bottom_TVAs[cur_TVA] > cur_TVAs[cur_TVA] :
                self.printBSC("C", bottom_TVAs, cur_TVAs)
            elif bottom_TVAs[cur_TVA] < 0 and cur_TVAs[cur_TVA] < 0 and bottom_TVAs[cur_TVA] > cur_TVAs[cur_TVA] :
                self.printBSC("C", bottom_TVAs, cur_TVAs)
            elif bottom_TVAs[cur_TVA] > 0 and cur_TVAs[cur_TVA] < 0 :
                self.printBSC("C", bottom_TVAs, cur_TVAs)
            elif bottom_TVAs[cur_TVA] == 0 or cur_TVAs[cur_TVA] == 0 :
                self.printBSC("C", bottom_TVAs, cur_TVAs)
            else : 
                self.printBSC("DO NOTHING", cur_TVAs, cur_TVAs)

    def run(self):
        #initial datas
        self.initialData()
        # print (self.close_Candle_B, self.close_Candle_S)

        #inital remaing time and monitor TVA with the rule
        time_cnt = self.getRemainTime_monitorTVA()
        # print ("remaing time for next 15min", time_cnt)
        
        while time_cnt <= ENV.CYCLE_TIME:
            # get the start time perf_count
            start_time = time.perf_counter()

            self.countChanged.emit(time_cnt)

            time_cnt += ENV.REFRESH_TIME
            # get the end time perf_count
            end_time = time.perf_counter()

            time.sleep(ENV.REFRESH_TIME - (end_time - start_time))

        self.run()
