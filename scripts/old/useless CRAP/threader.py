from threading import Thread
import time

class threader(Thread):

	def __init__(self, ID, state):
		Thread.__init__(self)
		self.ID = ID
		self.state = state

	def run(self):
		if self.ID == 1 & self.state == 1:
			exec_a(self)
		elif self.ID == 2:
			exec_b(self)
	
	def pause(self):
		while self.state == 0:
			print 'before sleep'
			time.sleep(5)
			self.state = 1
			print 'after sleep'
			print 'my id: %d' % self.ID

t1 = threader(1, 1)
t2 = threader(2, 1)

def exec_a(self):
	i = 0
	while i < 10:
		print 'do stuff, %d' % i
		i = i + 1

def exec_b(self):
	global t1
	t1.state = 0
	print 'before pause'
	t1.pause()
	print 'end of exec_b'

if __name__ == '__main__':
	t1.start()
	t2.start()
