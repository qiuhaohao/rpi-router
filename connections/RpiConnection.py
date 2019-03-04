from libs.arrow_finder import ArrowFinder

def to_byte(i, length=1, byteorder="little"):
	return i.to_bytes(length,byteorder)

DEST_HEADER_TO_PC = to_byte(8)

class RpiConnection:
	def __init__(self):
		self.arrowFinder = ArrowFinder()
		self.ready = False

	def send(self, bytes):
		self.ready = True

	def recv(self):
		while not self.ready:
			pass
		result = to_byte(bool(self.arrowFinder.getArrows()))
		return DEST_HEADER_TO_PC + result

	def init_connection(self):
		pass
