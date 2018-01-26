import sys, os
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from functools import partial
import imgkit
import urllib
from PIL import Image
import io, piexif

class MainDialog(QDialog):
	def __init__(self, parent=None):
		super(MainDialog, self).__init__(parent)
		self.initUI()

	def initUI(self):
		self.setWindowTitle("Web Capture")

		self.urlLabel = QLabel("Url:")
		self.urlValue = QLineEdit(self)
		self.goBtn = QPushButton("Go")
		self.goBtn.clicked.connect(self.go_url)
		self.fullBtn = QPushButton("Full")
		self.fullBtn.clicked.connect(partial(self.capture,1))
		self.curBtn = QPushButton("Current")
		self.curBtn.clicked.connect(partial(self.capture,2))
		self.scrBtn = QPushButton("Script")
		self.scrBtn.clicked.connect(partial(self.capture,3))

		urlLayout = QGridLayout()
		urlLayout.setAlignment(Qt.AlignLeft)
		urlLayout.addWidget(self.urlLabel,0,0)
		urlLayout.addWidget(self.urlValue,0,1)
		urlLayout.addWidget(self.goBtn,0,2)
		urlLayout.addWidget(self.fullBtn,0,3)
		urlLayout.addWidget(self.curBtn,0,4)
		urlLayout.addWidget(self.scrBtn,0,5)

		self.web = QWebView()
		self.web.load(QUrl("https://www.google.com"))

		buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
		buttonBox.rejected.connect(self.reject)

		mainLayout = QVBoxLayout()
		mainLayout.addLayout(urlLayout)
		mainLayout.addWidget(self.web)
		mainLayout.addWidget(buttonBox)

		self.setLayout(mainLayout)
		self.show()

	def go_url(self):
		self.url = str(self.urlValue.text())
		if self.url.startswith("http") == False:
			self.url = "http://" + self.url
		self.web.load(QUrl(self.url))

	def capture(self, opt):		
		warnBox = QMessageBox(QMessageBox.Warning, "Warning", "Failed to save image", QMessageBox.NoButton, self)
		warnBox.addButton("&Close", QMessageBox.RejectRole)

		url = self.url
		self.web.load(QUrl(url))
		#print self.web.title()
		now = getTime()
		if opt == 1:
			try:
				imgkit.from_url(url, "Full_" +self.web.title()+"_"+now+".jpg")
				insert_EXIF("Full_" +self.web.title()+"_"+now+".jpg",now)
				QMessageBox.information(self, "Success", "Capture Completed!")
			except:
				warnBox.exec_()
		elif opt == 2:				    	
			try:
				image = QImage(self.web.page().mainFrame().contentsSize(), QImage.Format_ARGB32)
				painter = QPainter(image)
				self.web.page().mainFrame().render(painter)
				painter.end()
				image.save("Part_"+self.web.title()+"_"+now+".jpg")							
				insert_EXIF("Part_"+self.web.title()+"_"+now+".jpg",now)
				QMessageBox.information(self, "Success", "Capture Completed!")
			except:
				warnBox.exec_()
		elif opt == 3:
			try:
				data = urllib.urlopen(url).read()
				f = open("Src_"+self.web.title()+"_"+now+ ".html", "w")
				f.write(data)
				f.close()
				QMessageBox.information(self, "Success", "Capture Completed!")
			except:
				warnBox.exec_()

def getTime():
	now = time.localtime()
	if now.tm_mon < 10:
		mon = "0"+str(now.tm_mon)
	else:
		mon = str(now.tm_mon)
	if now.tm_mday < 10:
		day = "0"+str(now.tm_mday)
	else:
		day = str(now.tm_mday)
	if now.tm_hour < 10:
		hour = "0"+str(now.tm_hour)
	else:
		hour = str(now.tm_hour)
	if now.tm_min < 10:
		Min = "0"+str(now.tm_min)
	else:
		Min = str(now.tm_min)
	if now.tm_sec < 10:
		sec = "0"+str(now.tm_sec)
	else:
		sec = str(now.tm_sec)
	str_time = str(now.tm_year)+mon+day+"-"+hour+Min+sec
	return str_time

def insert_EXIF(fname, now):
	time_stamp = now[:4] + ":" + now[4:6] + ":" + now[6:8] + " " + now[9:11] + ":" + now[11:13] + ":" + now[13:15]		
	zeroth_ifd = {piexif.ImageIFD.Make: u"Jungwan"}
	exif_ifd = {piexif.ExifIFD.DateTimeOriginal: time_stamp}
	gps_ifd = {piexif.GPSIFD.GPSDateStamp: time_stamp}
	first_ifd = {piexif.ImageIFD.Make: u"Jungwan"}
	
	exif_dict = {"0th":zeroth_ifd,"Exif":exif_ifd,"GPS":gps_ifd,"1st":first_ifd}
	exif_bytes = piexif.dump(exif_dict)	
	piexif.insert(exif_bytes, fname)

	


if __name__ == "__main__":
	if "export" not in os.listdir(os.getcwd()):		
		os.mkdir('./export')
	try:
		os.chdir('./export')
	except:
		pass	
	app = QApplication(sys.argv)
	dialog = MainDialog()
	sys.exit(app.exec_())