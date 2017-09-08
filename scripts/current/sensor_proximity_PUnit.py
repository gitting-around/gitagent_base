#!/usr/bin/env python
#no license, for the love of god

import sys
import rospy
from GITagent.msg import Position

def callback(data):
	rospy.loginfo(rospy.get_caller_id() + " I heard %f, %f", data.x_pos, data.y_pos)

def end_node():
	rospy.init_node('sensor_prox_punit', anonymous=True)
	
	rospy.Subscriber('mypos_xytheta', Position, callback)

	rospy.spin()

if __name__ == '__main__':
	end_node()
