from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton,QProgressBar, QDialog, QListWidget,QGridLayout
from PyQt5.QtCore import QTimer, QTime, Qt, pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import sys, os, traceback, types
from pytz import timezone
import pandas as pd
import pathlib
import csv

#import timezone module
from datetime import datetime
#import enviroment values
import env as ENV
#import thread apis
import Api.typeX_logic_thread as TYPEX_LOGIC_THREAD

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

		self.setWindowTitle('Watching SVC Files FOR TYPEX-ABC')
		
		#button
		self.button = QPushButton('Start', self)
		self.button.setStyleSheet("color: black; font-size : 23px; border : 3px solid black")
		self.button.setGeometry(40, 30, 130, 40)
		self.button.clicked.connect(self.onButtonClick)

		#progressbar for duration 0-24
		self.progress_0_24 = QProgressBar(self)
		self.progress_0_24.setGeometry(40, 90, 420, 15)
		self.progress_0_24.setMaximum(ENV.CYCLE_TIME)

		#progressbar for duration 0-24
		self.progress_1_23 = QProgressBar(self)
		self.progress_1_23.setGeometry(40, 120, 420, 15)
		self.progress_1_23.setMaximum(ENV.CYCLE_TIME)
		
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

	def onButtonClick(self):

		cur_time = datetime.now(timezone('GMT')).astimezone(timezone('Europe/Moscow'))
		date = cur_time.day
		if date < 25 and date > 7 :
			return

		if self.start_flag == 0 :
			return
		self.start_flag = 0

		try:
		    with open(ENV.MASTERFILEPATH + ENV.TYPEX_PRINT):
		        os.remove(ENV.MASTERFILEPATH + ENV.TYPEX_PRINT)
		        print ("Old TYPEX.csv file will be removed and create a new one.")
		except IOError:
			print ("New TYPEX.csv file will be created")

		try:
		    with open(ENV.MASTERFILEPATH + "TypeX_info.csv"):
		        os.remove(ENV.MASTERFILEPATH + "TypeX_info.csv")
		        print ("Old TYPEX_info.csv file will be removed and create a new one.")
		except IOError:
			print ("New TYPEX_info.csv file will be created")

		#for typeX processes
		print ("======================================OPENING MASTERSHEET EXCEL FILES================================")
		print ("-------------------------------------- TYPEX MASTERSHEET ------------------------------------")
		
		#reading for type 0 files
		mastersheet = pd.read_excel (ENV.MASTERFILEPATH + ENV.TYPEX_MASTER)
		records = mastersheet.to_records()
		self.typeX_Run = []
		row_index = 2

		for row in records :
			file = pathlib.Path(ENV.FILEPATH + 'IndexValuePanelData_' + row[1] + ".csv")

			if file.exists() == True :
				print (file)
				print ("---------------THIS FILE EXISTS--------------")
				index = len(self.typeX_Run)

				#classify this file is positive or negative
				self.typeX_Run.append(TYPEX_LOGIC_THREAD.External())

				self.typeX_Run[index].countChanged_FOR_0_24.connect(self.onCountChanged_FOR_0_24)
				self.typeX_Run[index].countChanged_FOR_1_23.connect(self.onCountChanged_FOR_1_23)
				self.typeX_Run[index].printChanged.connect(self.onPrintChanged)
				self.typeX_Run[index].src_file_name = row[1] + ".csv"
				
				if row[5] == "24HRS" :
					self.typeX_Run[index].start_hour = 0
					self.typeX_Run[index].end_hour = 24
				else :
					self.typeX_Run[index].start_hour = int(row[4])
					self.typeX_Run[index].end_hour = int(row[5])

				self.typeX_Run[index].start()
			row_index += 1


	def onCountChanged_FOR_0_24(self, value):
		self.progress_0_24.setValue(value)

	def onCountChanged_FOR_1_23(self, value):
		self.progress_1_23.setValue(value)

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
