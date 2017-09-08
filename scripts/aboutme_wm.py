#!/usr/bin/env python
#two little piggies went for a walk... and gotten eaten by the wolf 

from GITagent.msg import *
from math import sin, cos
import numpy as np
import random

class AboutMe_WM:
	# the placement of delta and ID (name of agent) in the working memory -> this seems like the case in which processing modules shortcut to lterm
	# as such this should be reviewed quite soon
	def __init__(self, delta, energy, ID, x, y, theta, red, green, blue, state):
		self.delta = delta
		self.energy = energy
		self.ID = ID
		#format [[1, [2, 3, 4]], [2, [4, 5]], [3, [6, 7]]]
		#need to be added: [[1, perceived_willingness, [2, 3, 4], [e1, e2, e3]], ....]
		self.known_people = []

		## each row contains client id and subsequently the final delta for each interaction
		self.moving_delta = []
		self.moving_delta_sorted = [self.delta]
		self.moving_drop_jobs = [self.delta]
		self.moving_depend_done = [self.delta]

		self.state = state

		self.past_jobs_dropped = 0
		self.HIGH = 0.7
		self.LOW = 0.3
		self.step = 0.05

	def write_log_file(self, filename, data):
		with open(filename, 'a') as f:
			f.write(data)

	# a more interesting energy loss could be adopted here - for instance some function that models the energy loss of some robot (kbs come to mind)
	def energy_loss(self):
		self.energy = self.energy - 1

	def update_pos(self, step):
		self.pos.x_pos = self.pos.x_pos + step * cos(self.pos.theta_pos)
		self.pos.y_pos = self.pos.y_pos + step * sin(self.pos.theta_pos)
		#print "cos: %f, sin: %f" % (cos(self.pos.theta_pos), sin(self.pos.theta_pos))
		if random.random() > 0.8:
			self.pos.theta_pos = self.pos.theta_pos + 1

	def keep_request(self, client, new_service, state, old_service, stdout_log, jobs_dropped, depend_done):
		accept = False
		print self.known_people
		self.write_log_file(stdout_log, '[keep request] just entered keep request\n')

		if client == -1:
			print 'client %d' % client
			self.write_log_file(stdout_log, '[keep request] client = -1\n')
		else:
			self.write_log_file(stdout_log, '[keep request] inside else\n')
			check_rand = random.random()
			self.write_log_file(stdout_log, '[keep request] check random, check_rand: %f\n' % check_rand)
			#if check_rand < self.reward_delta(client, new_service, state, old_service, stdout_log):
			#if check_rand < self.mirror_delta(client, stdout_log):
			#if check_rand < self.delta:
			jobs_dropped = 1 - jobs_dropped
			if check_rand < self.dep_delta(client, stdout_log, jobs_dropped, depend_done):
				accept = True
		return accept

	def dep_delta(self, client, stdout_log, jobs_dropped, depend_done):	
		self.write_log_file(stdout_log, '[dep_delta] into the wild\n')
		## what you need to make only one agent dynamic ############################################################################################################
		if self.ID > 10:
			drop_rate = jobs_dropped - self.past_jobs_dropped
			self.write_log_file(stdout_log, '[dep_delta] dropped: %f, past_dropped: %f, past delta: %f\n' % (jobs_dropped, self.past_jobs_dropped, self.delta))

			#self.delta = self.delta - (jobs_dropped - self.past_jobs_dropped) * jobs_dropped
			if jobs_dropped > self.HIGH:
				self.delta = self.delta - self.step
				self.write_log_file(stdout_log, '[dep_delta] delta decreased %f by step %f\n'%(self.delta, self.step))
			elif jobs_dropped < self.LOW:
				self.delta = self.delta + self.step
				self.write_log_file(stdout_log, '[dep_delta] delta increased %f by step %f\n'%(self.delta, self.step))
			elif abs(drop_rate) >= 0.01:
				self.write_log_file(stdout_log, '[dep_delta] entered else, L < jb_d < H\n')
				inc_dec = 1 if drop_rate >= 0 else -1
				self.delta = self.delta - inc_dec*self.step
				self.write_log_file(stdout_log, '[dep_delta] delta change %f by step %f, inc_dec = %d\n'%(self.delta, self.step, inc_dec))
			else:
				self.write_log_file(stdout_log, '[dep_delta] delta doesn\'t change, else condition, %f by step %f\n'%(self.delta, self.step))	

			#fit to [0,1]
			if self.delta > 1.0:
				self.delta = 1.0
			elif self.delta < 0.0:
				self.delta = 0.0

			self.write_log_file(stdout_log, '[dep_delta] delta = %f\n' % self.delta)
			self.past_jobs_dropped = jobs_dropped
		###########################################################################################################################################################

		self.moving_delta_sorted.append(self.delta)
		self.moving_drop_jobs.append(jobs_dropped)
		self.moving_depend_done.append(depend_done)

		self.write_log_file(stdout_log, '[dep_delta] moving_delta_sorted = %s\n' % str(self.moving_delta_sorted))
		self.write_log_file(stdout_log, '[dep_delta] moving_drop_jobs = %s\n' % str(self.moving_drop_jobs))

		match = False
		if self.moving_delta:
			for x in self.moving_delta:
				if client in x:
					self.moving_delta[self.moving_delta.index(x)].append(self.delta)
					match = True
					break
			if not match:
				self.moving_delta.append([client, self.delta])
		else:
			self.moving_delta.append([client, self.delta])

		return self.delta

	def just_delta(self):
		return self.delta

	def reward_delta(self, client, service, old_state, old_service, stdout_log):
		mirror = self.mirror_delta(client, stdout_log)
		if old_state == 1:
			print 'i am doing nothing - just mirror past behaviour'
			self.write_log_file(stdout_log, 'I am doing nothing - just mirror past behaviour\n' + 'new mirror: %f\n' % mirror)
		elif old_state == 2:
			print 'i am working - check the gain'
			print 'old gain: %d, new gain: %d\n' % (old_service[3], service[3])
			self.write_log_file(stdout_log, 'I am working - check gain\n' + 'old gain: %d, new gain: %d\n' % (old_service[3], service[3]))
			gain_loss = 1.0 * (service[3] - old_service[3])/old_service[3]
			print 'gain or loss: %f' % gain_loss
			self.write_log_file(stdout_log, 'gain or loss: %f' % gain_loss)
			mirror = mirror + gain_loss * mirror
			print 'new mirror: %f\n' % mirror
			self.write_log_file(stdout_log,'new mirror: %f\n' % mirror)
		else:
			print 'this shouldn\'t happen nerd'
			self.write_log_file(stdout_log,'this shouldn\'t happen nerd')
			mirror = 0.5

		match = False
		if self.moving_delta:
			for x in self.moving_delta:
				if client in x:
					self.moving_delta[self.moving_delta.index(x)].append(mirror)
					match = True
					break
			if not match:
				self.moving_delta.append([client, mirror])
		else:
			self.moving_delta.append([client, mirror])
		#print 'here is moving_delta: ' + str(self.moving_delta)

		return mirror	

	def mirror_delta(self, client, stdout_log):
		## CAREFUL - nuk po konsideron se cfare ndodh kur serveri nuk e njeh klientin!!!!
		## Plus duhet te shtosh nje mase per degree of certainty, ne menyre qe te mos penalizosh bashkeveprimet e reja!!!
				
		perceived_willingness = self.delta
		for x in self.known_people:
			if client == x[0]:
				if x[1] == -1:
					self.write_log_file(stdout_log, 'unknown interaction\n')
				else:
					perceived_willingness = x[1]
					self.write_log_file(stdout_log, 'known interaction\n')
				break

		context_delta = (self.delta + perceived_willingness) / 2
		self.write_log_file(stdout_log, 'context_delta: %f\n' % context_delta)
		return context_delta
