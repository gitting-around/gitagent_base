#!/usr/bin/env python
import threading
import time
c = threading.Condition()
flag = 0      #shared between Thread_A and Thread_B
val = 20

class Thread_A(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        global flag
        global val     #made global here
        while True:
                print str(self.name)+": val=" + str(val)
                time.sleep(0.1)
                flag = 1
                val = 30


class Thread_B(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        global flag
        global val    #made global here
        while True:
		print "B: val=" + str(val)
		time.sleep(0.5)
		flag = 0
		val = 20


a = Thread_A("myThread_name_A")
b = Thread_B("myThread_name_B")
c = Thread_A("myThread_name_D_A")


b.start()
a.start()
c.start()
a.join()
b.join()
