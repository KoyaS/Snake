#Written using pygame 1.9.4
from statistics import mean
import numpy as np
import pygame
import random
import math
import copy

#Colors
RED = (255,0,0)
BLACK = (0,0,0)
ORANGE = (255,165,0)

screen_width = 500
screen_height = 500
session_moves = 100
showScreen = False

#Training Settings
WRATE, BRATE = 1, 0.1
GENERATIONS = 100

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

class snakeGame(): #----------------------------------------------------------------------

	def __init__(self, food_limit):

		#Constants
		self.food_limit = food_limit
		self.screen_width = 500
		self.screen_height = 500

		#Screen/internal pygame
		pygame.display.init()
		self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
		self.clock = pygame.time.Clock()

		#Group to draw
		self.all_sprites_list = pygame.sprite.Group() 
		self.snake_list = pygame.sprite.Group()

		#Creating Snake
		self.snake_length = 2
		for i in range(self.snake_length):
			block = Block(BLACK,20,20) #Sets outline color, width, height
			block.rect.x = 220-(20*i)
			block.rect.y = 220

			self.snake_list.add(block) #Add to sprite group
			self.all_sprites_list.add(block)

		#Creating food
		self.food_eaten = 0
		self.food = Block(ORANGE,20,20) #Sets color,width,height
		self.food.rect.x = random.randrange(0,screen_width,20)
		self.food.rect.y = random.randrange(0,screen_height,20)
		if self.food.rect.y == 220:
			self.food.rect.y = 300
		self.all_sprites_list.add(self.food)

	def over_edge(self,x,y):
		# For checking if coordinates are over edge of screen
		if x > self.screen_width-20:	
			return(True)
		elif x < 0:
			return(True)
		if y > self.screen_height-20:		
			return(True)
		elif y < 0:
			return(True)
		return(False)
			

	def moveSnake(self, direction):

		first = True
		snakeDie = False
		for link in self.snake_list:

			# For wrapping snake around screen
			if self.over_edge(link.rect.x, link.rect.y):
				snakeDie = True

			if first:
				prevLinkX = link.rect.x
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
		return(currentLinkX,currentLinkY,snakeDie)

	def getHead(self):
		"""Returns xy pos of head and object"""
		head = self.snake_list.sprites()[0]
		return(head.rect.x, head.rect.y, head)

	def snakeCollide(self):
		"""Checks if segments of the snake have hit each other, if yes returns True"""
		head = self.getHead()[2]
		snakeHit = pygame.sprite.spritecollide(head, self.snake_list, False)
		if len(snakeHit) > 1:
			return(True)

	def checkFood(self):
		"""Checks if the snake is colliding with food. If snake is touching,
			moves food, returns True"""
		foodHit = pygame.sprite.spritecollide(self.food, self.snake_list, False)
		if len(foodHit)>0:
			self.food_eaten+=1
			self.food.rect.x = random.randrange(0,screen_width,20)
			self.food.rect.y = random.randrange(0,screen_height,20)
			return(True)

	def snakeVision(self, headPos, direction):
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

		if len(pygame.sprite.spritecollide(visionBlock, self.snake_list, False)) > 0 or self.over_edge(visionBlock.rect.x, visionBlock.rect.y):
			return(1)
		else:
			return(0)

	def snakeDecision(self, network, inputs):
		netOut = network.run(inputs)
		maxPosition = netOut.tolist().index(max(netOut)) # Max value in list
		if maxPosition == 0:
			return("up")
		elif maxPosition == 1:
			return("down")
		elif maxPosition == 2:
			return("right")
		elif maxPosition == 3:
			return("left")

	def runGame(self, network):
		self.food_eaten = 0
		prevDirection = "right"
		direction = "right"
		running = True
		turns = 0
		moves = 0

		while running:

			#Check if player clicks the X
			for event in pygame.event.get(): 
				if event.type == pygame.QUIT: 
					running = False
					exit()
				elif self.food_eaten == self.food_limit:
					running = False
					print("Food Limit Reached")

			if moves >= session_moves:
				running = False

			if showScreen == True:
				self.screen.fill(BLACK) #Clear Screen

			# Network choosing direction
			hx = self.getHead()[0]
			hy = self.getHead()[1]
			fx = self.food.rect.x
			fy = self.food.rect.y
			fdx = fx - hx
			fdy = fy - hy
			fv = abs(math.sqrt((hx-fx)**2 + (hy-fy)**2)) #Distance to food
			v = self.snakeVision((hx,hy),direction)
			inputs = [hx, hy, fdx, fdy, fv, v]
			direction = self.snakeDecision(network,inputs)
			prevX,prevY,snakeDie = self.moveSnake(direction)

			if prevDirection != direction: # For scoring snake for turns
				prevDirection = direction
				turns += 1
			
			if self.checkFood(): #Extends Snake
				block = Block(BLACK,20,20)
				block.rect.x = prevX
				block.rect.y = prevY
				self.snake_list.add(block)
				self.all_sprites_list.add(block)

			if showScreen == True:
				self.all_sprites_list.draw(self.screen) # Draws all sprites to screen
				pygame.display.flip() # Updates screen with drawn sprites
				self.clock.tick(60) # Moves time forward
			moves += 1 # For counting number of moves

			if snakeDie or self.snakeCollide(): # Checks if the snake hits the edge of the screen or itself
				running = False

		snakeScore = self.food_eaten + (moves*0.01) - (turns*0.01) #self.food_eaten*10 + moves #(turns*0.1)+(1*self.food_eaten)
		if showScreen:
			print(snakeScore)
		# pygame.quit()
		return(snakeScore)


class NeuralNetwork: #---------------------------------------------------------------------

	def __init__(self, inputs, hidden, hiddenLen, outputs):
		networkLen = hidden+2
		layerLens = [inputs]
		layerLens += [hiddenLen for i in range(0,hidden)]
		layerLens.append(outputs)

		weights = []
		for layerNo in range(1,networkLen):
			weights.append(np.random.uniform(0,1,(layerLens[layerNo],layerLens[layerNo-1])))

		biases = []
		for layerNo in range(1,networkLen):
			biases.append(np.random.uniform(0,1,(layerLens[layerNo])))

		aLs = []
		aLs.append(np.zeros(inputs))
		for layerNo in range(1,networkLen):
			aLs.append(np.zeros(layerLens[layerNo]))

		self.networkLen = networkLen
		self.layerLens = layerLens
		self.weights = weights
		self.biases = biases
		self.aLs = aLs

	def sigmoid(self, x):
		return(1 / (1 + pow(2,-x)))

	def chgWeights(self, change_rate):
		newWeights = []
		for layer in self.weights:
			newLayer = []
			for weights in layer:
					neuronChanges = np.random.uniform(-change_rate, change_rate,len(weights))
					weights += neuronChanges
					newLayer.append(weights)
			newWeights.append(newLayer)
		self.weights = newWeights

	def chgBiases(self, change_rate):
		newBiases = []
		for layer in self.biases:
			neuronChanges = np.random.uniform(-change_rate, change_rate, len(layer))
			layer += neuronChanges
			newBiases.append(layer)
		self.biases = newBiases

	def run(self, inputs):
		"""Simple feed forward"""
		self.aLs[0] = inputs

		for layerNo in range(0,self.networkLen-1):

			prevOut = self.aLs[layerNo]
			lW = self.weights[layerNo]
			lB = self.biases[layerNo]
			layerOut = self.sigmoid(np.add(np.dot(lW,prevOut),lB))

			self.aLs[layerNo+1] = layerOut

		return(self.aLs[self.networkLen-1])

class set():

	def __init__(self, wRate, bRate):
		self.wRate = wRate
		self.bRate = bRate
		self.highestScore = 0
		self.highestSnake = 0
		self.snakeScores = [0 for i in range (50)]
		self.snakeGen = [NeuralNetwork(6,3,10,4) for i in range(50)]

	def train(self, generations):
		for generation in range(generations):
			self.runSnakes()
			if generation%50 == 0:
				print(generation, mean(self.snakeScores), max(self.snakeScores))
			self.passGenes()

	def runSnakes(self):
		newScores = []
		for snake in self.snakeGen:
			session = snakeGame(10)
			score = session.runGame(snake)
			newScores.append(score)
			if score > self.highestScore: # Keeping track of best ever snake
				self.highestScore = score
				self.highestSnake = copy.deepcopy(snake)
		self.snakeScores = newScores

	def passGenes(self):
		topSnakes = []
		topScores = []
		for i in range(10):
			topIndex = self.snakeScores.index(max(self.snakeScores))

			topSnake = copy.deepcopy(self.snakeGen[topIndex])
			topScore = self.snakeScores[topIndex]
			self.snakeGen.pop(topIndex)
			self.snakeScores.pop(topIndex)
			topSnakes.append(topSnake)
			topScores.append(topScore)

		newSnakes = []
		for snake in topSnakes:
			snakeCopy = copy.deepcopy(snake)
			newSnakes.append(snakeCopy)
			for childNo in range(4):
				child = copy.deepcopy(snakeCopy)
				child.chgWeights(self.wRate)
				child.chgBiases(self.bRate)
				newSnakes.append(child)
		self.snakeGen = newSnakes

population = set(WRATE, BRATE)
population.train(GENERATIONS)

showScreen = True
print("HIGHEST SCORE: ", population.highestScore)
for i in range(10):
	bestSession = snakeGame(10)
	bestSession.runGame(population.highestSnake)

