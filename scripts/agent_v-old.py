#!/usr/bin/env python
#no license, for the love of god
#The agent takes the list of services one by one --> we can consider that this will come from some form of planning --> where should planning go, in adapt or execute??

import sys
import rospy
import time
from GITagent.msg import *
from GITagent.srv import *
from aboutme_wm import AboutMe_WM
import simulation_functions
import random

class Agent:

	def __init__(self, delta, energy, ID, x, y, theta, red, green, blue, state):
		self.about_me_wm = AboutMe_WM(delta, energy, ID, x, y, theta, red, green, blue, state)
		self.Alive = 20
	
		self.old_state = 1

		#From the list of services select 30% (this number can be modified) for the agent to be providing - at random
		#[id time energy reward ...] ... -> dependencies on other services for instance 4 5 2 1
		#active_servs format: [[5, 100, 3705, 42], [6, 97, 5736, 19], [9, 96, 9156, 4]]

		self.active_servs = simulation_functions.select_services()

		self.changed_servs = 1
		self.iteration = 1
		self.task_idx = 0
		self.service = self.active_servs[self.task_idx] 

		self.message = Message_Type()
		self.message.id = self.about_me_wm.ID
		self.message.rank = 10
		self.message.group = 1

		self.message.content = []
		self.message.content.append([x[0] for x in self.active_servs])

		self.message.timestamp = time.strftime('%X', time.gmtime())

		print self.message

		rospy.init_node('agent', anonymous=True)
		self.publish_global = rospy.Publisher('msgs', Message_Type, queue_size=200)
		rospy.Subscriber('trigger', StateTrigger, self.callback)
	
	def callback(self, data):
		rospy.loginfo(rospy.get_caller_id() + 'I am: %d, I heard %s', self.about_me_wm.ID, data.trigger)
		self.old_state = self.about_me_wm.state
		self.about_me_wm.state = 3
		
	def run_fsm(self):
		while self.Alive > 0:
			
			if self.about_me_wm.state == 1:
				self.wander()
			elif self.about_me_wm.state == 2:
				self.execute()
			elif self.about_me_wm.state == 3:
				self.adapt()

	def run_service_step(self, service, i):
		if i < service[1]:
			print 'Doing task %d, iteration: %d' % (service[0], i)
		else:
			self.about_me_wm.state = 1
			self.iteration = 1
			print 'Task %d, done, wandering again' % service[0]
			if (self.task_idx + 1) == len(self.active_srvs):
				self.task_idx = 0
			else:
				self.task_idx = self.task_idx + 1

			self.service = self.active_servs[self.task_idx]			
			
	def wander(self):
		print self.message
		time.sleep(1)

	def execute(self):
		self.run_service_step(self.service, self.iteration)	

	def adapt(self):
		print 'adapting'
		if random.random() > 0.9:
			print 'adapted'
			self.iteration = 1
			self.about_me_wm.state = 2
		else:
			print 'keep at what you\'re doing'
			if self.old_state == 2:
				self.about_me_wm.state = 2
				self.iteration = self.iteration + 1
			else:
				self.about_me_wm.state = 1
		#time.sleep(1)

	def stop(self):
		print 'what the hell am I doing in here'

if __name__ == '__main__':
	try:
		agent_id = rospy.get_param('brain_node/myID')
		print 'my id: %d' % agent_id
		agent = Agent(0.6, 1000, agent_id, 2,3, 3.14, 0.5, 0.5, 0.5, 1)
		agent.run_fsm()
	except rospy.ROSInterruptException:
		pass
