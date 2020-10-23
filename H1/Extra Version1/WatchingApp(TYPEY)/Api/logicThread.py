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
    run_type = -1
    pos_neg = 0

    def initialData(self) :
        #the previous row of the latest row
        self.previous_row = []

        #the just before lastest state row
        self.previous_data_row = []

        #the 10min start row        
        self.original_row = []

        #how much changed from the original
        self.inc_value = [0,0,0,0,0]

        #the latest row and current data array
        self.cur_row = []

        #the value which contain D1's last touch
        self.d1_last_touch = 0

        #set the state of printing B and S
        self.stateB = [1]
        self.stateS = [1]


    #write the new data on the last row of the data
    def append_list_as_row(self, data):
        # Open file in append mode
        file_name = ENV.MASTERFILEPATH + 'Type' + str(self.run_type) + '.csv'

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


    # log the C printing information on the new info file and the app log
    def log_detail(self, detailData) :
        file_name = ENV.MASTERFILEPATH + 'Type' + str(self.run_type) + '_info.csv'
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

    #print C function
    def printC(self, detail) :
        self.stateB[0] = -1
        self.stateS[0] = -1
        if self.last_print == "C":
            return
        self.last_print = 'C'

        # datetime object containing current date and time
        format = "%Y.%m.%d,%H:%M:%S"
        # Current time in GMT
        now_gmt = datetime.now(timezone('GMT'))
        now_asia = now_gmt.astimezone(timezone('Europe/Moscow'))
        date_str = now_asia.strftime(format)

        myData = [
            self.src_file_name[0:self.src_file_name.find("_")] + 
            ','+ 'Date:'+ date_str +
            ',' + 'Type' + str(self.run_type) + ':'+"C"]
        str_data = " "

        myDetailData = [
            self.src_file_name[0:self.src_file_name.find("_")] + 
            ','+ 'Date:'+ date_str +
            ',' + 'Type' + str(self.run_type) + ':'+"C" + "   : It's occured by " + detail]

        # Appending a row to csv with missing entries
        self.append_list_as_row(myData)
        self.printChanged.emit(str_data.join(myDetailData))

        # leave log on the panel and on the file.
        self.log_detail(detail, myDetailData)
        return

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
                previous_row.insert(0, "row")
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
                last_row.insert(0, "row")
                return last_row
            except IOError as x:
                print  ("couldn't read this file on this spot")

    #monitor the state change in every upgrade time
    def monitor_state(self) -> int:

        #mointor the last added point in D1 csv file
        if self.run_type == 0 :
            if (float(self.d1_current_row[2]) > float(self.d1_previous_data[2])) :
                self.d1_last_touch = 1
            if (float(self.d1_current_row[3]) > float(self.d1_previous_data[3])) :
                self.d1_last_touch = 2
            if (float(self.d1_current_row[4]) > float(self.d1_previous_data[4])) :
                self.d1_last_touch = 3
            if (float(self.d1_current_row[5]) > float(self.d1_previous_data[5])) :
                self.d1_last_touch = 4
            if (float(self.d1_current_row[6]) > float(self.d1_previous_data[6])) :
                self.d1_last_touch = 5

        #monitor any increase cnt in array index0-5
        if (float(self.cur_row[2]) > float(self.previous_data_row[2])) :
            self.inc_cnt[0] += 1
        if (float(self.cur_row[3]) > float(self.previous_data_row[3])) :
            self.inc_cnt[1] += 1
        if (float(self.cur_row[4]) > float(self.previous_data_row[4])) :
            self.inc_cnt[2] += 1
        if (float(self.cur_row[5]) > float(self.previous_data_row[5])) :
            self.inc_cnt[3] += 1
        if (float(self.cur_row[6]) > float(self.previous_data_row[6])) :
            self.inc_cnt[4] += 1

        #caculate the increase value in array index0-5
        self.inc_value[0] = float(self.cur_row[2]) - float(self.original_row[2])
        self.inc_value[1] = float(self.cur_row[3]) - float(self.original_row[3])
        self.inc_value[2] = float(self.cur_row[4]) - float(self.original_row[4])
        self.inc_value[3] = float(self.cur_row[5]) - float(self.original_row[5])
        self.inc_value[4] = float(self.cur_row[6]) - float(self.original_row[6])

        #catch any changes in index0-indx5
        if self.inc_cnt[0] <= 0 and self.inc_cnt[1] <= 0 and self.inc_cnt[2] <= 0 and self.inc_cnt[3] <= 0 and self.inc_cnt[4] <= 0 :
            return 0


        if self.inc_cnt[0] == 0 and self.inc_cnt[1] == 0 and self.inc_cnt[2] == 0 :
            self.stateB[0] = 2;

            if self.last_print == "B" and self.inc_value[3] >= 1 and self.inc_value[4] >= 1 :
                #mixed
                if self.cur_row[10] > self.previous_row[8] :
                    #current close price just passed the previous high price
                    self.printC("C#2 -- During the B: current close price just passed the previous high price!")
                if self.cur_row[10] < self.previous_row[10] :
                    #current close price drops below the previous close
                    self.printC("C#2 -- During the B: Current close price just drops below the previous close price!")

        if self.inc_cnt[0] == 0 and self.inc_cnt[3] == 0 and self.inc_cnt[4] == 0 :
            self.stateS[0] = 2;
            if self.last_print == "S" and self.inc_value[1] >= 1 and self.inc_value[2] >= 1 :
                #mixed
                if self.cur_row[10] < self.previous_row[9] :
                    #current row price just drops below the Previous low
                    self.printC("C#2 -- During the S: Current close price just drops below the Previous low price!")
                if self.cur_row[10] > self.previous_row[10] :
                    #current row price passes above Previous CLOSE
                    self.printC("C#2 -- During the S: Current close price just passes above the Previous Close price!")

        # touch 1,2,3 during the B state
        if self.stateB[0] == 2 and self.inc_cnt[1] > 0 or self.inc_cnt[2] > 0 or self.inc_cnt[0] > 0:
            self.stateB[0] = -1
        # touch 1,4,5 during the C state
        if self.stateS[0] == 2 and self.inc_cnt[3] > 0 or self.inc_cnt[4] > 0 or self.inc_cnt[0] > 0:
            self.stateS[0] = -1

        if self.last_print == "B" and self.stateB[0] == 2:
            if self.inc_value[1] + self.inc_value[2] >= 2:
                self.printC("C#1 -- During the B added full 2 points in Index1/2")
        if self.last_print == "S" and self.stateS[0] == 2:
            if self.inc_value[3] + self.inc_value[4] >= 2:
                self.printC("C#1 -- During the S added full 2 points in Index3/4")

        print (self.previous_data_row)
        print (self.cur_row)

        print ("===========EACH STATE==========")

        print (self.inc_cnt)
        print ("stateB:", self.stateB)
        print ("stateS:", self.stateS)

        print ("===========END OF ONE==========")

    def run(self):
        #initial datas
        self.initialData()

        #initial the increase of array
        time_cnt = 0

        self.previous_data_row = self.read_last_row(ENV.FILEPATH + 'IndexValuePanelData_' + self.src_file_name)
        self.original_row = self.previous_data_row
        self.previous_row = self.read_Previous_row(ENV.FILEPATH + 'IndexValuePanelData_' + self.src_file_name)

        print (self.previous_data_row)
        print (self.original_row)
        print (self.previous_row)

        #catch the lastest data from d1
        if self.run_type == 0:
            self.d1_previous_data = self.read_last_row(ENV.FILEPATH + 'IndexValuePanelData_' + self.d1_file_name)


        while time_cnt < ENV.CYCLE_TIME:
            start_time = time.perf_counter()
            time_cnt += ENV.REFRESH_TIME
            self.cur_row = self.read_last_row(ENV.FILEPATH + 'IndexValuePanelData_' + self.src_file_name)

            #catch the latest data from d1
            if self.run_type == 0:
                self.d1_current_row = self.read_last_row(ENV.FILEPATH + 'IndexValuePanelData_' + self.d1_file_name)

            self.monitor_state()
            self.countChanged.emit(time_cnt)
            end_time = time.perf_counter()

            #save the previous row
            self.previous_data_row = self.cur_row

            #save the previous data of d1 for type0
            if self.run_type == 0:
                self.d1_previous_data = self.d1_current_row

            time.sleep(ENV.REFRESH_TIME)

        print_str = " "
        if self.stateB[0] == 2:
            print_str = 'B'
        if self.stateS[0] == 2:
            print_str = "S"


        #for type0 logic -> monitor d1
        if self.run_type == 0:
            if self.d1_last_touch == 1 :
                print_str = " "
            if self.d1_last_touch == 2 or self.d1_last_touch == 3:
                print_str = "S"
            if self.d1_last_touch == 4 or self.d1_last_touch == 5:
                print_str = "B"


        if self.last_print == "C":

            print (print_str, self.last_print)

            self.last_print = print_str
            format = "%Y.%m.%d,%H:%M:%S"
            # Current time in GMT
            now_gmt = datetime.now(timezone('GMT'))
            now_asia = now_gmt.astimezone(timezone('Europe/Moscow'))
            date_str = now_asia.strftime(format)

            myData = [
                self.src_file_name[0:self.src_file_name.find("_")] + 
                ','+ 'Date:'+ date_str+
                ',Type' + str(self.run_type) + ':'+ print_str
            ]
            # Appending a row to csv with missing entries
            self.append_list_as_row(myData)
            self.log_detail(myData)
            str_data = " "
            self.printChanged.emit(str_data.join(myData))

        self.run()
