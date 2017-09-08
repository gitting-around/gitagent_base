#!/usr/bin/env python

import sys
import rospy
from GITagent.srv import *

def add_two_ints_client(x):
    rospy.wait_for_service('service')
    try:
        request = rospy.ServiceProxy('service', Service)
        resp1 = request(x)
        return resp1.outgoing
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

def usage():
    return "%s [x]"%sys.argv[0]

if __name__ == "__main__":
    if len(sys.argv) == 2:
        x = sys.argv[1]
    else:
        print usage()
        sys.exit(1)
    print "Requesting %s"%x
    print "%s, %s"%(x,add_two_ints_client(x))
