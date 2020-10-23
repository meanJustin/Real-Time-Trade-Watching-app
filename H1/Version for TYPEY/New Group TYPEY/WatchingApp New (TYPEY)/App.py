from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton,QProgressBar, QDialog, QListWidget,QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QTime, Qt, pyqtSlot, QThread, pyqtSignal

import pandas as pd

import sys, os, traceback, types
import pathlib
from pytz import timezone

#import timezone module
from datetime import datetime
import pytz 
#import enviroment values
import env as ENV
#import thread apis
import Api.typeY_logic_thread as TYPEY_LOGIC_THREAD

#When the Estimate Button is clicked
class MainWindow(QWidget):
	"""
	Simple dialog that consists of a Progress Bar and a Button.
	Clicking on the button results in the start of a timer and
	updates the progress bar.
	"""
	start_flag = 1

	def __init__(self):
		QWidget.__init__(self)
		self.setStyleSheet("color: black; background-color: rgb(0,162,232);")
		self.setGeometry(60,80,500,600)

		self.setWindowTitle('Watching SVC Files FOR TYPEY-ABC')
		
		#button
		self.button = QPushButton('Start', self)
		self.button.setStyleSheet("color: black; font-size : 23px; border : 3px solid black")
		self.button.setGeometry(40, 30, 130, 40)
		self.button.clicked.connect(self.onButtonClick)

		#progressbar
		self.progress = QProgressBar(self)
		self.progress.setGeometry(40, 100, 420, 15)
		self.progress.setMaximum(ENV.CYCLE_TIME)


		#List label
		list_label = QLabel(self)
		list_label.setStyleSheet("color: black; font-size : 23px;")
		list_label.setText("PRINTING LOG")
		list_label.setGeometry(60, 160, 200, 30)
		#listbox
		self.listwidget = QListWidget(self)
		self.listwidget.setStyleSheet("color: black; border : 3px solid black; font-size : 16px")
		self.listwidget.setGeometry(40, 200, 420, 300)

		self.time_label = QLabel(self)
		self.time_label.setStyleSheet("color: black; font-size : 20px; border : 3px solid black")
		self.time_label.setText("")
		self.time_label.setGeometry(40, 520, 300, 30)

		timer = QTimer(self)
		timer.timeout.connect(self.showTime)
		timer.start(1000)

		self.show()
		self.start_flag = 1

	def onButtonClick(self):
		if self.start_flag == 0 :
			print ("It started already")
			return
		self.start_flag = 0
		print (self.start_flag)
		try:
		    with open(ENV.MASTERFILEPATH + ENV.TYPEY_PRINT):
		        os.remove(ENV.MASTERFILEPATH + ENV.TYPEY_PRINT)
		        print ("Old TYPEY.csv file will be removed and create a new one.")
		except IOError:
			print ("New TYPEY.csv file will be created")

		try:
		    with open(ENV.MASTERFILEPATH + "TypeY_info.csv"):
		        os.remove(ENV.MASTERFILEPATH + "TypeY_info.csv")
		        print ("Old TYPEY_info.csv file will be removed and create a new one.")
		except IOError:
			print ("New TYPEY_info.csv file will be created")

		#for typeY processes
		print ("======================================OPENING MASTERSHEET EXCEL FILES================================")
		print ("-------------------------------------- TYPEY MASTERSHEET ------------------------------------")
		
		#read the master sheet file for each csv files		
		mastersheet = pd.read_excel (ENV.MASTERFILEPATH + ENV.TYPEY_MASTER_FILENAME)
		records = mastersheet.to_records()

		groupmastersheet = pd.read_excel(ENV.MASTERFILEPATH + ENV.GROUP_TYPEY_MASTER_FILENAME)
		group_cnt = len(groupmastersheet.columns)
		key_values = list(groupmastersheet.keys())
		if key_values[-1] == "SKIP n/a" :
			group_cnt -= 1

		self.typeY_Run = []

		for x in range(0,group_cnt) :
			groupmastersheet = pd.read_excel(ENV.MASTERFILEPATH + ENV.GROUP_TYPEY_MASTER_FILENAME, usecols = [x])
			group_temp = groupmastersheet.to_records()

			#run new process for new group
			run_index = len(self.typeY_Run)
			self.typeY_Run.append(TYPEY_LOGIC_THREAD.External())
			self.typeY_Run[run_index].files = []
			index = 0
			while 1 :
				if type(group_temp[index][1]) == float:
					break
				#new file object created
				#read file name
				self.typeY_Run[run_index].files.append(group_temp[index][1])
				index += 1


			index += 1
			#for triggering B of TVA condition
			self.typeY_Run[run_index].Enter_B_INDEX_need = int(group_temp[index][1].replace("B: All Asset Index 4/5 = ", "").replace(" > + Total TVA Sum is Positive All Assets.", ""))
			index += 2

			#for triggering S of TVA condition
			self.typeY_Run[run_index].Print_C_IN_B_INDEX = int(group_temp[index][1][0: group_temp[index][1].find("but")].replace("C: If Index 4/5 drops below  < ", "").replace(" b", ""))
			self.typeY_Run[run_index].Print_C_IN_B_POS_CNT = int(group_temp[index][1][group_temp[index][1].find("TVA SUM is") : -1].replace("TVA SUM is ","").replace(" asset or of less positive",""))
			index += 2


			#for printing C in B of TVA condition
			self.typeY_Run[run_index].Enter_S_INDEX_need = int(group_temp[index][1].replace("S: All Asset Index 2/3 = ", "").replace(" > + Total TVA Sum is Negative All Assets.", ""))
			index += 2

			#for printing C in S of TVA condition
			self.typeY_Run[run_index].Print_C_IN_S_INDEX = int(group_temp[index][1][0: group_temp[index][1].find("but")].replace("C: If Index 2/3 drops below  < ", "").replace(" b", ""))
			self.typeY_Run[run_index].Print_C_IN_S_NEG_CNT = int(group_temp[index][1][group_temp[index][1].find("TVA SUM is") : -1].replace("TVA SUM is ","").replace(" asset or less Negative",""))
			index += 2


			#for starting time for this group
			self.typeY_Run[run_index].start_hour = int(group_temp[index][1].replace("Start : ", ""))
			index += 1

			#for ending time for this group
			self.typeY_Run[run_index].end_hour = int(group_temp[index][1].replace("End : ", ""))
			index += 2

			if len(group_temp) > index and group_temp[index][1] == "OPPOSITE" :
				self.typeY_Run[run_index].opposite = group_temp[index + 1][1]

			self.typeY_Run[run_index].countChanged.connect(self.onCountChanged)
			self.typeY_Run[run_index].printChanged.connect(self.onPrintChanged)
			
			self.typeY_Run[run_index].start()


	def onCountChanged(self, value):
		self.progress.setValue(value)

	def onPrintChanged(self, value) :
		self.listwidget.addItems([value])

	def showTime(self) :
		format = "%H:%M:%S"
		# Current time in UTC
		now_gmt = datetime.now(timezone('GMT'))
		gmt_time = now_gmt.astimezone(timezone('Europe/Moscow'))
		self.time_label.setText("GMT+3      " + gmt_time.strftime(format))


if __name__ == "__main__":
	app = QApplication(sys.argv)
	screen = MainWindow()
	screen.show()
	sys.exit(app.exec_())
