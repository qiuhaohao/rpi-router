import queue
import threading

from connections.tcp import TCPServer
from connections.BTServer import BTServer
from connections.SerialArduino import SerialArduino
from connections.RpiConnection import RpiConnection

from threads.ReceiveThread import ReceiveThread
from threads.SendThread import SendThread

queue_lock = threading.Lock()
data_queue = queue.Queue()

connections = [
	SerialArduino(),
	RpiConnection(),
	BTServer(),
	TCPServer()
]

for c in connections:
	c.init_connection()

print("All Connections Up! Waiting for message...")

# # using Stubs for now
# from Stubs import ReceiverStub, SenderStub

# # initialising the connections 
# receivers = [ReceiverStub(id=i) for i in range(3)]
# senders = [SenderStub(id=i) for i in range(3)]



receive_threads = [
	ReceiveThread(threadID=i, 
					name="Receive_Thread_{}".format(i), 
					receiver=connections[i], 
					lock=queue_lock, 
					queue=data_queue
				) 
	for i in range(len(connections))
]

for t in receive_threads:
	t.start()

send_thread = SendThread(threadID=len(connections), 
							name="Send_Thread", 
							scheme=connections, 
							lock=queue_lock, 
							queue=data_queue
						)

send_thread.start()