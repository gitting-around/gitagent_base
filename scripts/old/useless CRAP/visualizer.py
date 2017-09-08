#!/usr/bin/env python
#no license, for the love of god

import sys
import rospy
from GITagent.msg import Position
from rqt_my_ui import MyPlugin
from PyQt4.QtGui import *
from PyQt4.QtCore import *

xypos_signal = pyqtSignal()

def callback(data):
	rospy.loginfo(rospy.get_caller_id() + "I heard %d, %d", data.x_pos, data.y_pos)
	
	xypos_signal.connect(MyPlugin.handle_xysignal)
	xypos_signal.emit()	

def visualizer():
	rospy.init_node('visualizer', anonymous=True)
	
	rospy.Subscriber('mypos_xytheta', Position, callback)

	rospy.spin()

if __name__ == '__main__':
	visualizer()

	
	

