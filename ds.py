from __future__ import print_function
import math
import pigpio

class sensor:

	def __init__(self, pi, gpio):

		self.pi = pi
		self.gpio = gpio

		self._start_tick = None
		self._last_tick = None
		self._low_ticks = 0
		self._high_ticks = 0
		self._last_level = 0

		self.wrong_level_count = 0
		self.on_measure = False

		pi.set_mode(gpio, pigpio.INPUT)

		self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

	# Method for calculating Ratio and Concentration
	def read(self):

		interval = self._low_ticks + self._high_ticks

		if interval > 0:
			ratio = float(self._low_ticks)/float(interval)*100.0
			conc = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62
		else:
			ratio = 0
			conc = 0.0

		self._start_tick = None
		self._last_tick = None
		self._low_ticks = 0
		self._high_ticks = 0
		self._last_level = 0

		wrong_level_count = self.wrong_level_count
		self.wrong_level_count = 0

		return (self.gpio, ratio, conc, wrong_level_count)

	def _cbf(self, gpio, level, tick):

		if self.on_measure == False:
				return

		if self._start_tick is not None:

			ticks = pigpio.tickDiff(self._last_tick, tick)
			self._last_tick = tick

			if self._last_level == level:
				self.wrong_level_count += 1
				return
			else:
				self._last_level = level

			if level == 0: # Falling edge.                
				self._high_ticks += ticks
			elif level == 1: # Rising edge.
				self._low_ticks += ticks
			else: # timeout level, not used
				pass

		else:
			self._start_tick = tick
			self._last_tick = tick
			self._last_level = level
			self.wrong_level_count = 0



if __name__ == "__main__":

	from datetime import datetime
	import time
	import pigpio
	import ds # import this script
	import sys

	pi = pigpio.pi('localhost')
	s25 = ds.sensor(pi, 4)
	#s10 = pidustsensor.sensor(pi, 17)

	while True:

		s25.on_measure = True
		time.sleep(30)	
		s25.on_measure = False

		timestamp = datetime.now()
		g25, r25, c25, wroing_level_count = s25.read()
		s25.wrong_level_count = 0
		PM25count = c25

		if PM25count < 0:    # If PM25count is less than Zero (Negative Value) set PM25 Count to Zero
			PM25count = 0

		if PM25count == 1114000.62:   #If PM25count gets error value set to zero
			PM25count = 0


		density = 1.65 * math.pow(10, 12)
		rpm25 = 0.44 * math.pow(10, -6)
		volpm25 = (4/3) * math.pi * (rpm25**3)
		masspm25 = density * volpm25
		concentration_ugm3_pm25 = PM25count * 3531.5 * masspm25

		cbreakpointspm25 = [ [0.0, 12, 0, 50],\
			   [12.1, 35.4, 51, 100],\
			   [35.5, 55.4, 101, 150],\
			   [55.5, 150.4, 151, 200],\
			   [150.5, 250.4, 201, 300],\
			   [250.5, 350.4, 301, 400],\
			   [350.5, 500.4, 401, 500], ]

		C = concentration_ugm3_pm25

		if C > 500.4:
			aqiPM25 = 500

		else:
			for breakpoint in cbreakpointspm25:
				if breakpoint[0] <= C <= breakpoint[1]:
					Clow25 = breakpoint[0]
					Chigh25 = breakpoint[1]
					Ilow25 = breakpoint[2]
					Ihigh25 = breakpoint[3]
					aqiPM25 = (((Ihigh25-Ilow25)/(Chigh25-Clow25))*(C-Clow25))+Ilow25     

		aqdata = timestamp, r25, int(c25), int(PM25count), int(concentration_ugm3_pm25), int(aqiPM25)
		print("time: {}, PM2.5: Ratio = {:.1f}, PM > 2.5 µg PCS Conc = {} µg/ft3, PM25count: {} µg/ft3, Metric Conc of PM25count = {} µg/m3, PM2.5 AQI: {}, wrong_int: {}". 
			format(timestamp, r25, int(c25), int(PM25count), int(concentration_ugm3_pm25), int(aqiPM25), wroing_level_count))

# Print

	pi.stop() # Disconnect from Pi.

