#!/usr/bin/python3
import socket
import sys
import threading
import time
import signal
from cryptography.fernet import Fernet
i=0
class userThread(threading.Thread):
	def __init__(self,host,portNumber,maxUsersCount):
		self.host=host
		self.maxUsersCount=maxUsersCount
		self.total_user=0
		self.connecting_users=[]#keep track of connecting users
		self.portNumber=portNumber
		self.threads=[]#list of socket thread
		self.users=[]#list of usernames of the connected clients
		self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.bind((host,portNumber))
		self.shared_key=b'gWEdcvtXUknmH8li0G_Aj0DrtJPyrg9SP38_zG-0o10='
		self.f=Fernet(self.shared_key)
	def run(self):
		self.sock.listen(5)
		try:
			while True:
				usrsock,addr=self.sock.accept()
				#if maximum number of connection reached, send back the #busy status
				#to the client and close its connection
				if self.total_user==self.maxUsersCount:
					token=self.f.encrypt(b"#busy")
					usrsock.send(token)
					usrsock.close()
				else:
					token=self.f.encrypt(b"#notbusy")
					usrsock.send(token)
					self.threads.append(usrsock)
					self.total_user+=1
					print("Current user count=",self.total_user)
					threading.Thread(target=self.thread_handler,args=(usrsock,)).start()
			self.sock.close()
		except socket.error as err:
			print(err)
			sys.exit()

	def thread_handler(self,usrsock):
		while True:
			try:
				resp=self.f.decrypt(usrsock.recv(1024)).decode()#receiving data
				if resp.startswith('#join'):
					usr=resp.replace('#join','').lstrip()
					if usr in self.users:
						global i
						usr=usr+str(i)
						token=self.f.encrypt(("#usernametaken %s"%usr).encode())
						usrsock.send(token)
						i+=1
					self.broadcast("#newuser %s"%usr,usrsock)
					self.users.append(usr)
					token=self.f.encrypt(("#welcome %s"%usr).encode())
					usrsock.send(token)
		        	#in order to prevent this thread to send 2 packets at the same time
		        	#let it sleep for 1 sec so data can arrive in sequence, not at the same time
					time.sleep(1)
					print("Current connecting users:")
					for usr in self.users:
						print(usr)
					if len(self.users)>1:
						for i in range(0,len(self.users)):
							if self.users[i]!=usr:
								token=self.f.encrypt(("#prevjoined %s"%self.users[i]).encode())
								usrsock.send(token)
							#announce to all the clients that a new user has joined
				if resp.startswith('#status'):
					token=self.f.encrypt("#statusPosted".encode())
					usrsock.send(token)
					status=resp.replace('#status','').lstrip()
					#broadcast status to all other users
					self.broadcast("#newStatus %s:%s"%(usr,status),usrsock)#changed from Ibroadcast, work but doesn't look good, lets try gui!
				if resp.startswith('#Bye'):
					self.broadcast("#Leave %s"%usr,usrsock)
					#broadcast message to all other users saying that a user is leaving
					token=self.f.encrypt("#Bye".encode())
					usrsock.send(token)
					self.threads.remove(usrsock)#remove that user thread
					self.total_user-=1 #subtract 1 from total user
					self.users.remove(usr)#remove username from list
					print("Current user count=",self.total_user)
					self.usr=""#set username to empty
					usrsock.close()
					break
			except IOError as err:
				print(err)
				sys.exit()
#broadcast messages to all clients except the connecting one
	def broadcast(self,message,sock):
		for thread in self.threads:
			if thread!=sock:
				token=self.f.encrypt(message.encode())
				thread.send(token)

	def Ibroadcast(self,message):
		for thread in self.threads:
			token=self.f.encrypt(message.encode())
			thread.send(token)
	
# def sig_handler(sig, frame):
# 	print("Interrupt received, closing program and terminating all connections...")
# 	sys.exit(1)
def main():
	maxUsersCount=5
	portNumber=58888
	if len(sys.argv)<3:
		print("Usage: python Server.py <portNumber> <max user count>")
		print("Now using port number=",portNumber)
		print("Maximum user count=",maxUsersCount)
	else:
		portNumber=int(sys.argv[1])
		maxUsersCount=int(sys.argv[2])
	print("Server now using port number=%d\nMaximum user count=%d"%(portNumber,maxUsersCount))
	try:
		threads=userThread('',portNumber,maxUsersCount).run()#start the work	
	except IOError as err:
		print(err)
		sys.exit()
if __name__=='__main__':
	main()


