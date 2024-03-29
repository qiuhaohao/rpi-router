import queue
import threading
import time
import random

from connections.libs.arrow_finder import ArrowFinder

def to_byte(i, length=1, byteorder="little"):
	return int(i).to_bytes(length,byteorder)

DEST_HEADER_TO_PC = to_byte(4)
SENDER_ADDR_FROM_RPI = to_byte(8)

CODE_CAPTURING_FINISHED = to_byte(21)
CODE_ARROW_DETECTED = to_byte(22)

# class ArrowFinderStub:
# 	def __init__(self, capture_delay=0.3, arrow_probability=0.5):
# 		self.capture_delay = capture_delay
# 		self.arrow_probability = arrow_probability
# 	def _detected(self):
# 		return random.random() < self.arrow_probability
# 	def _getResult(self):
# 		return {"arrows": [123] if self._detected() else []}
# 	def getArrows(self, after_capture=lambda: None):
# 		time.sleep(self.capture_delay)
# 		after_capture()
# 		result = self._getResult()
# 		return result

class DetectionThread(threading.Thread):
	def __init__(self, get_msg, on_finish_capturing, on_detected, debug=False):
		threading.Thread.__init__(self)
		self.debug=debug
		# self.arrowFinder = ArrowFinderStub() if debug else ArrowFinder()
		self.arrowFinder = ArrowFinder()
		self.get_msg = get_msg
		self.on_finish_capturing = on_finish_capturing
		self.on_detected = on_detected

	def run(self):
		while True:
			msg = self.get_msg()
			arrowsPos = self.detect()
			if len(arrowsPos):
				pos_payload = b''.join(list(map(to_byte, arrowsPos)))
				msg_payload = msg[2:] + pos_payload
				self.on_detected(msg_payload)

	def detect(self):
		arrows = self.arrowFinder.getArrows(
			after_capture = self.on_finish_capturing,
			with_image=True
		)['arrows']
		arrowPos = list(
			map(lambda a: a['pos'],
				arrows
				)
		)
		return arrowPos

class RpiConnection:
	def __init__(self, debug=False):
		self.ready = False
		self.debug=debug
		self.in_queue = queue.Queue()
		self.out_queue = queue.Queue()
		self.detech_thread = DetectionThread(
			get_msg=self.get_from_in_queue,
			on_finish_capturing=self.put_capturing_finished,
			on_detected=self.put_arrow_detected,
			debug=self.debug
		)
		self.detech_thread.start()

	def send(self, msg):
		self.in_queue.put(msg)

	def recv(self):
		# block when there is nothing to be received
		return self.out_queue.get()
	
	def get_from_in_queue(self):
		return self.in_queue.get()

	def put_capturing_finished(self):
		self.out_queue.put(
			DEST_HEADER_TO_PC
			+ SENDER_ADDR_FROM_RPI
			+ CODE_CAPTURING_FINISHED
		)

	def put_arrow_detected(self, msg_payload):
		self.out_queue.put(
			DEST_HEADER_TO_PC
			+ SENDER_ADDR_FROM_RPI
			+ CODE_ARROW_DETECTED
			+ msg_payload
		)

	def init_connection(self):
		# initialise detect_loop
		pass