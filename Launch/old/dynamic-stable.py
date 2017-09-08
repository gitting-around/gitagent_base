#!/usr/bin/env python
#no license, for the love of god

import sys

nr_agents = 0

def how_many_agents():
	global nr_agents
	nr_agents = input("Enter population size: ")

def write_launch_file():

	try: 
		launch = open('launch_agents.launch', 'w')
		launch.write('<launch>\n')

		for ii in range(1, nr_agents+1):
			launch.write('	<!-- BEGIN ROBOT')
			launch.write(str(ii))
			launch.write('-->\n')
		
			launch.write('	<group ns="robot')
			launch.write(str(ii))
			launch.write('">\n')

			launch.write('		<include file="$(find GITagent)/Launch/agent.launch"> <arg name="id" value="')
			launch.write(str(ii))
			launch.write('"/> </include>\n')
			launch.write('	</group>\n')
		
		launch.write('	<!-- BEGIN ENV')
		launch.write(str(ii))
		launch.write('-->\n')
	
		launch.write('	<group ns="environment">\n')

		launch.write('		<include file="$(find GITagent)/Launch/env.launch"> </include>\n')
		launch.write('	</group>\n')
		
		launch.write('</launch>\n')
		launch.close()
	except IOError:
		print "Error: can\'t find file or read data"
	

if __name__ == '__main__':
	how_many_agents()
	write_launch_file()
