
# neopixels.py
# Kitchen lights controller
# By Mark Cantrill (mark@astro-designs.com)
# Originally based on NeoPixel library strandtest example by Tony DiCola
# Direct port of the Arduino NeoPixel library strandtest example.

# Mode button allows some rudimentary control over the strand 'pattern'
# Plus & Minus buttons add brightness a level of brightness control to some patterns

import RPi.GPIO as GPIO
import time
from random import randint

from neopixel import *


# LED strip configuration:
LED_COUNT      = 189     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pinButtonMinus = 17
pinButtonPlus = 27
pinButtonMode = 22
pinLED = 4

LED_state = True
brightness = 50
colour = 0
red = 255
green = 255
blue = 255

GPIO.setup(pinButtonMode, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pinButtonPlus, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pinButtonMinus, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pinLED, GPIO.OUT)

GPIO.output(pinLED, LED_state)

def waitMode(hold_time=0.25):
	global LED_state
	while GPIO.input(pinButtonMode) == False:
		LED_state = not LED_state
		GPIO.output(pinLED, LED_state)
		time.sleep(0.25)

	LED_State = True
	GPIO.output(pinLED, LED_state)
	time.sleep(hold_time)
	
def setBrightness(red_100, green_100, blue_100, brightness = 100):
	global red, green, blue
	red = int(red_100 * (brightness / 100.0))
	green = int(green_100 * (brightness / 100.0))
	blue = int(blue_100 * (brightness / 100.0))
	if red > 255: red = 255
	if green > 255: green = 255
	if blue > 255: blue = 255
	print ("Adjusting RGB to: ", red, green, blue)

def waitButtons(hold_time=0.25):
	global LED_state, brightness, red, green, blue, colour
	while GPIO.input(pinButtonMode) == False and GPIO.input(pinButtonPlus) == False and GPIO.input(pinButtonMinus) == False:
		LED_state = not LED_state
		GPIO.output(pinLED, LED_state)
		time.sleep(hold_time)

	if GPIO.input(pinButtonPlus) == True:
		if brightness < 100:
			brightness = brightness + 10
		else: brightness = 100
		#print ("Brightness = ", brightness)
		time.sleep(hold_time)
		
	if GPIO.input(pinButtonMinus) == True:
		if brightness > 0:
			brightness = brightness - 10
		else: brightness = 0
		#print ("Brightness = ", brightness)
		time.sleep(hold_time)
        
	if GPIO.input(pinButtonMode) == True:
		if colour < 15:
			colour = colour + 1
		else: colour = 0
		#print ("Colour =", colour)
		time.sleep(hold_time)

	if colour == 0: # White
		red = 255
		green = 255
		blue = 255
	elif colour == 1: # Candle
		red = 255
		green = 147
		blue = 41
	elif colour == 2: # Tungsten
		red = 255
		green = 214
		blue = 170
	elif colour == 3: # Halogen
		red = 255
		green = 241
		blue = 224
	elif colour == 4: # Overcast
		red = 201
		green = 226
		blue = 255
	elif colour == 5: # Clear Blue Sky
		red = 64
		green = 156
		blue = 255
	elif colour == 6: # Yellow
		red = 0
		green = 255
		blue = 255
	elif colour == 7: # Cyan
		red = 255
		green = 255
		blue = 0
	elif colour == 8: # Green
		red = 0
		green = 255
		blue = 0
	elif colour == 9: # Magenta
		red = 255
		green = 0
		blue = 255
	elif colour == 10: # Blue
		red = 0
		green = 0
		blue = 255
	elif colour == 11: # Red
		red = 255
		green = 0
		blue = 0

	print red, green, blue, brightness
	LED_state = True
	GPIO.output(pinLED, LED_state)

def allWhite(strip, wait_ms=50):
	"""Fill strip with white"""
	color = Color(255,255,255)
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
	
	while GPIO.input(pinButtonMode) == 0:
		strip.setPixelColor(i,  Color(16,16,16))
		strip.setPixelColor(i1, Color(32,32,0))
		strip.setPixelColor(i2, Color(64,64,0))
		strip.setPixelColor(i3, Color(200,200,0))
		strip.setPixelColor(i4, Color(255,255,0))
		strip.setPixelColor(i5, Color(255,255,0))
		strip.setPixelColor(i6, Color(200,200,0))
		strip.setPixelColor(i7, Color(64,64,0))
		strip.setPixelColor(i8, Color(32,32,0))
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
	
	while GPIO.input(pinButtonMode) == 0:
		strip.setPixelColor(i,   Color(0,255,0))
		strip.setPixelColor(i1,  Color(0,255,0))
		strip.setPixelColor(i2,  Color(0,255,0))
		strip.setPixelColor(i3,  Color(0,255,0))
		strip.setPixelColor(i4,  Color(0,200,0))
		strip.setPixelColor(i5,  Color(0,200,0))
		strip.setPixelColor(i6,  Color(0,200,0))
		strip.setPixelColor(i7,  Color(0,150,0))
		strip.setPixelColor(i8,  Color(0,150,0))
		strip.setPixelColor(i9,  Color(0,150,0))
		strip.setPixelColor(i10, Color(0,100,0))
		strip.setPixelColor(i11, Color(0,100,0))
		strip.setPixelColor(i12, Color(0,100,0))
		strip.setPixelColor(i13, Color(0,50,0))
		strip.setPixelColor(i14, Color(0,50,0))
		strip.setPixelColor(i15, Color(0,50,0))
		strip.setPixelColor(i16, Color(0,50,0))
		strip.setPixelColor(i17, Color(0,25,0))
		strip.setPixelColor(i18, Color(0,25,0))
		strip.setPixelColor(i19, Color(0,25,0))
		strip.setPixelColor(i20, Color(0,25,0))
		strip.setPixelColor(i21, Color(0,12,0))
		strip.setPixelColor(i22, Color(0,12,0))
		strip.setPixelColor(i23, Color(0,12,0))
		strip.setPixelColor(i24, Color(0,12,0))
		strip.setPixelColor(i25, Color(0,6,0))
		strip.setPixelColor(i26, Color(0,6,0))
		strip.setPixelColor(i27, Color(0,6,0))
		strip.setPixelColor(i28, Color(0,6,0))
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
		
		time.sleep(wait_ms/1000.0)
	time.sleep(1)
	

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
	
	while GPIO.input(pinButtonMode) == 0:
		# Timer...
		if pactime > 0:
			pactime = pactime - 1
		else:
			pactime = 699
				
		# display board...
		for i in range(0, strip.numPixels()):
			if i == redghost_pos or i-1 == redghost_pos or i+1 == redghost_pos:
				color = Color(0, 255, 0) # red
			elif i == redghost2_pos or i-1 == redghost2_pos or i+1 == redghost2_pos:
				color = Color(0, 255, 0) # red
			elif i == redghost3_pos or i-1 == redghost3_pos or i+1 == redghost3_pos:
				color = Color(0, 255, 0) # red
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
				food_pos[pacman_pos] = 0
			
		# Eat the star...
		if pacman_pos == star_pos:
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
			print "Eat blue ghost"
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
			print "Eat blue ghost"
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
			print "Eat blue ghost"
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
		
	
def theaterChase(strip, color, wait_ms=50, iterations=10):
	"""Movie theater light style chaser animation."""
	for j in range(iterations):
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
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
	"""Rainbow movie theater light style chaser animation."""
	for j in range(256):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, wheel((i+j) % 255))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)


# Main program logic follows:
if __name__ == '__main__':
	global red, green, blue, brightness, colour
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	strip.begin()

	print ('Press Ctrl-C to quit.')
	cylon(strip, 4)
	kitt(strip, 0)
	pacman(strip,150)
	
	while True:
		# Fill with colour
		setBrightness(255, 255, 255, brightness) # White
		colorWipe(strip, Color(red, green,  blue),0)
		waitButtons()

		if colour < 11:
			setBrightness(red, green, blue, brightness)
			colorWipe(strip, Color(red, green,  blue),0)
		else:
			# Theater chase animations.
			theaterChase(strip, Color(127, 127, 127))  # White theater chase
			#waitMode()
			theaterChase(strip, Color(127,   0,   0))  # Red theater chase
			#waitMode()
			theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
			#waitMode()
			# Rainbow animations.
			rainbow(strip)
			rainbowCycle(strip)
			theaterChaseRainbow(strip)
