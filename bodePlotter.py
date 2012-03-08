from numpy import logspace, log10, mean, linspace
from connectClient import CEE
import pylab
import time

CEE = CEE()
pylab.ion()

channel = 'a'
periodCount = 10 

sampleTime = CEE.devInfo['sampleTime']
maxFreq = (1/sampleTime)/200
# maximum frequency = sampling rate / 20

frequencies = logspace(log10(10), log10(maxFreq), 40)
#log-spaced array of frequencies
amplitudes = []
phases = []

def findPhases(maxesA, maxesB):
	phases = []
	print maxesA
	print maxesB
	maxesA = [ maxA - maxesA[0] for maxA in maxesA ]
	maxesB = [ maxB - maxesA[0] for maxB in maxesB ]
	print maxesA
	print maxesB
	maxesA = maxesA[1:-1]
	maxesB = maxesB[0:-2]
	print maxesA
	print maxesB
	print ''
	for i in range(1, len(maxesA)):
		phase = ( maxesB[i] - maxesA[i] ) / float(maxesA[1])
		# calculate percent difference between spacing of two events
		phase = phase * 180
		# normalize to degrees
		phases.append(phase)
	return phases

def findLocalMaxes(values, a):
	chunkwidth = len(values)/periodCount
	# determine samples per period
	split = [values[i:i+chunkwidth] for i in range(0, len(values), chunkwidth)]
#	[pylab.axvline(x=point, color='r') for point in [i+chunkwidth for i in range(1, len(values), chunkwidth)]]
	# split into periods
	localMaxes = map(max, split)
	# find local maximums
	localMaxTimes = [ (chunk.index(localMax) + split.index(chunk)*chunkwidth)
		for localMax, chunk in zip(localMaxes, split) ]
#	pylab.plot(values)
#	pylab.plot(localMaxTimes, localMaxes, 'ro')
	# find indexes of local maximums
	return localMaxes, localMaxTimes
	# trim the garbage datapoints and return the information

for frequency in frequencies:
	setResponse = CEE.setOutput(channel, 'v', 2.5, 'sine', 2.5, .1, 0, 0)
	setResponse = CEE.setOutput(channel, 'v', 2.5, 'sine', 2.5, frequency, 1, 0)
	# source sine wave with full-scale voltage range at target frequency
	sampleCount = int( ( (1/frequency) * periodCount ) / sampleTime)
	# do math to get the equivalent of 'periodCount' in samples
	v, i = CEE.getInput(channel, 0, sampleCount, setResponse['startSample'])
	i = CEE.getInput('b', 0, sampleCount, setResponse['startSample'])[0]
	# get samples from CEE
	vMaxes, vMaxTimes = findLocalMaxes(v, True)
	iMaxes, iMaxTimes = findLocalMaxes(i, False)
	# get timestamps and maximum values for voltage and current
	amplitudes.append(mean(iMaxes))
	# calculate and record amplitude from array of local maximum currents
	phases.append(mean(findPhases(vMaxTimes, iMaxTimes)))
	# calculate and record phases from v/i maximums' timestamps 

pylab.figure()
pylab.subplot(2,1,1)
pylab.loglog(frequencies, amplitudes, '.')
#pylab.ylim(0,5)
pylab.ylabel("mean peak current")
pylab.subplot(2,1,2)
pylab.semilogx(frequencies, phases, '.')
pylab.ylabel("phase shift in degrees")
pylab.xlabel("frequency")
