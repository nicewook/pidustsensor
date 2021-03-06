#!/usr/bin/env python

# pidustsensor_v3.py

# Derived from PPD42NS.py (2015-11-22 Public Domain) Original Script located at http://abyz.co.uk/rpi/pigpio/examples.html
# Adaptions from https://github.com/andy-pi/weather-monitor/blob/master/air_quality.py

# Reference Information on Sensor
# http://www.shinyei.co.jp/stc/eng/optical/main_ppd42.html
# Detectable Particle Size: Over 1.0µm, Sensor uses the counting method not weight\
# Units are measured in pcs/L or pcs/0.01cf
#
# http://lantaukwcounter.blogspot.com/2015/10/pdd42-sensor-can-it-measure-pm10-and.html
# P1 for particles > 1 micron, P2 for particles > 2.5 micron
# Based on this it might be possible to capture AQI for PM2.5 but not AQI for PM10
# The script references PM10 but it appears the actual measure is particles greater than 1 micron
#
# https://www.engineeringtoolbox.com/particle-sizes-d_934.html
# one micron is one-millionth of a metre
# 1 micron = 10-6 m
# 1 micron = 1000 nano metre
# Airborne particles
# Airborne particles are solids suspended in the air.

# Larger particles - larger then 100 μm
# terminal velocities > 0.5 m/s
# fall out quickly
# includes hail, snow, insect debris, room dust, soot aggregates, coarse sand, gravel, and sea spray

# Medium-size particles - in the range 1 to 100 μm
# sedimentation velocities greater than 0.2 m/s
# settles out slowly
# includes fine ice crystals, pollen, hair, large bacteria, windblown dust, fly ash, coal dust, silt, fine sand, and small dust

# Small particles - less than 1 μm
# falls slowly, take days to years to settle out of a quiet atmosphere. In a turbulent atmosphere they may never settle out
# can be washed out by water or rain
# includes viruses, small bacteria, metallurgical fumes, soot, oil smoke, tobacco smoke, clay, and fumes


######
# The micrometre (International spelling as used by the International Bureau of Weights and Measures;
# SI symbol: μm) or micrometer (American spelling), also commonly known as a micron, 
# is an SI derived unit of length equaling 1×10−6 metre (SI standard prefix "micro-" = 10−6); 
# that is, one millionth of a metre (or one thousandth of a millimetre, 0.001 mm, or about 0.000039 inch).

###### Particle Size Discrimination by PPD42NJ (January 29th, 2013)
# https://i.publiclab.org/system/images/photos/000/010/160/original/Size_Discrimination%28PPD42NJ%29.pdf
#
# Discrimination of particle size can be done using a special method with our Particle Sensor, Model
# PPD42NJ.
#
# PPD42NJ has dual pulse output which works as follows;
# 1) Receptor receives scattered light from the particle, as a pulse.
# 2) Each raw pulse is amplified by an op-amp so that pulse can be acknowledged clearly.
# 3) PPD42NJ has 2 fixed threshold; voltage = 1V for P1 and voltage = 2.5V for P2.
# The threshold represents detecting size of particles, (approx) 1 micron or larger, and (approx.)2.5
# micron or larger sized particles respectively.
# 
# With PPD42NJ you can read each selected pulse, selected with 2 threshold detection voltage 1V and
# 2.5V which was converted to Lo Pulse directly at the same time.
#
# PPD42NJ also has a port enabling the user to set the alternative threshold detection voltage directly.
# (In other words, a threshold detection voltage 2.5V will be replaced with your designated alternative
# voltage.)

# As you may understand from above 3), you can have 2 different minimum size particles which will
# generate a pulse.
#
# For example:
# Particle sizes of cigarette smoke range from 0.01 micron to around 1micron.
# Particle sizes of house dust range from 1 micron to around 10 micron.
# 
# When you use 1V threshold (when you read Lo Pulse output at P1,) PPD42NJ detects particles
# larger than (approx.) 1 micron.
# 
# When you use 2.5V threshold (when you read Lo Pulse output at P2,) PPD42NJ detects partic#les
# larger than (apporx.) 2.5 micron.
#
# Over 1 micron sized particles represents cigarette smoke and house dust.
#
# Over 2.5 micron sized particles represents house dust only, because this is over the size range of
# cigarette smoke particles
#
# When you use our PPD42NJ to check unidentified particles in the room, you check the Lo Pulse
# occupancy time (ratio) over a certain unit time at both P1 and P2.
#
# By simple math you can then determine how much of which range of particle sizes there are.
#
# Pattern A
# 1V threshold Lo pulse output occupancy ratio : high
# 2.5V threshold Lo pulse output occupancy ratio : low or none
# means you have cigarette smoke at that period.
#
# Pattern B
# 1V threshold Lo pulse output occupancy ratio : high -- (a)
# 2.5V threshold Lo pulse output occupancy ratio : high --(b)
# (a) - k*(b) nearly equal 0(zero)
# means you have house dust at that period
#
# Pattern C
# 1V threshold Lo pulse output occupancy ratio : high -- (a)
# 2.5V threshold Lo pulse output occupancy ratio : high --(b)
# (a) - k*(b) still rather high
# means you have cigarette smoke and house dust at the same time at that period
	
####### Instructions ########################
# On the Raspbery Pi make sure to install pigpio using Apt
# $ sudo apt-get install pigpio python-pigpio python3-pigpio
#
# Once installed make sure to run the pidpio daemon before
# running this script
#
# $ sudo pigpiod
# $ python pidustsensor.py
# or
# $ python3 pidustsensor.py
#
# Other packages to install for storing the data and presenting graph data
# $ sudo apt-get install python python3 python3-matplotlib python-matplotlib python3-flask python-flask python3-numpy python-numpy nano git lighttpd sqlite3 sqlite3-dev

####### Wiring Options ######################
# +-----------------------------------------+
#  |                                         |
#  |  Shinyei PPD42NS  / Grove Dust Sensor   |
#  |  (Sensor components facing you          |           
#  |                                         |
#  |    |+|        |+|                       |          
#  |    SL2 POT    CN1 POT                   |
#  +-----------------------------------------+
#  |    Pin Number                           |
#  |                                         |          
#  |     |     |     |     |     |           |
#  |     5     4     3     2     1           |       
#  |     |     |     |     |     |           |
#  +-----------------------------------------+
#        |     |     |     |     | 
#        |     |     |     |  GND (Black)
#        |     |     |     |     | 
#        |     |  5V (Red) |     | 
#        |     |     |     |     | 
#        |   PM2.5   |     |     |
#        |     |     |     |     | 
#        |     |     |   PM1.0   |
#        |     |     |     |     |
#   Threshold  |     |     |     |
#   for Pin 2  |     |     |     | 
#        |     |     |     |     | 
#        |     |     |     |     | 
#
# CN : S5B-EH(JST)
# 1 : COMMON(GND) [Black Wire on Grove Sensor]
# 2 : OUTPUT(P2) [Not used on Grove Connectr] [Can be used for PM1.0]
# 3 : INPUT(5VDC 90mA) [Red Wire on Grove Sensor]
# 4 : OUTPUT(P1) [Yellow Wire on Grove Sensor] [Used for PM2.5 mesurements]
# 5 : INPUT(T1)･･･FOR THRESHOLD FOR [P2] [Not used on Grove Connector]
#############################################



# Using a Bi-Directional Logic Level Converter
#  +-----------------------------------------+
#  |                                         |
#  |  Shinyei PPD42  / Grove Dust Sensor     |
#  |  (Sensor facing you)                    |           
#  |                                         |
# |    |+|        |+|                       |          
#  |    SL2 POT    CN1 POT                   |
#  +-----------------------------------------+
#  |    Pin Number                           |
#  |                                         |          
#  |     |     |     |     |     |           |
#  |     5     4     3     2     1           |       
#  |     |     |     |     |     |           |
#  +-----------------------------------------+
#        |     |     |     |     | 
#        |     |     |     |  GND (Black)
#        |     |     |     |     | 
#        |     |  5V (Red) |     | 
#        |     |     |     |     | 
#        |   PM2.5   |     |     |
#        |     |     |     |     |                 +-----------------------+
#        |     |     |   PM1.0   |                 |Bi-Direction Logic     |
#        |     |     |     |     |                 |Level Converter        |
#        |     |     |     |     |                 +-----------------------+
#   Threshold  |     |     |     +--(1) GND--------|  GND              GND |----[[RPi GND Pin]]
#   for Pin 2  |     |     |                       |                       |
#        |     |     |     +-----(2) PM1.0---------|  B1               A1  |----[[RPi GPIO Pin]]
#        |     |     |                             |                       |
#        |     |     +-----------(3) 5V------+-----|  HV               LV  |----[[RPi 3.3V Pin]]
#        |     |                             |     |                       |
#        |     |                             |     |                       |
#        |     |             [[RPi 5V Pin]]--+     |                       |
#        |     |                                   |                       |
#        |     +-----------------(4) PM2.5---------|  B2               A2  |----[[RPi GPIO Pin]]
#        |                                         +-----------------------+
#        |
#   [[Not used]]
#
#
#############################################


# Using a Voltage Divider (At your own risk)
#
#  +-----------------------------------------+
#  |                                         |
#  |  Shinyei PPD42  / Grove Dust Sensor     |
#  |  (Sensor facing you)                    |           
#  |                                         |
#  |    |+|        |+|                       |          
#  |    SL2 POT    CN1 POT                   |
#  +-----------------------------------------+
#  |    Pin Number                           |
#  |                                         |          
#  |     |     |     |     |     |           |
#  |     5     4     3     2     1           |       
#  |     |     |     |     |     |           |
#  +-----------------------------------------+
#        |     |     |     |     | 
#        |     |     |     |  GND (Black)
#        |     |     |     |     | 
#        |     |  5V (Red) |     | 
#        |     |     |     |     | 
#        |   PM2.5   |     |     |
#        |     |     |     |     | 
#        |     |     |   PM1.0   |
#        |     |     |     |     |     1 kΩ        1 kΩ resistor
#   Threshold  |     |     |     +----[_____]-----[_____]------+--------> [[Pi GND Pin]]
#   for Pin 2  |     |     |                                   |
#        |     |     |     |                  1 kΩ resistor    |
#        |     |     |     +----------------[_____]------------+--------> [[Pi GPIO Pin 7]]
#        |     |     |                                         |
#        |     |     +-----------------> [[Pi 5V Pin]]         |
#        |     |                                               |
#        |     |                              1 kΩ resistor    |
#        |     +----------------------------[_____]------------+--------> [[Pi GPIO Pin 8]]
#        |
#        |
#   [[Not used]]
#
#
#############################################

from __future__ import print_function
import math
import pigpio
# also import writer for writing CSV logs
from csv import writer

class sensor:
    """
    A class to read a Shinyei PPD42NS Dust Sensor, e.g. as used
    in the Grove dust sensor.
    
    This code calculates the percentage of low pulse time and
    calibrated concentration in particles per 1/100th of a cubic
    foot at user chosen intervals.
    
    You need to use a voltage divider to cut the sensor output
    voltage to a Pi safe 3.3V (alternatively use an in-line
    20k resistor to limit the current at your own risk).
    """

    def __init__(self, pi, gpio):
        """
        Instantiate with the Pi and gpio to which the sensor
        is connected.
        """
        
        self.pi = pi
        self.gpio = gpio
        
        self._start_tick = None
        self._last_tick = None
        self._low_ticks = 0
        self._high_ticks = 0

        pi.set_mode(gpio, pigpio.INPUT)

        self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    # Method for calculating Ratio and Concentration
    def read(self):
        """
        Calculates the percentage low pulse time and calibrated
        concentration in particles per 1/100th of a cubic foot
        since the last read.

        For proper calibration readings should be made over
        30 second intervals.
        
        Returns a tuple of gpio, percentage, and concentration.
        """
        interval = self._low_ticks + self._high_ticks

        if interval > 0:
            ratio = float(self._low_ticks)/float(interval)*100.0
            conc = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62;
        else:
            ratio = 0
            conc = 0.0

        self._start_tick = None
        self._last_tick = None
        self._low_ticks = 0
        self._high_ticks = 0

        return (self.gpio, ratio, conc)

    def _cbf(self, gpio, level, tick):

        if self._start_tick is not None:

            ticks = pigpio.tickDiff(self._last_tick, tick)

            self._last_tick = tick

            if level == 0: # Falling edge.
                self._high_ticks = self._high_ticks + ticks

            elif level == 1: # Rising edge.
                self._low_ticks = self._low_ticks + ticks

            else: # timeout level, not used
                pass

        else:
            self._start_tick = tick
            self._last_tick = tick
         


if __name__ == "__main__":

    from datetime import datetime
    import time
    import pigpio
    import pidustsensor_v3 # import this script

    pi = pigpio.pi('localhost') # Connect to a remote pi or 'localhost'

    # Select the pi GPIO pin that is connected to the sensor
    # For PM2.5 Readings, connected to Pin 4 of the Sensor
    # Make sure to use the Broadcom GPIO Pin number
    s25 = pidustsensor_v3.sensor(pi, 8)

    # Select the pi GPIO pin that is connected to the sensor
    # For PM10 Readings, connected to Pin 2 of the Sensor
    # Make sure to use the Broadcom GPIO Pin number
    s10 = pidustsensor_v3.sensor(pi, 7)
    
   
    # Option to prompt for filename:
    ##logfilename = input("Please enter a name for the logfile.") 
    ##with open(logfilename + '.csv', 'w', newline='') as f:

    # Create a specific and static csv log file
    with open('airqualitylog.csv', 'w', newline='') as f:
    # Remove the above line if you want to use the prompt for logfile name function
		
        data_writer = writer(f)
        #write header for csv log file
        data_writer.writerow(['Date Time Stamp', 'Ratio for PM2.5', 'PM2.5 Concentration (PCS  per 0.01 cubic foot)', 'Concentration Count for 2.5 PM', 'PM2.5 Concentration (PCS per cubic metre)', 'US AQI for PM2.5 (Should be average of a 24h reading)', 'Ratio for PM10', 'PM10 Concentration (PCS  per 0.01 cubic foot)', 'Concentration Count for 10 PM', 'PM10 Concentration (PCS per cubic metre)', 'US AQI for PM10 (Should be average of a 24h reading)'])
        
        while True:
        
            time.sleep(30) # Use 30 for a properly calibrated reading.

            # Get the current time of the reading
            timestamp = datetime.now()
            
            # Read the PM2.5 values from the sensor
            # get the gpio, ratio and concentration in particles / 0.01 ft3
            g25, r25, c25 = s25.read()

            # do some checks on the concentration reading and print errors
            if (c25 == 1114000.62):
                print("PM2.5 Concentration Error\n")
                continue
	  
            if c25 < 0:
                raise ValueError('Concentration cannot be a negative number')


            # Read the PM10 values from the sensor
            # get the gpio, ratio and concentration in particles / 0.01 ft3
            g10, r10, c10 = s10.read()
            
            # do some checks on the concentration reading and print errors
            if (c10 == 1114000.62):
                print("PM10 Concentration Error\n")
                continue
	  
            if c10 < 0:
                raise ValueError('Concentration cannot be a negative number')


            # Special Calculations for differentiating between two particulate sizes
            # Note: Not sure why P10 calculation is subtracted from PM2.5
            # Maybe hreshold input (IN1) is left unsed, but it will be used later as a way to
            # split particule by size, and hence detect both PM10 and PM2.5 particules.
            PM10count = c10         # Not sure if this should be c10 only
            PM25count = c25         # Not sure if c25 - c10 is required instead


            # Convert conentrations to µg/ metre cubed
            # Convert concentration of PM2.5 and PM10 particles per 0.01 cubic feet to µg/ metre cubed
            # this method outlined by Drexel University students (2009) and is an approximation
            # does not contain correction factors for humidity and rain
      
            # Assume all particles are spherical, with a density of 1.65E12 µg/m3
            density = 1.65 * math.pow(10, 12)
        
            # PM2.5 Values
            # Assume the radius of a particle in the PM2.5 channel is .44 µm
            rpm25 = 0.44 * math.pow(10, -6)
        
            # Volume of a PM2.5 sphere = 4/3 * pi * radius^3
            volpm25 = (4/3) * math.pi * (rpm25**3)
        
            # mass = density * volume
            masspm25 = density * volpm25
        
            # parts/m3 =  parts/foot3 * 3531.5
            # µg/m3 = parts/m3 * mass in µg
            concentration_ugm3_pm25 = PM25count * 3531.5 * masspm25 # or use c25 instead of PM25count


            # PM10 Values
            # Assume the radius of a particle in the PM10 channel is 2.6 µm
            rpm10 = 2.6 * math.pow(10, -6)
        
            # Volume of a PM10 sphere = 4/3 * pi * radius^3
            volpm10 = (4/3) * math.pi * (rpm10**3)
        
            # mass = density * volume
            masspm10 = density * volpm10
        
            # parts/m3 =  parts/foot3 * 3531.5
            # µg/m3 = parts/m3 * mass in µg
            concentration_ugm3_pm10 = PM10count * 3531.5 * masspm10 # Or use c10 instead of PM10count



      
            # Convert concentration of PM2.5 particles in µg/ metre cubed to the USA 
            # Environment Agency Air Quality Index - AQI
            # https://en.wikipedia.org/wiki/Air_quality_index
            # Computing_the_AQI
            # https://github.com/intel-iot-devkit/upm/pull/409/commits/ad31559281bb5522511b26309a1ee73cd1fe208a?diff=split
            # input should be 24 hour average of ugm3, not instantaneous reading
      
        
            cbreakpointspm25 = [ [0.0, 12, 0, 50],\
                            [12.1, 35.4, 51, 100],\
                            [35.5, 55.4, 101, 150],\
                            [55.5, 150.4, 151, 200],\
                            [150.5, 250.4, 201, 300],\
                            [250.5, 350.4, 301, 400],\
                            [350.5, 500.4, 401, 500], ]
                        
            C = concentration_ugm3_pm25
        
            if C > 500.4:
                aqi25 = 500

            else:
                for breakpoint in cbreakpointspm25:
                    if breakpoint[0] <= C <= breakpoint[1]:
                        Clow25 = breakpoint[0]
                        Chigh25 = breakpoint[1]
                        Ilow25 = breakpoint[2]
                        Ihigh25 = breakpoint[3]
                        aqi25 = (((Ihigh25-Ilow25)/(Chigh25-Clow25))*(C-Clow25))+Ilow25


      
            # Convert concentration of PM10 particles in µg/ metre cubed to the USA 
            # Environment Agency Air Quality Index - AQI
            # https://en.wikipedia.org/wiki/Air_quality_index
            # Computing_the_AQI
            # https://github.com/intel-iot-devkit/upm/pull/409/commits/ad31559281bb5522511b26309a1ee73cd1fe208a?diff=split
            # input should be 24 hour average of ugm3, not instantaneous reading
      
        
            cbreakpointspm10 = [ [0, 54, 0, 50],\
                            [55, 154, 51, 100],\
                            [155, 254, 101, 150],\
                            [255, 354, 151, 200],\
                            [355, 424, 201, 300],\
                            [425, 504, 301, 400],\
                            [505, 604, 401, 500], ]
                        
            D = concentration_ugm3_pm10
        
            if D > 604:
                aqi10 = 500

            else:
                for breakpoint in cbreakpointspm10:
                    if breakpoint[0] <= D <= breakpoint[1]:
                        Clow10 = breakpoint[0]
                        Chigh10 = breakpoint[1]
                        Ilow10 = breakpoint[2]
                        Ihigh10 = breakpoint[3]
                        aqi10 = (((Ihigh10-Ilow10)/(Chigh10-Clow10))*(D-Clow10))+Ilow10
      

         
            # Store values in a variable
            aqdata = timestamp, r25, int(c25), int(PM25count), int(concentration_ugm3_pm25), int(aqi25), r10, int(c10), int(PM10count), int(concentration_ugm3_pm10), int(aqi10)
         
            # Store values in CSV log file
            data_writer.writerow(aqdata) 
         
            # Print values to console
            print("Timestamp of Readings = {} \n PM2.5:  Ratio = {:.1f}, Conc = {} µg/ft3, PM25count = {} µg/ft3, Metric Conc = {} µg/m3, PM2.5 AQI = {} \n PM10:   Ratio = {:.1f}, Conc = {} µg/ft3, PM10count = {} µg/ft3, Metric Conc = {} µg/m3, PM10 AQI = {} \n " .
                format(timestamp, r25, int(c25), int(PM25count), int(concentration_ugm3_pm25), int(aqi25), r10, int(c10), int(PM10count), int(concentration_ugm3_pm10), int(aqi10)))
         
            # Print
            
        pi.stop() # Disconnect from Pi.

# Example of values collected
# PM2.5  Ratio = 13.7 Conc = 9245 PM25count = 9245 µg/m3 = 19 PM2.5 AQI = 65
# PM10   Ratio = 4.2 Conc = 2179 PM10count = 2179 µg/m3 = 935 PM10 AQI = 500
#
# PM2.5  Ratio = 5.1 Conc = 2685 PM25count = 2685 µg/m3 = 5 PM2.5 AQI = 23
# PM10   Ratio = 5.6 Conc = 2982 PM10count = 2982 µg/m3 = 1279 PM10 AQI = 500
