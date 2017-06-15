# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import RPi.GPIO as GPIO
import time

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
	# Fill with colour
	setBrightness(255, 255, 255, brightness) # White
	colorWipe(strip, Color(red, green,  blue),0)
	while True:
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
