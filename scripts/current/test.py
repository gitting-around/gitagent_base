#!/usr/bin/env python
import sys
import time

class testing:
	def __init__(self):
		self.f = open('testing', 'w')

if __name__ == '__main__':
	## Redirect stderr to file located in home/.ros/ ######################
	ab = testing()

	f2 = open('other_testing', 'w')

	try:
		while True:
			time.sleep(1)
			print 'stuff'
			ab.f.write('stuff\n')
			f2.write('stuff\n')
	except KeyboardInterrupt:
		ab.f.close()
		f2.close()
	except (RuntimeError, TypeError, NameError):
		pass
	#except:
		#print("Unexpected error:", sys.exc_info()[0])
		#raise
	
