#!/usr/bin/env python
#no license, for the love of god
#The agent takes the list of services one by one --> we can consider that this will come from some form of planning --> where should planning go, in adapt or execute??

#so you think you can tell, heaven from hell, blue skies from pain, can you tell a green field?
#hakuna matata, what a wonderful phrase, hakuna matata, ain't no passing craze:DD
#nata dridhet mbi rrugica, dhe ti mbi doren time

#HEY DUMMY!!! YES YOU! -- BE CAREFUL OF HOW YOU REFERENCE CLASS ATTRIBUTES SELF.ATTR -- you useless nerd!!!
#ALSO, be careful of the NAMESPACES
#CAREFUL WHEN YOU RETURN VARIABLES, CHECK THE TYPES, INT OR STRING OR FLOAT
#CAREFUL, arguments in the call_serve() method should be passed in the order they are declared in the service.srv file!!
#CAREFUL randint(0,n) is inclusive for 0 and n

import sys
import time
import datetime
from GITagent.msg import *
from GITagent.srv import *
import rospy
from aboutme_wm import AboutMe_WM
import simulation_functions
import random
from threading import Lock
import fcntl

class Agent:

	def __init__(self, delta, energy, ID, x, y, theta, red, green, blue, state, depend_nr, popSize, provaNr):

		self.TIME = time.time()
		self.DURATION = 3600 # 20min
		## The attributes below serve as a timestamp for each function called ######
		self.handle = 0
		self.call = 0
		self.callback_bc = 0
		self.w = 0
		self.a = 0
		self.run_step = 0
		self.fsm = 0
		self.helping = False
		############################################################################
		# use this variable to count the instances in which an agent asks for help the same agent who asked it for help in the first place
		self.count_posReq = 0
		self.COUNT_noones = 0
		self.count_loops = 0

		self.steps_b4_equilibrium = 100

		self.lock = Lock()

		self.stdout_log = 'RESULT/pop_size.'+str(popSize) +'/prova.'+str(provaNr)+'/stdout_' + str(ID) + '_' + str(delta) +'_'+ str(depend_nr)
		self.stdout_callback = 'RESULT/pop_size.'+str(popSize) +'/prova.'+str(provaNr)+'/stdout_callback' + str(ID) + '_' + str(delta) +'_'+ str(depend_nr)
		self.stdout_handle = 'RESULT/pop_size.'+str(popSize) +'/prova.'+str(provaNr)+'/stdout_handle' + str(ID) + '_' + str(delta) +'_'+ str(depend_nr)

		self.about_me_wm = AboutMe_WM(delta, energy, ID, x, y, theta, red, green, blue, state)
		self.Alive = 20000

		self.attempted_jobs = 0
		self.completed_jobs = 0
		self.attempted_jobs_depend = 0
		self.completed_jobs_depend = 0
		self.depend_myself = 0
		self.collected_reward = 0

		self.old_state = 1
		
		## These vars are manipulated by multiple threads ###
		self.adaptive_state = []
		self.current_client = []
		self.service_req = []
		self.service_resp = []
		self.service_resp_content = []
		#####################################################

		self.client_index = -1
		self.old_client_index = -1

		#follows the indexing of known_people
		self.helping_interactions = []
		self.total_interactions = []

		# example format [[[e1-pos-inter, e1-tot-inter], [e2-pos-inter, e2-tot-inter] ...], ..], for serv1, serv2.... for the first guy in known_people
		self.capability_expertise = []

		self.timeouts = 0

		self.timeouts_xinteract = []

		#From the list of services select 30% (this number can be modified) for the agent to be providing - at random
		#[id time energy reward ...] ... -> dependencies on other services for instance 4 5 2 1
		#active_servs format: [[5, 100, 3705, 42], [6, 97, 5736, 19], [9, 96, 9156, 4]]
		self.active_servs = simulation_functions.select_services(self.about_me_wm.ID, depend_nr)
		print self.active_servs

		self.write_log_file(self.stdout_log, '[INIT] active_servs: ' + str(self.active_servs) + '\n')

		self.service = []

		self.changed_servs = 1
		self.iteration = 1 

		self.message = Message_Type()
		self.message.id = self.about_me_wm.ID
		self.message.rank = 10
		self.message.group = 1
		self.message.content = ''
		for x in self.active_servs:
			self.message.content = self.message.content + str(x[0]) + '|' 
		self.message.timestamp = time.strftime('%X', time.gmtime())

		## ROS Topics and Services ################################################
		###########################################################################
		self.conn_reset = 0
		rospy.init_node('agent', anonymous=True)

		myservice = '/robot' + str(self.about_me_wm.ID) + '/serve'
		srv = rospy.Service(myservice, Service_One, self.handle_serve)

		self.publish_global = rospy.Publisher('msgs', Message_Type, queue_size=200)
		rospy.Subscriber('trigger', Message_Type, self.callback)

		rospy.sleep(10)
		###########################################################################

	def write_log_file(self, filename, data):
		with open(filename, 'a') as f:
			f.write(data)
	## ROS Callbacks ##################################################################################
	###################################################################################################
	def handle_serve(self, request):
		
		idx = -1

		self.lock.acquire()
		self.handle = self.handle + 1
		local_handle = self.handle

		if request.id in self.current_client:
			idx = self.current_client.index(request.id)
			self.service_resp[idx] = False
			self.service_resp_content[idx] = -1
			self.service_req[idx] = int(request.incoming)
			self.adaptive_state[idx] = True
		else:
			self.service_req.append(int(request.incoming))
			self.current_client.append(request.id)
			self.service_resp.append(False)
			self.service_resp_content.append(-1)
			idx = self.current_client.index(request.id)
			self.adaptive_state.append(True)

		self.write_log_file(self.stdout_handle, '[handle_serve ' + str(local_handle) + '] request.incoming: ' + request.incoming + '\n' + '[handle_serve ' + str(local_handle) + '] request.id: ' + str(request.id) + '\n' + '[handle_serve ' + str(local_handle) + '] ' + 'Receiving request from: %d, for task: %d. Current client: %d\n' % (request.id, self.service_req[idx], self.current_client[idx]) + '[handle_serve ' + str(local_handle) + '] service_resp: %s\n' % str(self.service_resp[idx]))

		print 'Receiving request from: %d, for task: %d \n Current client: %d' % (request.id, self.service_req[idx], self.current_client[idx])
		## normally here would be a good place for filters ;)
		timeout = time.time() + 30 # stop loop 30 sec from now

		print 'service_resp: %s' % str(self.service_resp[idx])
		self.lock.release()

		while not self.service_resp[idx]:
			#time.sleep(0.1)

			if time.time() > timeout:
				print 'timeout'
				self.timeouts = self.timeouts + 1

				self.lock.acquire()
				self.service_resp_content[idx] = -1
				self.adaptive_state[idx] = False
				self.write_log_file(self.stdout_handle, '[handle_serve ' + str(local_handle) + '] timeout, id: ' +str(self.current_client[idx]) +' current adapt step: '+str(self.a)+'\n')
				self.lock.release()
				break

		outgoing = str(self.service_resp_content[idx])
		print 'request outgoing ' + outgoing
		self.lock.acquire()
		self.write_log_file(self.stdout_handle, '[handle_serve ' + str(local_handle) + '] request outgoing ' + outgoing+', client id' + str(self.current_client[idx]) +' current adapt step: '+str(self.a)+'\n')
		self.lock.release()

		return outgoing

	def call_serve(self, server, myid, request, anyone_index):
		other_service = '/robot' + str(server) + '/serve'
		self.call = self.call + 1

		print 'I am %d calling: %s' % (self.about_me_wm.ID, other_service)

		self.write_log_file(self.stdout_log, '[call_serve ' + str(self.call) + '] ' + 'I am %d calling: %s\n' % (self.about_me_wm.ID, other_service))

		self.lock.acquire()
		self.total_interactions[anyone_index] = self.total_interactions[anyone_index] + 1
		self.lock.release()

		service_idx = self.about_me_wm.known_people[anyone_index][2].index(int(request))
		self.lock.acquire()
		self.capability_expertise[anyone_index][service_idx][1] = self.capability_expertise[anyone_index][service_idx][1] + 1
		self.lock.release()

		rospy.wait_for_service(other_service, timeout=60)
		try:
			self.write_log_file(self.stdout_log, '[call_serve ' + str(self.call) + '] ' + 'inside try block, time: %s\n'%str(time.time()))
			serve = rospy.ServiceProxy(other_service, Service_One)
			resp1 = serve(myid, request)
			print resp1.outgoing

			self.write_log_file(self.stdout_log, '[call_serve ' + str(self.call) + '] ' + 'resp1.outgoing: %s\n' % resp1.outgoing)

			if not int(resp1.outgoing) == -1:
				self.lock.acquire()
				self.helping_interactions[anyone_index] = self.helping_interactions[anyone_index] + 1
				self.lock.release()

				if int(resp1.outgoing) == 1:
					self.lock.acquire()
					self.capability_expertise[anyone_index][service_idx][0] = self.capability_expertise[anyone_index][service_idx][0] + 1
					self.lock.release()

			#Calculate perceived willingness
			self.lock.acquire()
			self.about_me_wm.known_people[anyone_index][1] = self.helping_interactions[anyone_index]/float(self.total_interactions[anyone_index])
			self.lock.release()
			print 'perceived willingness from server: %d, is: %f' % (server, self.about_me_wm.known_people[anyone_index][1])

			self.write_log_file(self.stdout_log, '[call_serve ' + str(self.call) + '] ' + 'perceived willingness from server: %d, is: %f\n' % (server, self.about_me_wm.known_people[anyone_index][1]))

			#Calculate perceived expertise for the service
			self.lock.acquire()
			self.about_me_wm.known_people[anyone_index][3][service_idx] = self.capability_expertise[anyone_index][service_idx][0]/float(self.capability_expertise[anyone_index][service_idx][1])
			self.lock.release()
			print 'perceived expertise from server: %d, is: %f' % (server, self.about_me_wm.known_people[anyone_index][3][service_idx])

			self.write_log_file(self.stdout_log, '[call_serve ' + str(self.call) + '] ' + 'perceived expertise from server: %d, is: %f\n' % (server, self.about_me_wm.known_people[anyone_index][3][service_idx]) + '[call_serve ' + str(self.call) + '] ' + 'capability expertise: ' + str(self.capability_expertise) + '\n')
			
			return resp1.outgoing
		except rospy.ServiceException, e:
			print "Service call failed: %s"%e
			self.write_log_file(self.stdout_log, '[call_serve ' + str(self.call) + '] ' + 'Service call failed: %s, at time %s'%(e, str(time.time())))
			self.conn_reset = self.conn_reset + 1
			pass

	def callback(self, data):
		rospy.loginfo(rospy.get_caller_id() + 'I am: %d, I heard %d', self.about_me_wm.ID, data.id)
		# callback_bc modified ONLY here
		self.callback_bc = self.callback_bc + 1

		self.write_log_file(self.stdout_callback, '[callback ' + str(self.callback_bc) + '][ROSPY] I am: %d, I heard %d\n' % (self.about_me_wm.ID, data.id))
		
		guy_id_srv = [data.id, -1]
		guy_id_srv.append([int(x) for x in filter(None, data.content.split('|'))])
		exp = []
		for x in range(0, len(guy_id_srv[2])):
			exp.append(-1)
		guy_id_srv.append(exp)

		self.lock.acquire()
		self.about_me_wm.known_people.append(guy_id_srv)
		self.lock.release()
		print 'known people'
		print self.about_me_wm.known_people

		self.write_log_file(self.stdout_callback, '[callback ' + str(self.callback_bc) + '] known people ' + str(self.about_me_wm.known_people) + '\n')
		#For each new person, append the values for the experiences. FOLLOWS the INDEXING of known_people
		self.lock.acquire()
		self.helping_interactions.append(0)
		self.total_interactions.append(0)
		self.lock.release()

		temp_values = []
		for x in range(0, len(guy_id_srv[2])):
			temp_values.append([0,0])

		self.lock.acquire()
		self.capability_expertise.append(temp_values)
		self.lock.release()
		print self.capability_expertise
		self.write_log_file(self.stdout_callback, '[callback ' + str(self.callback_bc) + '] capability_expertise ' + str(self.capability_expertise) + '\n')
	###################################################################################################

	## FSM -- Mental States #########################################
	#################################################################
	def run_fsm(self):

		while not rospy.is_shutdown():

			self.fsm = self.fsm + 1

			if random.random() > 0.2:
				self.publish_global.publish(self.message)
				print 'Published'
				self.write_log_file(self.stdout_log, '[fsm ' + str(self.fsm) + '] published\n')

			if time.time() > self.TIME + self.DURATION:
				self.lock.acquire()
				for x in self.service_resp:
					self.service_resp[self.service_resp.index(x)] = True
				self.write_log_file(self.stdout_log, '[fsm ' + str(self.fsm) + '] Finished Correctly\n')
				self.lock.release()
				return
			self.lock.acquire()
			if True in self.adaptive_state:
				
				self.write_log_file(self.stdout_log, '[fsm ' + str(self.fsm) + '] current client_index: ' + str(self.client_index) + '\n')
				self.old_client_index = self.client_index
				self.write_log_file(self.stdout_log, '[fsm ' + str(self.fsm) + '] ' + str(self.adaptive_state) + ' ' + str(self.current_client) + '\n')
				self.client_index = self.adaptive_state.index(True)

				self.write_log_file(self.stdout_log, '[fsm ' + str(self.fsm) + '] ' + str(self.adaptive_state) + ' ' + str(self.current_client) + '\n')
				self.old_state = self.about_me_wm.state
				self.about_me_wm.state = 3
				self.write_log_file(self.stdout_log, '[fsm ' + str(self.fsm) + '] ' + str(self.adaptive_state) + ' ' + str(self.current_client) + '\n')
				self.adaptive_state[self.adaptive_state.index(True)] = False
			self.lock.release()

			if self.about_me_wm.state == 1:
				self.wander()
			elif self.about_me_wm.state == 2:
				self.execute()
			elif self.about_me_wm.state == 3:
				self.adapt()
			elif self.about_me_wm.state == 4:
				self.stop()
		
			#rospy.sleep(1)
	#################################################################
	def wander(self):
		self.w = self.w + 1
		print 'wander'
		self.write_log_file(self.stdout_log, '[wander ' + str(self.w) + '] wander\n')

		if random.random() > 0.7:
			self.task_idx = random.randint(1, len(self.active_servs)) - 1 #randint(a,b) kthen int ne [a,b]
			self.service = self.active_servs[self.task_idx]

			print 'Chosen service: ' + str(self.service) + '\n'

			self.attempted_jobs = self.attempted_jobs + 1

			if len(self.service) > 4:
				self.attempted_jobs_depend = self.attempted_jobs_depend + 1

			self.write_log_file(self.stdout_log, '[wander ' + str(self.w) + '] Chosen service: ' + str(self.service) + '\n')

			self.about_me_wm.state = 2
		else:
			print 'do nothing - zot jepi atij qe rri kot :DD'
			self.write_log_file(self.stdout_log, '[wander ' + str(self.w) + '] do nothing - zot jepi atij qe rri kot :DD\n')

	def execute(self):
		self.run_service_step(self.service, self.iteration)	
			
	def adapt(self):
		self.a = self.a + 1
		print 'adapting'
		self.write_log_file(self.stdout_log, '[adapt ' + str(self.a) + '] adapting\n')

		for x in self.active_servs:
			if x[0] == self.service_req[self.client_index]:
				self.task_idx = self.active_servs.index(x)

		#Decide if it is good to accept request
		print 'client: %d, service_resp: %s' % (self.current_client[self.client_index], str(self.service_resp[self.client_index]))

		self.write_log_file(self.stdout_log, '[adapt ' + str(self.a) + '] client: %d, service_resp: %s\n' % (self.current_client[self.client_index], str(self.service_resp[self.client_index])) + '[adapt ' + str(self.a) + '] old serve: %s\n' % (str(self.service)))

		#self.stdout_log.write('[adapt ' + str(self.a) + '] file log: %s\n' % (str(self.stdout_log)))
		#self.stdout_log.write('[adapt ' + str(self.a) + '] old state: %s\n' % (str(self.old_state)))
		#self.stdout_log.write('[adapt ' + str(self.a) + '] current client: %s\n' % (str(self.current_client[self.client_index])))
		#self.stdout_log.write('[adapt ' + str(self.a) + '] new serve: %s\n' % (str(self.active_servs[self.task_idx])))
		rate = -1000

		if self.attempted_jobs == 0:
			rate = 0.0
		else:
			rate = 1.0 * self.completed_jobs / self.attempted_jobs

		accept = self.about_me_wm.keep_request(self.current_client[self.client_index], self.active_servs[self.task_idx], self.old_state, self.service, self.stdout_log, rate)
		if self.handle > 0:
			self.write_log_file(self.stdout_log, '[adapt ' + str(self.a) + '] handled = %d\n' % (self.handle))
			self.timeouts_xinteract.append(1.0 * self.timeouts/self.handle)
		else:
			self.write_log_file(self.stdout_log, '[adapt ' + str(self.a) + '] nope, nope, nope\n')

		print 'accept ' + str(accept)
		self.write_log_file(self.stdout_log, '[adapt ' + str(self.a) + '] accept ' + str(accept) + '\n')

		if accept:
			print 'adapted'
			self.count_posReq = self.count_posReq + 1
			self.write_log_file(self.stdout_log, '[adapt ' + str(self.a) + '] adapted\n')

			self.attempted_jobs = self.attempted_jobs + 1

			self.iteration = 1
			self.about_me_wm.state = 2
			self.service = self.active_servs[self.task_idx]

			if len(self.service) > 4:
				self.attempted_jobs_depend = self.attempted_jobs_depend + 1

			self.helping = True
			print self.service
			self.write_log_file(self.stdout_log, '[adapt ' + str(self.a) + '] service: ' + str(self.service) + '\n' + '[adapt ' + str(self.a) + '] helping: ' + str(self.helping) + '\n')

		else:
			print 'keep at what you\'re doing'
			#praktikisht e le pergjysem kerkesen
			self.write_log_file(self.stdout_log, '[adapt ' + str(self.a) + '] keep at what you\'re doing\n' + '[adapt ' + str(self.a) + '] before if: current client_index: ' + str(self.client_index) + '\n')
			if not self.client_index == -1:
				self.lock.acquire()
				self.service_req[self.client_index] = -1
				self.service_resp_content[self.client_index] = -1 #<----- changed this today
				self.service_resp[self.client_index] = True
				self.lock.release()
			
			self.client_index = self.old_client_index
			self.write_log_file(self.stdout_log, '[adapt ' + str(self.a) + '] after old state: current client_index: ' + str(self.client_index) + '\n')

			self.about_me_wm.state = self.old_state

	def stop(self):
		print 'what the hell am I doing in here'
	##################################################################

	## Execution STEP #####################################################
	#######################################################################
	def run_service_step(self, service, i):
		self.run_step = self.run_step + 1

		depend = False
		timeout = time.time() + 10

		if len(service) > 4:
			depend = True
			#self.attempted_jobs_depend = self.attempted_jobs_depend + 1
#rregullo kete qe te mos quaje te bere ato jobs qe kane deshtuar
		if i <= service[1] and not depend:
			print 'Doing task %d, iteration: %d' % (service[0], i)

			self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] Doing task %d, iteration: %d\n' % (service[0], i))
			self.iteration = self.iteration + 1

			if self.iteration > service[1]:
				self.about_me_wm.state = 1
				self.iteration = 1

				self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] client_index %d, helping %s\n' % (self.client_index, self.helping))

				if self.helping:
					self.service_req[self.client_index] = -1
					if random.random() > 0: #it will always succeed
						self.lock.acquire()
						self.service_resp_content[self.client_index] = 1
						self.lock.release()
						self.completed_jobs = self.completed_jobs + 1
						self.collected_reward = self.collected_reward + service[3]

						print 'Helping, Task %d, done, wandering again' % service[0]
						self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] Helping, Task %d, done, wandering again\n' % service[0])

					else:
						self.lock.acquire()
						self.service_resp_content[self.client_index] = 0
						self.lock.release()
						print 'Helping, Task %d, failed, wandering again' % service[0]
						self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] Helping, Task %d, failed, wandering again\n' % service[0])

					self.lock.acquire()
					self.service_resp[self.client_index] = True
					self.lock.release()
					self.helping = False
					self.client_index = -1
				else:
					self.completed_jobs = self.completed_jobs + 1
					self.collected_reward = self.collected_reward + service[3]

					print 'Task %d, done, wandering again' % service[0]
					self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] Task %d, done, wandering again\n' % service[0])

		elif i <= service[1] and depend:
			print 'Doing task %d, iteration. Depend is true' % service[0]
			self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] Doing task %d, iteration. Depend is true\n' % service[0])

			stringing = str(service[4])
			if not len(self.about_me_wm.known_people) == 0:
				anyone = False
				anyone_id = []
				anyone_id_idx = []
				subset_known = []
				anyone_index = -1
				jj = -1

				for x in self.about_me_wm.known_people:
					if service[4] in x[2]:
						subset_known.append(x)
						anyone_id.append(x[0])
						anyone = True
						anyone_id_idx.append(self.about_me_wm.known_people.index(x))

				self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] anyone_id: ' + str(anyone_id) + '\n' + '[run_step ' + str(self.run_step) + '] anyone_id_idx: ' + str(anyone_id_idx) + '\n' + '[run_step ' + str(self.run_step) + '] subset: ' + str(subset_known) + '\n')

				if anyone:
					## function to choose the server -- right now random from the list above
					if self.run_step < self.steps_b4_equilibrium:
						jj = random.randint(0, len(anyone_id) - 1)
						self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] jj at random: %d\n' % jj)
					else:
						if random.random() < 0.8:
							jj = subset_known.index(max(subset_known, key=lambda x: x[1]))
							self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] jj using lambda function: %d\n' % jj)
						else:
							jj = random.randint(0, len(anyone_id) - 1)
							self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] jj at random after equilibrium: %d\n' % jj)
					anyone_index = anyone_id_idx[jj]
					server = anyone_id[jj]

					self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] anyone_id: ' + str(anyone_id[jj]) + '\n' + '[run_step ' + str(self.run_step) + '] anyone_index: ' + str(anyone_index) + '\n' + '[run_step ' + str(self.run_step) + '] server: ' + str(server) + '\n')
					print server
					
					server_resp = -1000

					try:
						server_resp = int(self.call_serve(server, self.about_me_wm.ID, stringing, anyone_index))
					except:
						self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] it went to heell: ' + '\n')
						server_resp = -1
						pass

					print 'checking after service return: ' + str(server_resp)
					self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] checking after service return: ' + str(server_resp) + '\n')
					self.about_me_wm.state = 1
					self.iteration = 1

					if server == self.client_index:
						self.count_loops = self.count_loops + 1
						self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] counting loops + 1' + '\n')
					#here is where you update the values for the agent's expertise and perceived willingness to help
					if server_resp == 1:
						self.completed_jobs = self.completed_jobs + 1
						self.completed_jobs_depend = self.completed_jobs_depend + 1
						self.collected_reward = self.collected_reward + service[3]

						print 'Task %d, done, wandering again' % service[0]
						self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] Task %d, done, wandering again\n' % service[0])
					else:
						prob = random.random()
						self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] prob %d: \n' % prob)
						if prob <= 0.3:
							self.completed_jobs = self.completed_jobs + 1
							self.completed_jobs_depend = self.completed_jobs_depend + 1
							self.collected_reward = self.collected_reward + service[3]
							self.depend_myself = self.depend_myself + 1

							print 'Task %d, done, wandering again' % service[0]
							self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] Task %d, done by myslef, after failed help request\n' % service[0])
							server_resp = 1
						else:
							print 'Task %d, failed, wandering again' % service[0]
							self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] Task %d, failed, both help request and by myself\n' % service[0])

					if self.helping:
						self.lock.acquire()
						self.service_req[self.client_index] = -1
						self.service_resp_content[self.client_index] = server_resp
						self.service_resp[self.client_index] = True
						self.lock.release()
						self.helping = False
						self.client_index = -1
				else:
					server_resp = 0

					self.COUNT_noones = self.COUNT_noones + 1
					print 'no one to ask that has this capability'
					self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] no one to ask that has this capability\n' + '[run_step ' + str(self.run_step) + '] Doing task %d\n' % service[0])

					self.about_me_wm.state = 1
					if self.helping:
						self.lock.acquire()
						self.service_req[self.client_index] = -1
						self.service_resp_content[self.client_index] = server_resp
						self.service_resp[self.client_index] = True
						self.lock.release()
						self.helping = False
						self.client_index = -1
				#self.service_req = -1 --- careful with this one
			else:
				print 'no one to ask'
				self.COUNT_noones = self.COUNT_noones + 1
				self.write_log_file(self.stdout_log, '[run_step ' + str(self.run_step) + '] no one to ask\n' + '[run_step ' + str(self.run_step) + '] Doing task %d\n' % service[0])

				server_resp = 0
				if self.helping:
					self.lock.acquire()
					self.service_req[self.client_index] = -1
					self.service_resp_content[self.client_index] = server_resp
					self.service_resp[self.client_index] = True
					self.lock.release()
					self.helping = False
					self.client_index = -1
				self.about_me_wm.state = 1
			
	#######################################################################

## MAIN #######################################################################
###############################################################################
if __name__ == '__main__':
	## Redirect stderr to file located in home/.ros/ ######################
	agent_id = rospy.get_param('brain_node/myID')

	delta = rospy.get_param('brain_node/myDelta')

	depends = rospy.get_param('brain_node/myDepend')

	popSize = rospy.get_param('brain_node/popSize')

	provaNr = rospy.get_param('brain_node/provaNr')

	print delta

	starttime = time.time()

	stderr_file = 'RESULT/pop_size.'+str(popSize) +'/prova.'+str(provaNr)+'/log_err_' + str(agent_id) +'_'+ str(delta) +'_'+ str(depends)
	f = open(stderr_file, 'w')
	orig_stderr = sys.stderr
	sys.stderr = f

	energy = random.randint(1000, 4000)
	print delta
	print energy
	print 'my id: %d' % agent_id
	agent = Agent(delta, energy, agent_id, 2,3, 3.14, 0.5, 0.5, 0.5, 1, depends, popSize, provaNr)

	agent.write_log_file(agent.stdout_log, 'id: %d \ndelta: %f\nenergy: %f\n' % (agent_id, delta, energy))

	try:
		agent.run_fsm()
	except rospy.ROSInterruptException:
		pass
	except (RuntimeError, TypeError, NameError):
		pass
	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise
	finally:
		sys.stderr = orig_stderr
		f.close()

		dur = time.time() - starttime

		#WRITE results to files

		filename = 'RESULT/pop_size.'+str(popSize) +'/prova.'+str(provaNr)+'/reward_results_' + str(delta) +'_'+ str(depends) + '_'+ str(agent.about_me_wm.ID)
		agent.write_log_file(filename, str(agent.about_me_wm.ID) + '	' + str(agent.timeouts) + '	' +str(agent.handle)+'	'+ str(agent.depend_myself) + '	'+str(agent.completed_jobs_depend) +'	'+str(agent.attempted_jobs_depend) + '	' + str(agent.completed_jobs) + '	' + str(agent.attempted_jobs) +'	'+ str(agent.collected_reward) + '	' + str(agent.count_loops) + '	'+str(dur)+'	'+str(agent.COUNT_noones)+'	'+str(agent.count_posReq)+'	'+str(agent.conn_reset)+'\n')
		#agent.write_log_file(filename, str(datetime.datetime.now()) + '\n')

		filename1 = 'RESULT/pop_size.'+str(popSize) +'/prova.'+str(provaNr)+'/moving-delta_results_' + str(delta) +'_'+ str(depends) + '_'+ str(agent.about_me_wm.ID)
		agent.write_log_file(filename1, str(agent.about_me_wm.ID) + '\n')
		average_delta = 0
		nr_deltas = 0
		for x in agent.about_me_wm.moving_delta:
			agent.write_log_file(filename1, str(x) + '\n')
			if x:
				b = x
				b.pop(0)
				for y in b:
					average_delta = average_delta + y
					nr_deltas = nr_deltas + 1
		agent.write_log_file(filename1, str(average_delta)+'	'+str(nr_deltas)+'\n\n')
		#agent.write_log_file(filename1, str(datetime.datetime.now()) + '\n')

		filename2 = 'RESULT/pop_size.'+str(popSize) +'/prova.'+str(provaNr)+'/cap-expertise_results_' + str(delta) +'_'+ str(depends) + '_'+ str(agent.about_me_wm.ID)
		agent.write_log_file(filename2, str(agent.about_me_wm.ID) + '\n')
		for x in agent.about_me_wm.known_people:
			agent.write_log_file(filename2, '	' + str(x[1]) + '\n')
			agent.write_log_file(filename2, '	' + str(x) + '\n')
			agent.write_log_file(filename2, '	' + str(agent.capability_expertise[agent.about_me_wm.known_people.index(x)]) + '\n\n')
		agent.write_log_file(filename2, '\n')

		filename3 = 'RESULT/pop_size.'+str(popSize) +'/prova.'+str(provaNr)+'/moving_delta_sorted_' + str(delta) +'_'+ str(depends) + '_'+ str(agent.about_me_wm.ID)
		agent.write_log_file(filename3, str(agent.about_me_wm.ID) + '	')
		for x in agent.about_me_wm.moving_delta_sorted:
			agent.write_log_file(filename3, str(x) + '	')
		agent.write_log_file(filename3, '\n')

		filename4 = 'RESULT/pop_size.'+str(popSize) +'/prova.'+str(provaNr)+'/moving_drop_jobs_' + str(delta) +'_'+ str(depends) + '_'+ str(agent.about_me_wm.ID)
		agent.write_log_file(filename4, str(agent.about_me_wm.ID) + '	')
		for x in agent.about_me_wm.moving_drop_jobs:
			agent.write_log_file(filename4, str(x) + '	')
		agent.write_log_file(filename4, '\n')
		agent.write_log_file(filename4, str(agent.about_me_wm.ID) + '	')
		for x in agent.timeouts_xinteract:
			agent.write_log_file(filename4, str(x) + '	')
		agent.write_log_file(filename4, '\n')


###############################################################################
