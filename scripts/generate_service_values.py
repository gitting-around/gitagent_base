#!/usr/bin/env python
#holy crap!
#For now, service i depends on service i + 1. For n services, when i == n, then i doesn't depend on any other service.
#probably needs re-write for better design

import sys
import random

time_range = 10
energy_range = 10000
reward_range = 50

def generate_service():
	time = random.randint(1, time_range)
	energy = random.randint(1, energy_range)
	reward = random.randint(1, reward_range)
	return {'time':time, 'energy':energy, 'reward':reward}
	 
if __name__ == '__main__':
	nr_services = -1
	try:
        	nr_services = int(sys.argv[1])
    	except IndexError:
        	print "Usage: generate_service_values.py <arg1>"
        	sys.exit(1)
	try: 
		service_file = open('services_list', 'w')

		for ii in range(1, nr_services + 1):
			service = generate_service()

			if not ii == nr_services:
				service_file.write(str(ii) + '	' + str(service['time']) + '	' + str(service['energy']) + '	' + str(service['reward']) + '	' + str(ii+1) +'\n')
			else:
				service_file.write(str(ii) + '	' + str(service['time']) + '	' + str(service['energy']) + '	' + str(service['reward']) + '\n')
			
		service_file.close()
	except IOError:
		print "Error: can\'t find file or read data"
