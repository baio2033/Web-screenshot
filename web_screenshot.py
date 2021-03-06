import sys, os
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from functools import partial
from PIL import Image
import io, piexif, sqlite3, md5

class MainDialog(QDialog):
	def __init__(self, parent=None):
		super(MainDialog, self).__init__(parent)
		self.initUI()

	def initUI(self):
		self.setWindowTitle("Web Capture")

		self.backBtn = QPushButton("Back")
		self.backBtn.clicked.connect(self.goBack)
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
		urlLayout.addWidget(self.backBtn,0,6)

		self.web = QWebView()
		self.web.load(QUrl("https://www.google.com"))

		self.web.urlChanged.connect(self.checkUrl)

		buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
		buttonBox.rejected.connect(self.reject)

		mainLayout = QVBoxLayout()
		mainLayout.addLayout(urlLayout)
		mainLayout.addWidget(self.web)
		mainLayout.addWidget(buttonBox)

		self.resize(1920,1080)

		self.setLayout(mainLayout)
		self.show()

	def goBack(self):
		self.web.page().triggerAction(QWebPage.Back)

	def checkUrl(self):
		#print str(self.web.url())		
		self.url = str(self.web.url())
		tmp = self.url.split("QUrl(u'")[1]
		tmp = tmp[:-2]
		self.urlValue.setText(tmp)

	def go_url(self):
		self.url = str(self.urlValue.text())
		if self.url.startswith("http") == False:
			self.url = "http://" + self.url
		self.web.load(QUrl(self.url))

	def capture(self, opt):		
		warnBox = QMessageBox(QMessageBox.Warning, "Warning", "Failed to save image", QMessageBox.NoButton, self)
		warnBox.addButton("&Close", QMessageBox.RejectRole)

		url = self.url
		if url.startswith("PyQt4.QtCore.QUrl"):
			url = url.split("QUrl(u'")[1]
			url = url[:-2]
		#print self.web.title()
		now = getTime()
		if opt == 1:
			try:
				frame = self.web.page().currentFrame()
				size = frame.contentsSize()

				ori_width = self.web.width()
				ori_height = self.web.height()

				size.setWidth(size.width()+20)
				size.setHeight(size.height()+10)
				self.web.resize(size)
				self.web.page().setViewportSize(size)

				image = QImage(size, QImage.Format_ARGB32)
				painter = QPainter(image)
				frame.render(painter, QWebFrame.ContentsLayer)				
				painter.end()				
				image.save("Full_ScreenShot_"+now+".jpg")												
				insert_EXIF("Full_ScreenShot_"+now+".jpg",now)	

				storeDB(url, now, "Full_ScreenShot_"+now+".jpg", "Full")	

				size.setWidth(ori_width)
				size.setHeight(ori_height)
				self.web.resize(size)
				self.web.page().setViewportSize(size)

				QMessageBox.information(self, "Success", "Capture Completed!")
			except Exception as e:	
				print e		
				warnBox.exec_()
		elif opt == 2:				    	
			try:				
				size = self.web.page().currentFrame().contentsSize()
				size.setWidth(self.web.width())
				size.setHeight(self.web.height())
				image = QImage(size, QImage.Format_ARGB32)				
				painter = QPainter(image)				
				self.web.page().currentFrame().render(painter)
				painter.end()
				image.save("Part_ScreenShot_"+now+".jpg")							
				insert_EXIF("Part_ScreenShot_"+now+".jpg",now)
				storeDB(url, now, "Part_ScreenShot_"+now+".jpg", "Part")
				QMessageBox.information(self, "Success", "Capture Completed!")
			except Exception as e:				
				warnBox.exec_()
		elif opt == 3:						
			try:
				data = self.web.page().currentFrame().toHtml()
				f = open("Src_"+now+".html" ,"w")
				f.write(data)
				f.close()
				storeDB(url, now, "Src_"+now+".html", "Script")
				QMessageBox.information(self, "Success", "Capture Completed!")
			except:
				warnBox.exec_()


def storeDB(url, now, fname, f_type):
	m = md5.new()
	f = open(fname, "rb")
	m.update(f.read())
	fileHash = m.hexdigest()
	f.close()

	conn = sqlite3.connect('capture.db')
	cur = conn.cursor()
	sql = "insert into Capture (type, fileName, url, time, md5) values (?, ?, ?, ?, ?)"
	cur.execute(sql, (f_type, fname, url, now, fileHash))
	conn.commit()

	conn.close()



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

	if "capture.db" not in os.listdir(os.getcwd()):
		f = open("capture.db", "w")
		f.close()
		conn = sqlite3.connect("capture.db")
		cur = conn.cursor()
		cur.execute("create table Capture (type LONGVARCHAR, fileName LONGVARCHAR, url LONGVARCHAR, time LONGVARCHAR, md5 LONGVARCHAR)")
		conn.commit()
		conn.close()

	app = QApplication(sys.argv)
	dialog = MainDialog()
	sys.exit(app.exec_())