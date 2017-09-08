#!/usr/bin/env python
#no license, for the love of god

import sys
import rospy
from GITagent.msg import *
import simulation_functions

class Interrupter:
	
	def __init__(self):
		self.pub = rospy.Publisher('trigger', StateTrigger, queue_size=10)
		rospy.init_node('interrupter', anonymous=True)
    		self.rate = rospy.Rate(0.5) # 10hz
		
	def run(self):
		while not rospy.is_shutdown():
			test = StateTrigger()
			test.trigger = 1
			self.pub.publish(test)
			print test.trigger
			self.rate.sleep()
	
if __name__ == '__main__':
	try:
		interrupter = Interrupter()
		interrupter.run()
	except rospy.ROSInterruptException:
		pass
