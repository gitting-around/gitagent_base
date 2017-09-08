#self.delta = self.delta - (jobs_dropped - self.past_jobs_dropped) * jobs_dropped
if self.delta <= self.LOW and jobs_dropped < self.HIGH:
	self.delta = self.delta + self.step
	self.write_log_file(stdout_log, '[dep_delta] delta increased by step\n')
elif self.delta > self.LOW and jobs_dropped >= self.HIGH:
	self.delta = self.delta - self.step
	self.write_log_file(stdout_log, '[dep_delta] delta decreased by step\n')
elif (self.delta < self.LOW and jobs_dropped > self.HIGH) or (self.delta > self.HIGH and jobs_dropped < self.LOW):
	self.write_log_file(stdout_log, '[dep_delta] do nothing\n')
elif jobs_dropped < self.LOW:
	self.delta = self.delta + self.step
	self.write_log_file(stdout_log, '[dep_delta] delta increased by step, delta = %f, jobs dropped = %f\n' % (self.delta, jobs_dropped))
elif jobs_dropped > self.HIGH:
	self.delta = self.delta - self.step
	self.write_log_file(stdout_log, '[dep_delta] delta DEcreased by step, delta = %f, jobs dropped = %f\n' % (self.delta, jobs_dropped))
else:
	self.write_log_file(stdout_log, '[dep_delta] big nope: delta = %f, drops = %f\n' % (self.delta, jobs_dropped))



if jobs_dropped > self.HIGH:
	self.step = (self.HIGH + self.LOW)/2
	self.delta = self.delta - self.step
	self.write_log_file(stdout_log, '[dep_delta] delta decreased %f by step %f\n'%(self.delta, self.step))
elif jobs_dropped < self.LOW:
	self.step = (self.HIGH + self.LOW)/2
	self.delta = self.delta + self.step
	self.write_log_file(stdout_log, '[dep_delta] delta increased %f by step %f\n'%(self.delta, self.step))
else:
	self.step = jobs_dropped - self.past_jobs_dropped
	self.delta = -self.step
	self.write_log_file(stdout_log, '[dep_delta] delta change %f by step %f\n'%(self.delta, self.step))

#fit to [0,1]
if self.delta > 1.0:
	self.delta = 1.0
elif self.delta < 0.0:
	self.delta = 0.0
