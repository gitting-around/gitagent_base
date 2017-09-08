import threading

global num 
num = 0

def worker():
	i = 0
	global num
	while i < 10:
		i = i+1
		if num == 0:
			print 'do the stuff'
		else:
			print 'adapting'
			num = 0

def interrupting():
	i = 0
	count = 0
	global num
	while i < 10:
		i = i+1
		if count == 2:
			count = 0
			num = 1
		else:
			count = count + 1
		
if __name__ == '__main__':
	t1 = threading.Thread(target=worker)
	t2 = threading.Thread(target=interrupting)
	t1.start()
	t2.start()


	
