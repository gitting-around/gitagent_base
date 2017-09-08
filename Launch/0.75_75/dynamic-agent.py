#!/usr/bin/env python
#no license, for the love of god

import sys

nr_agents = 0

def how_many_agents():
	global delta, depends, popSize, provaNr
	delta = input("Enter delta: ")
	depends = input("Enter depends ")
	popSize = input("Enter pop size ")
	provaNr = input("Enter provaNr ")

def write_launch_file():

	try: 
		launch = open('agent.launch', 'w')
		launch.write('<launch>\n')

		launch.write('	<arg name="id"/>\n')
		launch.write('	<node pkg="GITagent" type="agent.py" name="brain_node" output="log" launch-prefix="xterm -e">\n')
		launch.write('		<param name="myID" value="$(arg id)" />\n')
		launch.write('		<param name="myDelta" value="'+str(delta)+'" />\n')
		launch.write('		<param name="myDepend" value="'+str(depends)+'" />\n')
		launch.write('		<param name="popSize" value="'+str(popSize)+'" />\n')
		launch.write('		<param name="provaNr" value="'+str(provaNr)+'" />\n')
		launch.write('	</node>')

		launch.write('	<node pkg="GITagent" type="msg_PUnit.py" name="msg_punit" output="log" launch-prefix="xterm -e">\n')
		launch.write('		<param name="myID" value="$(arg id)" />\n')
		launch.write('	</node>\n')

		
		launch.write('</launch>\n')
		launch.close()
	except IOError:
		print "Error: can\'t find file or read data"
	

if __name__ == '__main__':
	how_many_agents()
	write_launch_file()
