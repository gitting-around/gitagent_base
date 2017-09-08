#!/usr/bin/env python
#no license, for the love of god

import sys
import rospy
import time
from GITagent.msg import *

class PUnit:

	myMessage = Message_Type()
	me = -1
	known_people = []

	def __init__(self, agent_id):

		rospy.init_node('msg_punit', anonymous=True)
		self.me = agent_id
		print self.me

		self.publish_env = rospy.Publisher('/environment/env_topic', Message_Type, queue_size=200)
		self.publish_brain = rospy.Publisher('trigger', Message_Type, queue_size=200)
		rospy.Subscriber('msgs', Message_Type, self.callback_color)
		rospy.Subscriber('/environment/env_topic', Message_Type, self.callback_env)

	def callback_color(self, data):
		rospy.loginfo(rospy.get_caller_id() + " Callback-from-brain %d, %s", data.id, data.content)
		self.myMessage = data
		if not rospy.is_shutdown():
			self.publish_env.publish(self.myMessage)
			print self.myMessage
		
	def callback_env(self, data):
		rospy.loginfo(rospy.get_caller_id() + " Callback-from-env %d, %s", data.id, data.content)
		if not self.me == data.id:
			print 'sent message to brain'

			guy_id_srv = [data.id]
			guy_id_srv.append([int(x) for x in filter(None, data.content.split('|'))])
			
			new = True
			for x in self.known_people:
				if x[0] == data.id:
					new = False

			if new:
				self.known_people.append(guy_id_srv)

			print self.known_people

			if not rospy.is_shutdown() and new:
				self.myMessage = data
				self.publish_brain.publish(self.myMessage)
				print 'published new individual'

if __name__ == '__main__':
	agent_id = rospy.get_param('msg_punit/myID')
	punit = PUnit(agent_id)

	TIME = time.time()
	DURATION = 3600 # 2min
	#rospy.spin()
	while True:
		if time.time() > TIME + DURATION:
			break
