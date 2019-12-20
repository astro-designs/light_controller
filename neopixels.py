
# neopixels.py
# Kitchen lights controller
# By Mark Cantrill (mark@astro-designs.com)
# Originally based on NeoPixel library strandtest example by Tony DiCola
# Direct port of the Arduino NeoPixel library strandtest example.

# Plus & Minus buttons change the level of brightness on some patterns
# Mode button allows some rudimentary control over the strand 'pattern'
# Hold the Mode button while pressing Plus or Minus to change the pattern

import RPi.GPIO as GPIO
import sys
import time
import datetime
from random import randint
from rpi_ws281x import __version__ as __rpi_ws281x__, PixelStrip, Color
from array import *
import urllib2
import json


# LED strip configuration:
LED_COUNT      = 189     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define the GPIO channels used for the three control buttons
pinButtonMinus = 17 # Minus / - / Down : Controls the brightness
pinButtonPlus = 27  # Plus / + / UP    : Controls the brightness
pinButtonMode = 22  # Mode             : Controls the lighting mode

# Define the GPIO channel used to illuminate the LED
pinLED = 4			# Usually flashes when the buttons are being scanned

#Define the GPIO channel used to interrupt / kill the program
pinEXTCTRL = 23

while GPIO.gpio_function(LED_PIN) == GPIO.HARD_PWM:
	print ("Waiting for PWM pin to be released...")
	time.sleep(1)

# Configure the initial configuration
global brighness, LightingMode, UpdateRequired, red, green, blue
LED_state = True
brightness = 50
LightingMode = 12 #Initial mode
UpdateRequired = True
red = 255
green = 255
blue = 255
ReverseStrip = False

# Lookup LightingMode names...
ModeLookup = ["White", "Candle", "Tungsten", "Halogen", "Overcast", "ClearBlueSky",
              "Yellow", "Cyan", "Green", "Magenta", "Blue", "Red",
              "Cylon", "KnightRider", "TwinkleColours",
              "TheaterChaseRainbow", "RainbowCycle", "CheerLights", "Pacman",
              "TheaterChaseWhite", "TheaterChaseRed", "TheaterChaseBlue",
              "Rainbow", "RainbowCycle", "TheaterChaseRainbow", "TwinkleCOlours with CountDown"]           

# Configure the GPIO functions
GPIO.setup(pinButtonMode, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pinButtonPlus, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pinButtonMinus, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pinLED, GPIO.OUT)

# Illuminate the LED...
GPIO.output(pinLED, LED_state)

# Cheerlights stuff...
urlRoot = "http://api.thingspeak.com/channels/1417/"
namesToRGB = {'red':        Color(255,  0,  0),
    		'green':        Color(  0,128,  0),
    		'blue':         Color(  0,  0,255),
    		'cyan':         Color(  0,255,255),
    		'white':        Color(255,255,255),
    		'warmwhite':    Color(253,245,230),
    		'grey':         Color(128,128,128),
    		'purple':       Color(128,  0,128),
    		'magenta':      Color(255,  0,255),
    		'yellow':       Color(255,255,  0),
    		'orange':       Color(255,165,  0),
    		'pink':         Color(255,192,203),
    		'candle':       Color(255,147, 41),
    		'tungsten':     Color(255,214,170),
    		'halogen':      Color(255,241,224),
    		'overcast':     Color(201,226,255),
    		'clearbluesky': Color( 64,156,255),
    		'oldlace':      Color(253,245,230)}

#retrieve and load the JSON data into a JSON object
def getJSON(url):
    jsonFeed = urllib2.urlopen(urlRoot + url)
    feedData = jsonFeed.read()
    #print feedData
    jsonFeed.close()

    data = json.loads(feedData)
    return data

#use the JSON object to identify the colour in use,
#update the last entry_id processed
def parseColour(feedItem):
    global lastID
    global pixels
    #print feed["created_at"], feed["field1"]
    for name in namesToRGB.keys():
        if feedItem["field1"] == name:
            print name
            color = namesToRGB[name]
            print color
            for i in range(strip.numPixels()):
                strip.setPixelColor(i,color)

    lastID = getEntryID(feedItem)

#read the last entry_id
def getEntryID(feedItem):
    return int(feedItem["entry_id"])            

# Define a function to check for the mode pin to be set
# and to check if the EXTCTRL pin has been set to something other than '1'
def checkModeExt():
	global LightingMode, brightness, UpdateRequired
	mode_sts = False
	if GPIO.gpio_function(pinEXTCTRL) == 0:
		mode_sts = True
		#GPIO.setup(LED_PIN, GPIO.IN)
		GPIO.setup(pinEXTCTRL, GPIO.IN)
		#GPIO.cleanup()
		#sys.exit(130)
	else:
		if GPIO.input(pinButtonMode):
			if GPIO.input(pinButtonMinus):
				if LightingMode > 0:
					mode_sts = True
					LightingMode = LightingMode - 1
					UpdateRequired = True
					print("LightingMode: ", LightingMode)
					time.sleep(0.25)
				
			elif GPIO.input(pinButtonPlus):
				if LightingMode < 23:
					mode_sts = True
					LightingMode = LightingMode + 1
					UpdateRequired = True
					print("LightingMode: ", LightingMode)
					time.sleep(0.25)			
			
		else:
			if GPIO.input(pinButtonPlus) == True:
				if brightness < 100:
					brightness = brightness + 10
					UpdateRequired = True
				else: brightness = 100
				#print ("Brightness = ", brightness)
				time.sleep(1)
		
			if GPIO.input(pinButtonMinus) == True:
				if brightness > 0:
					brightness = brightness - 10
					UpdateRequired = True
				else: brightness = 0
				#print ("Brightness = ", brightness)
				time.sleep(1)
        
	return (mode_sts)

# Define a function to control the brightness
def setBrightness(red_100, green_100, blue_100, brightness = 100):
	global red, green, blue
	red = int(red_100 * (brightness / 100.0))
	green = int(green_100 * (brightness / 100.0))
	blue = int(blue_100 * (brightness / 100.0))
	if red > 255: red = 255
	if green > 255: green = 255
	if blue > 255: blue = 255
	#print ("Adjusting RGB to: ", red, green, blue)

# Define a function to set the lighting mode to 'All Off'
def allBlack(strip, wait_ms=50):
	"""Fill strip with black"""
	color = Color(0,0,0)
	print ('Colour (R, G, B): ', color)
	for i in range(strip.numPixels()):
		strip.setPixelColor(i,color)
		strip.show()
		time.sleep(wait_ms/1000.0)

# Define a function to set the lighting mode to 'All White'
# Note at maximum brightness, these LEDs can draw a lot from the PSU so
# make sure your PSU is up to delivering a few Amps! 100 LEDs can take a good 4Amps!
def allWhite(strip, wait_ms=50):
	"""Fill strip with white"""
	#color = Color(255,255,255)
	color = namesToRGB['white']
	for i in range(strip.numPixels()):
		strip.setPixelColor(i,color)
		strip.show()
		time.sleep(wait_ms/1000.0)

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

# Define a lighting mode to move a red spot left, right, left, right...
# Don't know what a Cylon is? You're not old enough! Look it up... :o)
# Inspired by a TV show from the 80's...
# Alternatively, call it Tennis mode
def cylon(strip, wait_ms=50):
	print "The Cylons are here!"
	dir = 1
	i = 10
	i1 = 9
	i2 = 8
	i3 = 7
	i4 = 6
	i5 = 5
	i6 = 4
	i7 = 3
	i8 = 2
	i9 = 1
	
	#while GPIO.input(pinButtonMode) == 0:
	while checkModeExt() == False:
		strip.setPixelColor(i,  Color(16,16,16))
		strip.setPixelColor(i1, Color(0,32,0))
		strip.setPixelColor(i2, Color(0,64,0))
		strip.setPixelColor(i3, Color(0,200,0))
		strip.setPixelColor(i4, Color(0,255,0))
		strip.setPixelColor(i5, Color(0,255,0))
		strip.setPixelColor(i6, Color(0,200,0))
		strip.setPixelColor(i7, Color(0,64,0))
		strip.setPixelColor(i8, Color(0,32,0))
		strip.setPixelColor(i9, Color(16,16,16))
		strip.show()
		
		i9 = i8
		i8 = i7
		i7 = i6
		i6 = i5
		i5 = i4
		i4 = i3
		i3 = i2
		i2 = i1
		i1 = i
		
		if i == 1:
			dir = 1
			i+=1
		elif i == strip.numPixels()-1:
			dir = 0
			i-=1
		elif dir == 1:
			i+=1
		else:
			i-=1
		
		time.sleep(wait_ms/1000.0)
	time.sleep(1)

# Define a lighting mode inspired by another popular TV show from the 80's	
def kitt(strip, wait_ms=50):
	print "Hello, I'm the Knight Industries Two-Thousand!"
	dir = 1
	i   = 30
	i1  = 29
	i2  = 28
	i3  = 27
	i4  = 26
	i5  = 25
	i6  = 24
	i7  = 23
	i8  = 22
	i9  = 21
	i10 = 20
	i11 = 19
	i12 = 18
	i13 = 17
	i14 = 16
	i15 = 15
	i16 = 14
	i17 = 13
	i18 = 12
	i19 = 11
	i20 = 10
	i21 = 9
	i22 = 8
	i23 = 7
	i24 = 6
	i25 = 5
	i26 = 4
	i27 = 3
	i28 = 2
	i29 = 1
	
	#while GPIO.input(pinButtonMode) == 0:
	while checkModeExt() == False:
		strip.setPixelColor(i,   Color(255,0,0))
		strip.setPixelColor(i1,  Color(255,0,0))
		strip.setPixelColor(i2,  Color(255,0,0))
		strip.setPixelColor(i3,  Color(255,0,0))
		strip.setPixelColor(i4,  Color(200,0,0))
		strip.setPixelColor(i5,  Color(200,0,0))
		strip.setPixelColor(i6,  Color(200,0,0))
		strip.setPixelColor(i7,  Color(150,0,0))
		strip.setPixelColor(i8,  Color(150,0,0))
		strip.setPixelColor(i9,  Color(150,0,0))
		strip.setPixelColor(i10, Color(100,0,0))
		strip.setPixelColor(i11, Color(100,0,0))
		strip.setPixelColor(i12, Color(100,0,0))
		strip.setPixelColor(i13, Color(50,0,0))
		strip.setPixelColor(i14, Color(50,0,0))
		strip.setPixelColor(i15, Color(50,0,0))
		strip.setPixelColor(i16, Color(50,0,0))
		strip.setPixelColor(i17, Color(25,0,0))
		strip.setPixelColor(i18, Color(25,0,0))
		strip.setPixelColor(i19, Color(25,0,0))
		strip.setPixelColor(i20, Color(25,0,0))
		strip.setPixelColor(i21, Color(12,0,0))
		strip.setPixelColor(i22, Color(12,0,0))
		strip.setPixelColor(i23, Color(12,0,0))
		strip.setPixelColor(i24, Color(12,0,0))
		strip.setPixelColor(i25, Color(6,0,0))
		strip.setPixelColor(i26, Color(6,0,0))
		strip.setPixelColor(i27, Color(6,0,0))
		strip.setPixelColor(i28, Color(6,0,0))
		strip.setPixelColor(i29, Color(0,0,0))
		strip.show()
		
		i29 = i28
		i28 = i27
		i27 = i26
		i26 = i25
		i25 = i24
		i24 = i23
		i23 = i22
		i22 = i21
		i21 = i20
		i20 = i19
		i19 = i18
		i18 = i17
		i17 = i16
		i16 = i15
		i15 = i14
		i14 = i13
		i13 = i12
		i12 = i11
		i11 = i10
		i10 = i9
		i9  = i8
		i8  = i7
		i7  = i6
		i6  = i5
		i5  = i4
		i4  = i3
		i3  = i2
		i2  = i1
		i1  = i
		
		if i == 1:
			dir = 1
			i+=1
		elif i == strip.numPixels()-1:
			dir = 0
			i-=1
		elif dir == 1:
			i+=1
		else:
			i-=1
		
		time.sleep((200 / strip.numPixels()) * wait_ms/1000.0)
	time.sleep(1)
	
# Define a lighting mode inspired by a popular computer game from... you guessed it, the 80's!
def pacman(strip, wait_ms=50):

	print "Pacman!"
	
	food_pos = []
	# Initial positions...
	pacman_pos = 1 # randint(1,10)
	pacman_dir = 1 #left to right
	redghost_pos = -90 + randint(0,19)
	redghost2_pos = -115 + randint(0,9)
	redghost3_pos = -125 + randint(0,9)
	ghost_dir = 1 #left to right
	blueghost_pos = -1000
	blueghost2_pos = -1020
	blueghost3_pos = -1030
	star_pos = 140 + randint(0,6)*5
	for i in range(0, strip.numPixels()):
		food_pos.append(1)
	for i in range(0, strip.numPixels()):
		if i % 5 == 0:
			food_pos[i] = 1
		else:
			food_pos[i] = 0
	
	# The board components...
	pacman = 1
	redghost = 2
	blueghost = 3
	food = 4
	star = 5
	pactime = 4
	
	# Wait for the Mode button to be pressed
	#while GPIO.input(pinButtonMode) == 0:
	while checkModeExt() == False:
		# Timer...
		if pactime > 0:
			pactime = pactime - 1
		else:
			pactime = 699

		#print("Star pos: ", star_pos)
		#print randint(0,6)
		#print("Red Ghost #1 pos: ", redghost_pos)
		#print("Red Ghost #2 pos: ", redghost2_pos)
		#print("Red Ghost #3 pos: ", redghost3_pos)
		
		# display board...
		for i in range(0, strip.numPixels()):
			if i == redghost_pos or i-1 == redghost_pos or i+1 == redghost_pos:
				color = Color(255, 0, 0) # red
			elif i == redghost2_pos or i-1 == redghost2_pos or i+1 == redghost2_pos:
				color = Color(255, 0, 0) # red
			elif i == redghost3_pos or i-1 == redghost3_pos or i+1 == redghost3_pos:
				color = Color(255, 0, 0) # red
			elif i == pacman_pos or i-1 == pacman_pos or i+1 == pacman_pos:
				color = Color(255, 255, 0) # yellow
			elif i == blueghost_pos or i-1 == blueghost_pos or i+1 == blueghost_pos:
				color = Color(0, 0, 255) # blue
			elif i == blueghost2_pos or i-1 == blueghost2_pos or i+1 == blueghost2_pos:
				color = Color(0, 0, 255) # blue
			elif i == blueghost3_pos or i-1 == blueghost3_pos or i+1 == blueghost3_pos:
				color = Color(0, 0, 255) # blue
			elif i == star_pos:
				color = Color(255, 255, 255) # Bright white
			elif food_pos[i] == 1:
				color = Color(12, 12, 12) # white
			else:
				color = Color(0, 0, 0) # black

			strip.setPixelColor(i, color)
		
		strip.show()
		
		# Move
		if pactime % 3 == 0:
			# If out of range, head back into range...
			if pacman_dir < 0:
				pacman_dir = 1
			elif pacman_dir > strip.numPixels()-1:
				pacman_dir = 0
				
			# Just move back & forward between end points
			if pacman_dir == 1:
				if pacman_pos < strip.numPixels()-1:
					pacman_pos = pacman_pos + 1
				else:
					pacman_dir = 0
			else:
				if pacman_pos > 0:
					pacman_pos = pacman_pos - 1
				else:
					pacman_dir = 1

		# Red ghost runs towards pacman
		# slightly faster than pacman
		if pactime % 2 == 0:
			if redghost_pos < pacman_pos:
				redghost_pos = redghost_pos + 1
			else:
				redghost_pos = redghost_pos - 1

			if redghost2_pos < pacman_pos:
				redghost2_pos = redghost2_pos + 1
			else:
				redghost2_pos = redghost2_pos - 1

			if redghost3_pos < pacman_pos:
				redghost3_pos = redghost3_pos + 1
			else:
				redghost3_pos = redghost3_pos - 1

		# Eat the food...
		# (if pacman is on the board...)
		if pacman_pos > -1 and pacman_pos < strip.numPixels()-1:
			if food_pos[pacman_pos] == 1:
				print ("Yum")
				food_pos[pacman_pos] = 0
			
		# Eat the star...
		if pacman_pos == star_pos:
			print ("Yum!!! A pill!")
			pacman_dir = 0
			star_pos = -1
			blueghost_pos = redghost_pos
			blueghost2_pos = redghost2_pos
			blueghost3_pos = redghost3_pos
			redghost_pos = -1000
			redghost2_pos = -900
			redghost3_pos = -500

		# pacman eats blue ghost...
		if pacman_pos == blueghost_pos:
			print "YUM!!! Eat blue ghost"
			blueghost_pos = -1000
		else:
			# Blue ghost runs away from pacman
			# slightly slower than pacman
			if pactime % 4 == 0:
				if blueghost_pos < pacman_pos:
					blueghost_pos = blueghost_pos - 1
				else:
					blueghost_pos = blueghost_pos + 1

		if pacman_pos == blueghost2_pos:
			print "YUM!!! Eat blue ghost"
			blueghost2_pos = -1000
		else:
			# Blue ghost runs away from pacman
			# slightly slower than pacman
			if pactime % 4 == 0:
				if blueghost2_pos < pacman_pos:
					blueghost2_pos = blueghost2_pos - 1
				else:
					blueghost2_pos = blueghost2_pos + 1

		if pacman_pos == blueghost3_pos:
			print "YUM!!! Eat blue ghost"
			blueghost3_pos = -1000
		else:
			# Blue ghost runs away from pacman
			# slightly slower than pacman
			if pactime % 4 == 0:
				if blueghost3_pos < pacman_pos:
					blueghost3_pos = blueghost3_pos - 1
				else:
					blueghost3_pos = blueghost3_pos + 1


		# redghost eats pacman
		# Send pacman off the board one way or the other...
		if pacman_pos == redghost_pos or pacman_pos == redghost2_pos or pacman_pos == redghost3_pos:
			print ("Arrrrgh!!!")
			if pacman_dir == 1:
				pacman_pos = pacman_pos + 500
			else:
				pacman_pos = pacman_pos - 500

			
		# Re-initialise if game over
		if (pacman_pos < 0 or pacman_pos > strip.numPixels()-1) and (redghost_pos < 0 or redghost_pos > strip.numPixels()-1) and (redghost2_pos < 0 or redghost2_pos > strip.numPixels()-1) and (redghost3_pos < 0 or redghost3_pos > strip.numPixels()-1) and (blueghost_pos < 0 or blueghost_pos > strip.numPixels()-1) and (blueghost2_pos < 0 or blueghost2_pos > strip.numPixels()-1) and (blueghost3_pos < 0 or blueghost3_pos > strip.numPixels()-1):
			pacman_pos = 1
			pacman_dir = 1 #left to right
			redghost_pos = -80 + randint(0,19)
			redghost2_pos = -105 + randint(0,9)
			redghost3_pos = -120 + randint(0,9)
			ghost_dir = 1 #left to right
			blueghost_pos = -1000
			blueghost2_pos = -1020
			blueghost3_pos = -1030
			star_pos = 140 + randint(0,6)*5
			for i in range(0, strip.numPixels()):
				food_pos.append(1)
			for i in range(0, strip.numPixels()):
				if i % 5 == 0:
					food_pos[i] = 1
				else:
					food_pos[i] = 0
			
		time.sleep(wait_ms/1000)
	time.sleep(1)
		
def ChristmasLights(strip, wait_ms=50):
# Create a strip of randomly coloured lights...

	global red, green, blue
	
	brightness_array = []
	col = []
	for i in range(0, strip.numPixels()):
		brightness_array.append(1)
		col.append(1)

	# Initialise colour & brightness arrays...	
	for i in range(0, strip.numPixels()):
		brightness_array[i] = randint(0,50) - 25
		col[i] = 8

	while checkModeExt() == False:
			
		for i in range(0, strip.numPixels()):
			if brightness_array[i] >= 25:
				brightness_array[i] = -25
			else:
				brightness_array[i] = brightness_array[i] + 1
				
			if brightness_array[i] == 0:
				col[i] = randint(0,7)
			
			if col[i] == 0:   # White
				red = 255
				green = 255
				blue = 255
			elif col[i] == 1: # Yellow
				red = 0
				green = 255
				blue = 255
			elif col[i] == 2: # Cyan
				red = 255
				green = 255
				blue = 0
			elif col[i] == 3: # Green
				red = 0
				green = 255
				blue = 0
			elif col[i] == 4: # Magenta
				red = 255
				green = 0
				blue = 255
			elif col[i] == 5: # Blue
				red = 0
				green = 0
				blue = 255
			elif col[i] == 6: # Red
				red = 255
				green = 0
				blue = 0
			elif col[i] == 7: # Grey
				red = 128
				green = 128
				blue = 128
			else:             # Black
				red = 0
				green = 0
				blue = 0

			brightness = abs(brightness_array[i]) * 4
			setBrightness(red, green, blue, brightness)
			strip.setPixelColor(i, Color(red, green, blue))
	
		strip.show()
		time.sleep(wait_ms/1000.0)

def cheerlights(strip, wait_ms=1000):

    #process the currently available list of colours
    data = getJSON("feed.json")
    for feedItem in data["feeds"]:
        parseColour(feedItem)
    strip.show()

    while checkModeExt() == False:
        data = getJSON("field/1/last.json")
    
        if getEntryID(data) > lastID:   #Has this entry_id been processed before?
            parseColour(data)
            time.sleep(5)
            strip.show()
        else:
            time.sleep(wait_ms/1000.0)
	
def theaterChase(strip, color, wait_ms=50, iterations=10):
	"""Movie theater light style chaser animation."""
	while checkModeExt() == False:
		#for j in range(iterations):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, color)
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)
				

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)
		

def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	# Wait for the Mode button to be pressed
	j = 0
	while checkModeExt() == False:
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)
		if j < (256*iterations)-1:
			j += 1
		else:
			j = 0
	time.sleep(1)
	

def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	global LightingMode, UpdateRequired
	
	# Initialise variables...
	j = 0
	
	# Wait for the Mode button to be pressed or for all iterations to be complete
	while checkModeExt() == False and j < (256*iterations)-1:
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)
		if j < (256*iterations)-1:
			j += 1
		else:
			j = 0

	time.sleep(1)
	#LightingMode = 16
	UpdateRequired = True
	

def theaterChaseRainbow(strip, wait_ms=50):
	"""Rainbow movie theater light style chaser animation."""
	global LightingMode, UpdateRequired
	
	# Initialise variables...
	j = 0
	# Wait for the Mode button to be pressed
	while checkModeExt() == False:
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, wheel((i+j) % 255))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)
		if j < 255:
			j += 1
		else:
			j = 0
	time.sleep(1)

def CountDown(strip, wait_ms=30):
	"""Countdown timer in binary with 10th second resolution."""
	global LightingMode, UpdateRequired, red, green, blue
	
	brightness_array = []
	col = []
	for i in range(0, strip.numPixels()):
		brightness_array.append(1)
		col.append(1)

	# Initialise colour & brightness arrays...	
	for i in range(0, strip.numPixels()):
		brightness_array[i] = randint(0,50) - 25
		col[i] = 8

	offset = int(LED_COUNT / 2) - 13
	
	# Initialise alarm time... (3 minutes)
	AlarmTime = (datetime.datetime(2019,12,25,0,0) - datetime.datetime(1970,1,1)).total_seconds()
	#print (AlarmTime)
	
	#AlarmTime = time.time() + 10
	#print (AlarmTime)
	
	
	TimeLeft = AlarmTime - time.time()

	while checkModeExt() == False and TimeLeft > 0:
		for i in range(0, strip.numPixels()):
			if TimeLeft > 0:
				#color = Color(64, 0, 0) # red
				#strip.setPixelColor(i, color)
				
				if brightness_array[i] >= 25:
					brightness_array[i] = -25
				else:
					brightness_array[i] = brightness_array[i] + 1
					
				if brightness_array[i] == 0:
					col[i] = randint(0,7)
				
				if col[i] == 0:   # White
					red = 255
					green = 255
					blue = 255
				elif col[i] == 1: # Yellow
					red = 0
					green = 255
					blue = 255
				elif col[i] == 2: # Cyan
					red = 255
					green = 255
					blue = 0
				elif col[i] == 3: # Green
					red = 0
					green = 255
					blue = 0
				elif col[i] == 4: # Magenta
					red = 255
					green = 0
					blue = 255
				elif col[i] == 5: # Blue
					red = 0
					green = 0
					blue = 255
				elif col[i] == 6: # Red
					red = 255
					green = 0
					blue = 0
				elif col[i] == 7: # Grey
					red = 128
					green = 128
					blue = 128
				else:             # Black
					red = 0
					green = 0
					blue = 0

				brightness = abs(brightness_array[i]) * 4
				setBrightness(red, green, blue, brightness)
				strip.setPixelColor(i, Color(red, green, blue))
				
				if (i >= offset) and (i < (offset + 26)):
					color = Color(0, 0, 0)
					strip.setPixelColor(i, color)
					if (i - offset) == 0: # Bit(15)
						if int(TimeLeft) & 32768 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 1: # Bit(14)
						if int(TimeLeft) & 16384 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 2: # Bit(13)
						if int(TimeLeft) & 8192 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 3: # Bit(12)
						if int(TimeLeft) & 4096 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 4: # Bit(11)
						if int(TimeLeft) & 2048 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 5: # Bit(10)
						if int(TimeLeft) & 1024 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 6: # Bit(9)
						if int(TimeLeft) & 512 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 7: # Bit(8)
						if int(TimeLeft) & 256 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 8: # Bit(7)
						if int(TimeLeft) & 128 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 9: # Bit(6)
						if int(TimeLeft) & 64 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 10: # Bit(5)
						if int(TimeLeft) & 32 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 11: # Bit(4)
						if int(TimeLeft) & 16 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 12: # Bit(3)
						if int(TimeLeft) & 8 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 13: # Bit(2)
						if int(TimeLeft) & 4 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 14: # Bit(1)
						if int(TimeLeft) & 2 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 15: # Bit(0)
						if int(TimeLeft) & 1 > 0:
							color = Color(255, 255, 255)
							strip.setPixelColor(i, color)
					if (i - offset) == 16: # (0)
						if TimeLeft - int(TimeLeft) > 0.05:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
					if (i - offset) == 17: # (0)
						if TimeLeft - int(TimeLeft) > 0.15:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
					if (i - offset) == 18: # (0)
						if TimeLeft - int(TimeLeft) > 0.25:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
					if (i - offset) == 19: # (0)
						if TimeLeft - int(TimeLeft) > 0.35:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
					if (i - offset) == 20: # (0)
						if TimeLeft - int(TimeLeft) > 0.45:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
					if (i - offset) == 21: # (0)
						if TimeLeft - int(TimeLeft) > 0.55:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
					if (i - offset) == 22: # (0)
						if TimeLeft - int(TimeLeft) > 0.65:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
					if (i - offset) == 23: # (0)
						if TimeLeft - int(TimeLeft) > 0.75:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
					if (i - offset) == 24: # (0)
						if TimeLeft - int(TimeLeft) > 0.85:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
					if (i - offset) == 25: # (0)
						if TimeLeft - int(TimeLeft) > 0.95:
							color = Color(0, 255, 0)
							strip.setPixelColor(i, color)
			else:
				
				color = Color(0, 0, 255)
				strip.setPixelColor(i, color)
				
		strip.show()
		time.sleep(wait_ms/1000.0)
		TimeLeft = AlarmTime - time.time()

	if TimeLeft < 0:
		LightingMode = 16
		UpdateRequired = True

# Main program logic follows:
try:
	#global red, green, blue, brightness, LightingMode, UpdateRequired

	# Check if PWM pin is already being used...
	# Wait for it to be released...
    # WaitPWM function removed

	# Create NeoPixel object with appropriate configuration.
	strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	strip.begin()

	print ("Press Ctrl-C to quit.")

    # Clear any existing colour - set to black...
	allBlack(strip, 5)
	
	if len(sys.argv) > 1:
		LightingMode = int(sys.argv[1])
	
	print ("Lighting Mode: ", ModeLookup[LightingMode])
	
	while True:

		if LightingMode < 12:
			checkModeExt()

		if UpdateRequired:
			print ("Updating...")
			# Reset UpdateRequired to stop this loop repeating
			UpdateRequired = False
			if LightingMode == 0: # White
				#brightness = 50
				red = 255
				green = 255
				blue = 255
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 1: # Candle
				#brightness = 50
				red = 255
				green = 147
				blue = 41
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 2: # Tungsten
				#brightness = 50
				red = 255
				green = 214
				blue = 170
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 3: # Halogen
				#brightness = 50
				red = 255
				green = 241
				blue = 224
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 4: # Overcast
				#brightness = 50
				red = 201
				green = 226
				blue = 255
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 5: # Clear Blue Sky
				#brightness = 50
				red = 64
				green = 156
				blue = 255
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 6: # Yellow
				#brightness = 50
				red = 0
				green = 255
				blue = 255
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 7: # Cyan
				#brightness = 50
				red = 255
				green = 255
				blue = 0
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 8: # Green
				#brightness = 50
				red = 0
				green = 255
				blue = 0
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 9: # Magenta
				#brightness = 50
				red = 255
				green = 0
				blue = 255
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 10: # Blue
				#brightness = 50
				red = 0
				green = 0
				blue = 255
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 11: # Red
				#brightness = 50
				red = 255
				green = 0
				blue = 0
				setBrightness(red, green, blue, brightness)
				colorWipe(strip, Color(red, green, blue),0)
			elif LightingMode == 12:
				cylon(strip, 10)
			elif LightingMode == 13:
				kitt(strip, 5)
			elif LightingMode == 14:
				ChristmasLights(strip,30)
			elif LightingMode == 15:
				theaterChaseRainbow(strip)
			elif LightingMode == 16:
				rainbowCycle(strip)
			elif LightingMode == 17:
				cheerlights(strip,1000)
			elif LightingMode == 18:
				pacman(strip,150)
			elif LightingMode == 19:
				theaterChase(strip, Color(127, 127, 127))  # White theater chase
			elif LightingMode == 20:
				theaterChase(strip, Color(127,   0,   0))  # Red theater chase
			elif LightingMode == 21:
				theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
			elif LightingMode == 22:
				rainbow(strip)
			elif LightingMode == 23:
				rainbowCycle(strip)
			elif LightingMode == 24:
				theaterChaseRainbow(strip)
			elif LightingMode == 25:
				CountDown(strip)

except KeyboardInterrupt:
	print "Keyboard Interrupt (ctrl-c) - exiting program loop"
	allBlack(strip, 5)
	GPIO.setup(LED_PIN, GPIO.IN)

finally:
	GPIO.cleanup()
