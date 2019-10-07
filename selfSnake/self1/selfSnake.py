#Written using pygame 1.9.4
import statistics as stats
import numpy as np
import network
import pygame
import random
import math

#Constants
snake_length = 3

RED = (255,0,0)
BLACK = (0,0,0)
ORANGE = (255,165,0)

screen_width = 500
screen_height = 500

food_limit = 100

movents_allowed = 100
snakes_per_generation = 50

showScreen = False

#Snake Network Settings
inputs = 6
hidden = 3
hiddenLen = 10
outputs = 4
learnRate = 0.5

#Pre Loop
pygame.display.init()
screen = pygame.display.set_mode([screen_width, screen_height])

clock = pygame.time.Clock()

#Pygame sprite class - taken from website
class Block(pygame.sprite.Sprite):

	# Constructor. Pass in the color of the block,
	# and its x and y position
	def __init__(self, color, width, height):
	   # Call the parent class (Sprite) constructor
	   pygame.sprite.Sprite.__init__(self)

	   # Create an image of the block, and fill it with a color.
	   # This could also be an image loaded from the disk.
	   self.image = pygame.Surface([width, height])
	   self.image.fill(color)
	   self.image.fill(RED, self.image.get_rect().inflate(-3, -3)) #adds an outline

	   # Fetch the rectangle object that has the dimensions of the image
	   # Update the position of this object by setting the values of rect.x and rect.y
	   self.rect = self.image.get_rect(width=20,height=20)

#Group to draw
all_sprites_list = pygame.sprite.Group()

#Creating Snake
snake_list = pygame.sprite.Group()
for i in range(snake_length):
	#Sets outline color, width, height
	block = Block(BLACK,20,20) 

	block.rect.x = 300-(20*i)
	# block.rect.x = 0+(20*i)
	block.rect.y = 200

	snake_list.add(block) #Add to sprite group
	all_sprites_list.add(block)

default_snake_list = snake_list

#Snake Movement
direction = "right"
def moveSnake(direction):

	sideCollision = False
	first = True
	for link in snake_list:
		#For wrapping snake around screen horizontally
		if link.rect.x > screen_width-20:
			link.rect.x = 0
			# sideCollision = True
		elif link.rect.x < 0:
			link.rect.x += screen_width
			# sideCollision = True
		#For wrapping snake around screen vertically
		if link.rect.y > screen_height-20:
			link.rect.y = 0
			# sideCollision = True
		elif link.rect.y < 0:
			link.rect.y += screen_height
			# sideCollision = True

		if first:
			firstX = link.rect.x
			prevLinkX = link.rect.x
			firstY = link.rect.y
			prevLinkY = link.rect.y	
			if direction=="up":
				link.rect.y -= 20
			elif direction=="down":
				link.rect.y += 20
			elif direction=="right":
				link.rect.x += 20
			elif direction=="left":
				link.rect.x -= 20
			first=False
		else:
			currentLinkY = link.rect.y
			currentLinkX = link.rect.x
			link.rect.y = prevLinkY
			link.rect.x = prevLinkX
			prevLinkY = currentLinkY
			prevLinkX = currentLinkX

	return(currentLinkX,currentLinkY, firstX, firstY, sideCollision)

def snakeCollide():
	"""Checks if segments of the snake have hit each other, if yes returns True"""
	first = True
	snakeHit=[]
	for link in snake_list:
		if first:
			snakeHit = pygame.sprite.spritecollide(link, snake_list, False)
			first = False
	if len(snakeHit)>1:
		return(True)

def snakeVision(headPos, direction):
	visionBlock = Block(BLACK,20,20)

	visionBlock.rect.x = headPos[0]
	visionBlock.rect.y = headPos[1]

	if direction=="up":
		visionBlock.rect.y -= 20
	elif direction=="down":
		visionBlock.rect.y += 20
	elif direction=="right":
		visionBlock.rect.x += 20
	elif direction=="left":
		visionBlock.rect.x -= 20

	if len(pygame.sprite.spritecollide(visionBlock, snake_list, False)) > 0:
		return(True)
	else:
		return(False)

	

def snakeHeadPos():
	"""Returns position of head of snake"""
	first = True
	for link in snake_list:
		if first:
			first = False
			headX = link.rect.x
			headY = link.rect.y
		return(headX, headY, link)

#Creating food
food = Block(ORANGE,20,20) #Sets color,width,height
global food_eaten
food_eaten=0
foodStartX = random.randrange(screen_width)
foodStartY = random.randrange(screen_height)
food.rect.x = foodStartX
food.rect.y = foodStartY
all_sprites_list.add(food)

default_all_sprites_list = all_sprites_list

def checkFood():
	"""Checks if the snake is colliding with food. If snake is touching,
		moves food, returns True"""
	foodHit = pygame.sprite.spritecollide(food, snake_list, False)
	if len(foodHit)>0:
		global food_eaten
		food_eaten+=1
		food.rect.x = random.randrange(0,screen_width,20)
		food.rect.y = random.randrange(0,screen_height,20)
		#print(food_eaten)
		return(True)

class generation():

	def __init__(self, numSnakes, learnRate):

		#Creating list of snake network objects
		self.snakeGen = []
		self.learnRate = learnRate
		self.numSnakes = numSnakes

		for i in range(numSnakes):
			self.snakeGen.append(network.NeuralNetwork(inputs, hidden, hiddenLen, outputs))

		self.snakeScores = np.zeros(numSnakes) #Initializing snake list

	def runSnakes(self):
		"""Passes each of the snakes through the game where the 
			network must use 200 moves as efficiently as possible"""
		snakeID = 0
		for snake in self.snakeGen:
			score = self.runGame(snake)
			self.snakeScores[snakeID] = score
			snakeID += 1

		return(self.snakeScores)

	def readOutput(self, network, xf, yf, xh, yh, v, fd):
		"""Will run values of network and output a direction 
			("up", "down",etc) for snake to move in."""

		netOut = network.run([xf,yf,xh,yh,v,fd])
		maxPosition = netOut.tolist().index(max(netOut))

		if maxPosition == 0:
			return("up")
		elif maxPosition == 1:
			return("down")
		elif maxPosition == 2:
			return("right")
		elif maxPosition == 3:
			return("left")
		else:
			return("readOutput error")

	def chgWeights(self, snakeNet):
		newWeights = []
		for layer in snakeNet.weights:
			newLayer = []
			for weights in layer:
					neuronChanges = np.random.uniform(-self.learnRate,self.learnRate,len(weights))
					weights += neuronChanges
					newLayer.append(weights)
			newWeights.append(newLayer)
		return(newWeights)

	def chgBiases(self, snakeNet):
		newLayers = []
		for layer in snakeNet.biases:
			
			neuronChanges = np.random.uniform(-self.learnRate,self.learnRate,len(layer))
			layer += neuronChanges
			newLayers.append(layer)

		return(newLayers)

	def passGenes(self):
		"""Evaluates performance of previous generation and creates
			'child' snakes from the top 20%. Takes inputs
			from the self.snakeGen and self.snakeScores. Outputs new
			list of snakes as next generation."""
		topSnakes = []
		tempSnakeScores = self.snakeScores.tolist()

		#Loop determines best snakes after trials
		for snakeNum in range(10):
			topSnakeIndex = tempSnakeScores.index(max(tempSnakeScores))
			tempSnakeScores.pop(topSnakeIndex)
			topSnakes.append(self.snakeGen.pop(topSnakeIndex))

		#Loop Creates children from top 10 snakes
		newSnakes = []
		for topSnake in topSnakes: 
			newSnakes.append(topSnake)
			for childNo in range(4):
				newSnake = topSnake
				newSnake.weights = self.chgWeights(topSnake)
				newSnake.biases = self.chgBiases(newSnake)
				newSnakes.append(newSnake)

		return(newSnakes)

	def train(self):
		self.snakeScores = self.runSnakes()
		self.snakeGen = self.passGenes()
		return(stats.mean(self.snakeScores), max(self.snakeScores))

	def runGame(self, snakeNet):
		global food_eaten
		food_eaten = 0
		direction = "right"
		prevDir = "right"
		snakeDir = "right"
		turn_count = 0

		#Creating Snake
		snake_list = pygame.sprite.Group()
		all_sprites_list = pygame.sprite.Group()
		for i in range(snake_length):
			#Sets outline color, width, height
			block = Block(BLACK,20,20) 
			block.rect.x = 300-(20*i)
			block.rect.y = 200
			snake_list.add(block) #Add to sprite group
			all_sprites_list.add(block)

		#Creating food
		food = Block(ORANGE,20,20) #Sets color,width,height
		food.rect.x = random.randrange(40,screen_width)
		food.rect.y = random.randrange(40,screen_height)
		all_sprites_list.add(food)

		snakeHeadPos()[2].rect.x = 20
		snakeHeadPos()[2].rect.y = 20

		

		#Main loop -------------------------------------------------------------
		
		for move in range(movents_allowed):

			if showScreen:
				#Check if player clicks the X
				for event in pygame.event.get(): 
					if event.type == pygame.QUIT: 
						exit()
					elif food_eaten == food_limit:
						running = False
				#Clear Screen
				screen.fill(BLACK)

				all_sprites_list.draw(screen) # Draws all sprites to screen
				pygame.display.flip() # Updates screen with drawn sprites
				clock.tick(120) # Moves time forward

			#Network inputs (foodx/y headx/y visiont/f)
			xf = food.rect.x
			yf = food.rect.y
			xh, yh, headObj = snakeHeadPos()
			v = snakeVision([xh,yh],direction)
			fd = math.sqrt((xf-xh)**2 + (yf-yh)**2)

			snakeDir = self.readOutput(snakeNet,xf,yf,xh,yh,v,fd) #Output of network

			if snakeDir != prevDir:

				if snakeDir == "up" and direction != "down":
					direction="up"
					turn_count += 1
				elif snakeDir == "down" and direction != "up":
					direction="down"
					turn_count += 1
				elif snakeDir == "right" and direction != "left":
					direction="right"
					turn_count += 1
				elif snakeDir == "left" and direction != "right":
					direction="left"
					turn_count += 1

			prevDir = direction

			prevX,prevY,headX,headY,sideCollision = moveSnake(direction)
			
			if checkFood():
				#Extends Snake
				block = Block(BLACK,20,20)
				block.rect.x = prevX
				block.rect.y = prevY
				snake_list.add(block)
				all_sprites_list.add(block)

			if snakeCollide():
				return(0)

		return(food_eaten+(turn_count*0.1))

gen1 = generation(snakes_per_generation, learnRate)

prevTrainOut = 0
for i in range(100000):
	trainOut = gen1.train()
	print(i, trainOut)
	if trainOut[1]>10:
		showScreen=True
	
