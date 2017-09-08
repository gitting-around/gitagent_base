#!/usr/bin/env python
#no license, for the love of god

import sys
import rospy
from GITagent.msg import Position, Color
from aboutme_wm import AboutMe_WM

class Environment:
	
	def __init__(self):
		rospy.init_node('env', anonymous=True)
		rospy.Subscriber('/environment/env_topic', Color, self.callback_color)
		self.publish_global = rospy.Publisher('/environment/env_topic', Color, queue_size=200)
		rospy.spin()

	def callback_color(self, data):
		rospy.loginfo(rospy.get_caller_id() + " I heard %f, %f, %f", data.red, data.green, data.blue)
		print 'I\'m publishing message from %d' % data.id
		rate = rospy.Rate(5) #1Hz
		self.publish_global.publish(data)
		rate.sleep()

if __name__ == '__main__':
	env = Environment()
	
