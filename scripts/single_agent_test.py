#!/usr/bin/env python
#no license, for the love of god

import sys
import rospy
import time
from GITagent.msg import *
from GITagent.srv import *
from aboutme_wm import AboutMe_WM
import simulation_functions

global test_var
test_var = 0

class Agent:
	
	def __init__(self, delta, energy, ID, x, y, theta, red, green, blue, state):
		self.about_me_wm = AboutMe_WM(delta, energy, ID, x, y, theta, red, green, blue, state)
		self.Alive = 20
		
		#From the list of services select 30% (this number can be modified) for the agent to be providing - at random
		#[id time energy reward]
		#active_servs format: [[5, 100, 3705, 42], [6, 97, 5736, 19], [9, 96, 9156, 4]]

		active_servs = simulation_functions.select_services()
		rospy.init_node('agent', anonymous=True)
		rospy.Subscriber('trigger', StateTrigger, self.callback)
	
	def callback(self, data):
		rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data.trigger)
		self.about_me_wm.state = self.about_me_wm.state + 1
		if self.about_me_wm.state > 3:
			self.about_me_wm.state = 1
		#print self.about_me_wm.state

	def run_fsm(self):
		global test_var
		while self.Alive > 0:
			
			while self.about_me_wm.state == 1:
				self.wander()
			while self.about_me_wm.state == 2:
				self.execute()
			while self.about_me_wm.state == 3:
				self.adapt()
			
	def wander(self):
		print 'not all who wander are lost'

	def execute(self):
		global test_var
		print test_var
		test_var = test_var + 1

	def adapt(self):
		print 'lulet e majit - qe u befshim lemsh u befshim'

	def stop(self):
		print 'what the hell am I doing in here'

if __name__ == '__main__':
	agent = Agent(0.6, 1000, 1, 2,3, 3.14, 0.5, 0.5, 0.5, 1)
	agent.run_fsm()
