#!/usr/bin/python3
import sys
import socket
import threading
from cryptography.fernet import Fernet
from PyQt5 import uic
from PyQt5.QtWidgets import *
usr=''
class UserThread(threading.Thread):
	def __init__(self,host,port,ui):
		self.host=host
		self.port=port
		self.username=''
		self.ui=ui
		self.shared_key=b'gWEdcvtXUknmH8li0G_Aj0DrtJPyrg9SP38_zG-0o10='
		self.f=Fernet(self.shared_key)
		try:
			self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.sock.connect((host,port))
		except IOError as ioerr:
			print(ioerr)
			sys.exit()
		except socket.error as sockerr:
			print(sockerr)
			sys.exit()
	def run(self):
		status=self.f.decrypt(self.sock.recv(1024)).decode()#Receive the server status before making any connection
		if status=="#busy":
			print("The server is busy, please try again later.")
			sys.exit()
		try:
    		#start the thread
			global usr
			usr=input("Enter your name:\n")
			token=self.f.encrypt(("#join %s"%usr).encode())
			self.sock.send(token)
			threading.Thread(target=self.receive_server_data,args=(self.sock,)).start()
		except IOError as ioerr:
			print(ioerr)
			sys.exit()

	def sendtext(self):
		global usr
		data=self.ui.lineEdit.text()
		if data!="" and data!="Exit":
			self.ui.plainTextEdit.appendHtml("<html><b>"+usr+"</b></html>:"+data)
			token=self.f.encrypt(("#status %s"%data).encode())
			self.sock.send(token)
			self.ui.lineEdit.setText("")
		if data=="Exit":
			token=self.f.encrypt("#Bye".encode())
			self.sock.send(token)
			sys.exit(2)
#thread for receiving and handling data from server
	def receive_server_data(self,sock):
		while True:
			data=self.f.decrypt(sock.recv(1024)).decode()#what if the message is longer than 1024 bytes?
			if data.startswith('#newuser'):
				self.username=data.replace('#newuser','').lstrip()
				self.ui.plainTextEdit.appendPlainText("New user "+self.username+" has joined.")
    	    	#print all current connecting users, minus the one that got just connected
			if data.startswith('#prevjoined'):
				l=data.replace('#prevjoined','').lstrip().split()
				for usr in l:
					if usr!=self.username:
						self.ui.plainTextEdit.appendPlainText("Previously joined user: "+usr)
			if data.startswith('#usernametaken'):
				self.ui.plainTextEdit.appendPlainText("Username has already taken.")
				self.username=data.replace('#usernametaken','').lstrip()
				self.ui.plainTextEdit.appendPlainText("Your username will be "+self.username)
			if data.startswith('#welcome'):
				usr=data.replace('#welcome','').lstrip()
				self.ui.plainTextEdit.appendPlainText("Welcome user "+usr+" to my Social Media App.")
				self.ui.plainTextEdit.appendPlainText("To leave enter Exit on a new line.")
				#display any broadcasted status 
			if data.startswith('#newStatus'):
				usr_and_stt=data.replace('#newStatus','').lstrip()
				usrinfo=usr_and_stt.split(':')
				usrname=str(usrinfo[0])
				usrstt=str(usrinfo[1]).rstrip()
				self.ui.plainTextEdit.appendPlainText(usrname+":"+usrstt)
			if data.startswith('#Leave'):
				usr=data.replace('#Leave','').lstrip()
				self.ui.plainTextEdit.appendPlainText("User "+usr+" has left the chat.")
			if data.startswith('#Bye'):
				self.ui.plainTextEdit.appendPlainText("The user has closed the connection.")
				sock.close()
				break

class Mychatroom(QWidget):
	def __init__(self):
		super().__init__()
		self.ui=uic.loadUi("chatroom.ui")
		self.ui.show()
		portNumber=58888	#Default port
		host="localhost"	#Default host
		if len(sys.argv)<3:
			print("Usage: python User.py <host> <portNumber>")
			print("Now using host=%s, portNumber=%d"%(host,portNumber))
		else:
			host=str(sys.argv[1])
			portNumber=int(sys.argv[2])
		self.thread=UserThread(host,portNumber,self.ui)#do the real work
		self.thread.run()
		self.ui.pushButton.clicked.connect(self.thread.sendtext)#call the handler function when clicked
		self.ui.plainTextEdit.setReadOnly(True)#disable text editing to make it a display widget.

def main():
	app=QApplication(sys.argv)
	win=Mychatroom()
	sys.exit(app.exec_())

if __name__=='__main__':
	main()
