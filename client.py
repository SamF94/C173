import sys, socket, time, random

port = int(sys.argv[1])
name = sys.argv[2]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", port))
ready = sock.recv(1024)
print (name + ": READY.")
sock.send("GET test.txt".encode("UTF-8"))
ok = sock.recv(1024)
sock.send("READY".encode("UTF-8"))
totalBytes = int.from_bytes(sock.recv(1024), byteorder='big', signed=False)
sock.send("OK".encode("UTF-8"))

f = open("test.txt", "wb")

bytesLeft = totalBytes
print (name + ": receiving")
time.sleep(random.randint(2,6))

while(bytesLeft > 0):
	data = sock.recv(min(1024, bytesLeft))
	bytesLeft -= len(data)
	f.write(data)
f.close()

done = sock.recv(1024)
print (name + ": DONE")
sock.close()
	
