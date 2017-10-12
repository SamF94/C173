import threading
import socket
import sys
import os
import queue
import time

class Manager(threading.Thread):
	def __init__(self, maxClients):
		threading.Thread.__init__(self)
		#have maxClients as self.maxClients
		self.maxClients = maxClients
		#instantiate self running (sets) and self.q (queue)
		self.q = queue.Queue()
		self.running = set()
		
	def add(self, client):
		#add client to self.q
		self.q.put(client)
	
	def run(self):
		while True:
			kick = []
		#	remove any completed clients from self.running
			for t in self.running:
				if not t.isAlive(): kick.append(t)
			for t in kick:
				self.running.remove(t)
		
		#	start a new ClientHandler from self.q, IF APPLICABLE
			if self.q.empty() == True:
				time.sleep(1)
				continue	

			elif (len(self.running) >= self.maxClients):
				time.sleep(1)
				continue
		
			else:
			#	remove the next client thread from the queue
				nextClient = self.q.get()
				#thread = threading.Thread(target = self.running, ())
				nextClient.start()
				self.running.add(nextClient)

class ClientHandler(threading.Thread):
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.conn = conn
		
	def run(self):
		self.conn.send("READY".encode("UTF-8"))

		data = self.conn.recv(1024).decode("UTF-8")

		#cmdAndFile = data.decode("UTF-8")

		data = data.split(" ")

		filename = data[1]
		command = data[0]
		#self.conn.send("OK".encode("UTF-8"))

		if command == "GET":
			self.conn.send("OK".encode("UTF-8"))
			ready = self.conn.recv(1024).decode("UTF-8")
			size = os.path.getsize(filename)
			self.conn.send(data)
			OK = self.conn.recv(1024).decode("UTF-8")	
			
			f = open(filename, "rb")
			while size > 0:
				if size < 1024:
					data = f.read(size)
				else:
					data = f.read(1024)
				#s.send(data)
				size -= len(data)
			f.close()

			self.conn.send("DONE".encode("UTF-8"))
			#data = self.conn.recv(1024)
			self.conn.close()
			
		elif command == "PUT":
			self.conn.send("OK".encode("UTF-8"))
			data = self.conn.recv(1024).decode("UTF-8")
			size = int.from_bytes(data, byteorder = "big", signed = True)

			f = open(filename, "wb")
			while size > 0:
				if size < 1024:
					data = self.conn.recv(size)
				else:
					data = self.conn.recv(1024)
				f.write(data)
				size -= len(data)
			f.close()
			self.conn.send("DONE".encode("UTF-8"))
			#data = self.conn.recv(1024)
			self.conn.close()

		elif command == "DEL":
			if not os.access(filename, os.R_OK) or not os.path.isfile(filname):
				self.conn.send("No access to file " + filename).encode("UTF-8")
			else:
				self.conn.send("OK".encode("UTF-8"))
				size = os.path.getsize(filename)
				os.remove(filename)
				#ok = self.conn.recv(1024).decode("UTF-8")
				self.conn.send("DONE".encode("UTF-8"))
				self.conn.close()

if __name__ == "__main__":
	port = int(sys.argv[1])
	maxClients = int(sys.argv[2])
	
	verbose = "-v" in sys.argv

	runManager = Manager(maxClients)
	runManager.start()
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("", port))
	
	s.listen(3)
	
	#if verbose:
		#print("waiting on port", port)
	#instantiate and start a Manager object
	while True:
	#	accept() new client constructor
		conn, addr = s.accept()
	#	create ClientHandler object
		temp = ClientHandler(conn)
	#	add to Manager
		runManager.add(temp)
		#ClientManager.start()