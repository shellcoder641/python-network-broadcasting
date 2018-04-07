import sys
import socket
import threading
class UserThread(threading.Thread):
	def __init__(self,host,port):
		self.host=host
		self.port=port
		self.username=''
		try:
			self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.sock.connect((host,port))
		except IOError as ioerr:
			print ioerr
			sys.exit()
		except socket.error as sockerr:
			print sockerr
			sys.exit()
	def run(self):
		status=self.sock.recv(1024)#Receive the server status before making any connection
		if status=="#busy":
			print "The server is busy, please try again later."
			sys.exit()
		try:
    	                #start the two threads
		        threading.Thread(target=self.receive_server_data,args=(self.sock,)).start()
		        threading.Thread(target=self.send_usr_input,args=(self.sock,)).start()
		except IOError as ioerr:
			print ioerr
			sys.exit()
	def send_usr_input(self,sock):
		usr=raw_input("Enter your name:\n")
		self.sock.send("#join %s"%usr)
		try:
			while True:
				data=sys.stdin.readline()#read from stdin
				#status must not be the Exit command or a 1 character
				if not data.startswith('Exit') and len(data)>1:
					    self.sock.send("#status %s"%data)
				elif data.startswith('Exit'):
					self.sock.send("#Bye")
					break
		except IOError as ioerr:
			print ioerr
			sys.exit()
		except socket.error as sockerr:
			print sockerr
			sys.exit()
#thread for receiving and handling data from server
	def receive_server_data(self,sock):
		while True:
		        data=sock.recv(1024)
			if data.startswith('#newuser'):
			        self.username=data.replace('#newuser','').lstrip()
				print "New user %s has joined!!!"%self.username
    	                #print all current connecting users, minus the one that got just connected
    		        if data.startswith('#prevjoined'):
    		    	        l=data.replace('#prevjoined','').lstrip().split()
    			        for usr in l:
    				    if usr!=self.username:
    				        print "New user %s has joined!!!"%usr
    		        if data.startswith('#usernametaken'):
    		                print "Username has already taken."
                                self.username=data.replace('#usernametaken','').lstrip()
                                print "Your username will be ",self.username
                        if data.startswith('#welcome'):
    			        usr=data.replace('#welcome','').lstrip()
    			        print "Welcome user %s to our Social Media App."%usr
    			        print "To leave enter Exit on a new line."
 		            #display any broadcasted status 
    		        if data.startswith('#newStatus'):
    			        usr_and_stt=data.replace('#newStatus','').lstrip()
    			        usrinfo=usr_and_stt.split(':')
    			        usrname=str(usrinfo[0])
    			        usrstt=str(usrinfo[1])
    			        print "<%s>: %s"%(usrname,usrstt)
    		        if data.startswith('#Leave'):
    			        usr=data.replace('#Leave','').lstrip()
    			        print "\nThe user %s is leaving!!!"%usr
    		        if data.startswith('#Bye'):
    			        print "The server has closed the connection."
    			        sock.close()
                                break
def main():
	portNumber=58888	#Default port
	host="localhost"	#Default host
	if len(sys.argv)<3:
		print "Usage: python User.py <host> <portNumber>"
		print "Now using host=%s, portNumber=%d"%(host,portNumber)
	else:
		host=str(sys.argv[1])
		portNumber=int(sys.argv[2])
	thread=UserThread(host,portNumber).run()#do the real work
if __name__=='__main__':
	main()
