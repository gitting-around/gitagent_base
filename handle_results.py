#!/usr/bin/env python
# This function takes the results files one by one and does the following computations
# Calculates: depend_complete, depend_others_complete, reward_xjob, interrupts, jobs dropped
# puts the different values in 5 different matrices
# after the iteration over all the files is over, it puts the matrices into seperate files
# in the end it plots the results into 3D and heat map
import sys
import os.path
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

def extract_values(deltas, dependencies):

	depend_matrix = [[-1]*len(dependencies) for _ in range(len(deltas))]
	depend_other = [[-1]*len(dependencies) for _ in range(len(deltas))]
	reward_xjob = [[-1]*len(dependencies) for _ in range(len(deltas))]
	interrupts = [[-1]*len(dependencies) for _ in range(len(deltas))]
	jobs_dropped = [[-1]*len(dependencies) for _ in range(len(deltas))]

	print depend_matrix

	for l in range(len(deltas)):
		for k in range(len(dependencies)):
			filename = 'all_reward_results_'+str(deltas[l])+'_'+str(dependencies[k])
			if os.path.isfile(filename):
				with open(filename, 'r') as results:
					res_dm = 0
					res_da = 0
					res_dc = 0
					res_noones = 0
					res_rw = 0
					res_ja = 0
					res_jc = 0
					res_int = 0
					res_req = 0
					for line in results:
						iline = [int(float(i)) for i in line.split('\t')]
						#CAREFUL YOU HAVE MORE COLUMNS IN LATER VERSIONS OF THE PROGRAM
						res_int = res_int + iline[1]
						res_req = res_req + iline[2]
						res_noones = res_noones + iline[11]
						res_dm = res_dm + iline[3]
						res_dc = res_dc + iline[4]
						res_da = res_da + iline[5]
						res_jc = res_jc + iline[6]
						res_ja = res_ja + iline[7]
						res_rw = res_rw + iline[8]
				depend_matrix[l][k] = 1.0 * res_dc / (res_da - res_noones)
				depend_other[l][k] = 1.0 * (res_dc - res_dm) / (res_da - res_noones)
				reward_xjob[l][k] = 1.0 * res_rw / res_jc
				interrupts[l][k] = 1.0 * res_int / res_req
				jobs_dropped[l][k] = 1.0 - 1.0 * res_jc / (res_ja - res_noones)
			else:
				depend_matrix[l][k] = -1
				depend_other[l][k] = -1
				reward_xjob[l][k] = -1
				interrupts[l][k] = -1
				jobs_dropped[l][k] = -1
	for x in depend_matrix:
		print x
	print '\n'
	for x in depend_other:
		print x
	print '\n'
	for x in reward_xjob:
		print x
	print '\n'
	for x in interrupts:
		print x
	print '\n'
	for x in jobs_dropped:
		print x
	print '\n'

	temp_delta = deltas

	#plot3D('depend', deltas, dependencies, depend_matrix)
	#plotHeatMap('depend', deltas, dependencies, depend_matrix)

	#plot3D('jobs_dropped', deltas, dependencies, jobs_dropped)
	#plotHeatMap('jobs_dropped', deltas, dependencies, jobs_dropped)

	#plot3D('reward_xjob', deltas, dependencies, reward_xjob)
	#plot3D('interrupts', deltas, dependencies, interrupts)
	#plotHeatMap('interrupts', deltas, dependencies, interrupts)

	#plot3D('depend_other', deltas, dependencies, depend_other)
	#plotHeatMap('depend_other', deltas, dependencies, depend_other)

	write2File('depend', temp_delta, dependencies, depend_matrix)
	write2File('jobs_dropped', deltas, dependencies, jobs_dropped)
	write2File('reward_xjob', temp_delta, dependencies, reward_xjob)
	write2File('interrupts', deltas, dependencies, interrupts)
	write2File('jobs_dropped', temp_delta, dependencies, jobs_dropped)

#careful how YOU NAME STUFF
def plot3D(tipi, deltas, deps, matrix):

	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1, projection='3d')
	X = np.array(deps)
	print X
	print deps
	print deltas
	Y = np.array(deltas)
	print 'below'
	print Y
	X, Y = np.meshgrid(X, Y)
	Z = np.array(matrix)

	print X
	print Y
	print Z

	ax.set_xlabel('Dependency Degree')
	ax.set_ylabel('Deltas')
	ax.set_zlabel(tipi)

	scat =  ax.scatter(X,Y,Z)
	#surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0, antialiased=False)

	ax.set_zlim3d(0, 1)
	plt.savefig(tipi+'_3D.jpeg')
	plt.show()

#Rezultati nuk ngjan tamam!
def plotHeatMap(tipi, deltas, deps, matrix):
	#X = np.array(deps)
	#Y = np.array(deltas)
	temp_delta = list(deltas)
	temp_delta.append(1.1)
	temp_dep = list(deps)
	temp_dep.append(125)
	X, Y = np.meshgrid(temp_dep, temp_delta)
	Z = np.array(matrix)
	plt.pcolormesh(X, Y, Z)
	plt.colorbar()
	plt.savefig(tipi+'_heatmap.jpeg')

def write2File(tipi, deltas, deps, matrix):
	temp_delta = list(deltas)
	with open(tipi, 'w') as results:
		results.write('	')
		for x in deps:
			results.write(str(x) + '		')
		results.write('\n')

		for row in matrix:
			results.write(str(temp_delta.pop(0)) + '	')
			for x in row:
				results.write(str(x) + '	')
			results.write('\n')

if __name__ == '__main__':

	if len(sys.argv) == 3:
		filename = sys.argv[1]
		tipi = sys.argv[2]
		deltas = [0.0, 0.25, 0.5, 0.75, 1.0]
		dependencies = [10, 25, 50, 75, 100]
		matrix = []
		with open(filename, 'r') as results:
			for lines in results:
				matrix.append([float(i) for i in lines.split()])
		plotHeatMap(tipi, deltas, dependencies, matrix)

	elif len(sys.argv) == 7:
		nr_deltas = int(sys.argv[1])
		delta_step = int(sys.argv[2])
		delta_init = float(sys.argv[3])
		nr_dep = int(sys.argv[4])
		dep_step = int(sys.argv[5])
		dep_init = int(sys.argv[6])

		#build the deltas & dependencies lists
		deltas = []
		deltas.append(delta_init)
		for i in range(nr_deltas - 1):
			deltas.append(deltas[i] + delta_step)
		print deltas

		dependencies = []
		dependencies.append(dep_init)
		for i in range(nr_dep - 1):
			dependencies.append(dependencies[i] + dep_step)
		print dependencies

		extract_values(deltas, dependencies)
	elif len(sys.argv) == 4:
		nr_deltas = int(sys.argv[1])
		delta_step = float(sys.argv[2])
		delta_init = float(sys.argv[3])

		#build the deltas & dependencies lists
		deltas = []
		deltas.append(delta_init)
		for i in range(nr_deltas - 1):
			deltas.append(deltas[i] + delta_step)
		print deltas
		dependencies = [10, 25, 50, 75, 100]

		extract_values(deltas, dependencies)
	elif len(sys.argv) < 2:
		print 'take it with default values'
		deltas = [0.0, 0.5, 1.0]
		dependencies = [10, 50, 100]
		extract_values(deltas, dependencies)
	else:
		print "Usage: \n1. Either no arguments -> default values\n2. Or: nr_deltas step delta_init_val nr_dependencies step dependencies_init_val\n"
