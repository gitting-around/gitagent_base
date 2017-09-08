#!/usr/bin/env python
#two little piggies went for a walk... and gotten eaten by the wolf 

from GITagent.msg import *
from math import sin, cos
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

		self.state = state

	# a more interesting energy loss could be adopted here - for instance some function that models the energy loss of some robot (kbs come to mind)
	def energy_loss(self):
		self.energy = self.energy - 1

	def update_pos(self, step):
		self.pos.x_pos = self.pos.x_pos + step * cos(self.pos.theta_pos)
		self.pos.y_pos = self.pos.y_pos + step * sin(self.pos.theta_pos)
		#print "cos: %f, sin: %f" % (cos(self.pos.theta_pos), sin(self.pos.theta_pos))
		if random.random() > 0.8:
			self.pos.theta_pos = self.pos.theta_pos + 1

	def keep_request(self, client, new_service, state, old_service, stdout_log):
		accept = False
		print self.known_people
		stdout_log.write('[keep request] just entered keep request\n')

		if client == -1:
			print 'client %d' % client
			stdout_log.write('[keep request] client = -1\n')
		else:
			stdout_log.write('[keep request] inside else\n')
			check_rand = random.random()
			stdout_log.write('[keep request] check random, check_rand: %f\n' % check_rand)
			if check_rand < self.reward_delta(client, new_service, state, old_service, stdout_log):
			#if check_rand < self.mirror_delta(client, stdout_log):
			#if check_rand < self.delta:
				accept = True
		return accept
	
	def just_delta(self):
		return self.delta

	def reward_delta(self, client, service, old_state, old_service, stdout_log):
		mirror = self.mirror_delta(client, stdout_log)
		if old_state == 1:
			print 'i am doing nothing - just mirror past behaviour'
			stdout_log.write('I am doing nothing - just mirror past behaviour\n')
			stdout_log.write('new mirror: %f\n' % mirror)
		elif old_state == 2:
			print 'i am working - check the gain'
			stdout_log.write('I am working - check gain\n')
			print 'old gain: %d, new gain: %d\n' % (old_service[3], service[3])
			stdout_log.write('old gain: %d, new gain: %d\n' % (old_service[3], service[3]))
			gain_loss = 1.0 * (service[3] - old_service[3])/old_service[3]
			print 'gain or loss: %f' % gain_loss
			stdout_log.write('gain or loss: %f' % gain_loss)
			mirror = mirror + gain_loss * mirror
			print 'new mirror: %f\n' % mirror
			stdout_log.write('new mirror: %f\n' % mirror)
		else:
			print 'this shouldn\'t happen nerd'
			stdout_log.write('this shouldn\'t happen nerd')
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
					stdout_log.write('unknown interaction\n')
				else:
					perceived_willingness = x[1]
					stdout_log.write('known interaction\n')
				break

		context_delta = (self.delta + perceived_willingness) / 2
		stdout_log.write('context_delta: %f\n' % context_delta)
		return context_delta
