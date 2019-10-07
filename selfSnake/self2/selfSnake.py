#Written using pygame 1.9.4
import numpy as np
import statistics
import pygame
import random
import math

#Game Settings
food_limit = 10
session_moves = 100
showScreen = False

#Colors
RED = (255,0,0)
BLACK = (0,0,0)
ORANGE = (255,165,0)

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
		self.snake_length = 3
		self.food_limit = food_limit
		self.screen_width = 500
		self.screen_height = 500

		#Screen/internal pygame
		pygame.display.init()
		self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
		self.clock = pygame.time.Clock()

		self.all_sprites_list = pygame.sprite.Group() #Group to draw
		self.snake_list = pygame.sprite.Group()

		#Creating Snake
		for i in range(self.snake_length):
			block = Block(BLACK,20,20) #Sets outline color, width, height
			block.rect.x = 300-(20*i)
			block.rect.y = 200

			self.snake_list.add(block) #Add to sprite group
			self.all_sprites_list.add(block)

		#Creating food
		self.food_eaten = 0
		self.food = Block(ORANGE,20,20) #Sets color,width,height
		self.food.rect.x = random.randrange(self.screen_width)
		self.food.rect.y = random.randrange(self.screen_height)
		self.all_sprites_list.add(self.food)

	def moveSnake(self, direction):
		"""Least semantic code yet functional"""
		first = True
		for link in self.snake_list:

			# For wrapping snake around screen
			if link.rect.x > self.screen_width-20:
				link.rect.x = 0
			elif link.rect.x < 0:
				link.rect.x += self.screen_width
			if link.rect.y > self.screen_height-20:
				link.rect.y = 0
			elif link.rect.y < 0:
				link.rect.y += self.screen_height

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
		return(currentLinkX,currentLinkY)

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
			self.food.rect.x = random.randrange(0,self.screen_width,20)
			self.food.rect.y = random.randrange(0,self.screen_height,20)
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

		if len(pygame.sprite.spritecollide(visionBlock, self.snake_list, False)) > 0:
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
		random.seed(1)
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
			fv = math.sqrt((hx-fx)**2 + (hy-fy)**2)
			v = self.snakeVision((hx,hy),direction)
			inputs = [hx, hy, fx, fy, fv, v]
			direction = self.snakeDecision(network,inputs)
			prevX,prevY = self.moveSnake(direction)

			if prevDirection != direction: # For scoring snake for turns
				prevDirection = direction
				turns += 1
			
			if self.checkFood(): #Extends Snake
				block = Block(BLACK,20,20)
				block.rect.x = prevX
				block.rect.y = prevY
				self.snake_list.add(block)
				self.all_sprites_list.add(block)

			if self.snakeCollide():
				running=False

			if showScreen == True:
				self.all_sprites_list.draw(self.screen) # Draws all sprites to screen
				pygame.display.flip() # Updates screen with drawn sprites
				self.clock.tick(60) # Moves time forward
			moves += 1 # For counting number of moves

		snakeScore = (turns*0.1)+(1*self.food_eaten)
		if showScreen:
			print(snakeScore)
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

class trainSet(): #----------------------------------------------------------------------

	def __init__(self, snakes_per_gen, bias_rate, weight_rate):

		if snakes_per_gen%5 != 0:
			return("ERROR, SNAKES/GEN MUST BE MULTIPLE OF 5")
		self.snakes_per_gen = snakes_per_gen
		self.bias_rate = bias_rate
		self.weight_rate = weight_rate

		self.snakeGen = [] # Holds networks for all snakes
		self.topSnakes = [] # Holds best preforming snakes from each generation
		self.snakeScores = [0 for i in range(self.snakes_per_gen)] 
		self.weightChanges = [] 
		self.biasChanges = []

		self.highestScore = 0
		self.highestSnake = []

		for snakeNo in range(snakes_per_gen):
			snakeBrain = NeuralNetwork(6,3,8,4)
			self.snakeGen.append(snakeBrain)


	def runSet(self):
		"""Runs snakes through a single generation"""
		newScores = []
		for snake in self.snakeGen:
			session = snakeGame(food_limit)
			snakeScore = session.runGame(snake)
			newScores.append(snakeScore)

		self.snakeScores = newScores

	def passGenes(self):
		highestScoreIndex = self.snakeScores.index(max(self.snakeScores)) # Gets index of highest scoring snake
		if self.snakeScores[highestScoreIndex] > self.highestScore:
			self.highestSnake = self.snakeGen[highestScoreIndex]
			self.highestScore = self.snakeScores[highestScoreIndex]

		topSnakes = []
		topSnakeCount = self.snakes_per_gen/5
		for snakeID in range(int(topSnakeCount)): # Loop for getting top 20% of snakes from generation 
			maxScoreIndex = self.snakeScores.index(max(self.snakeScores)) # Gets index of highest scoring snake
			self.snakeScores.pop(maxScoreIndex) # Removes score at max index
			topSnakes.append(self.snakeGen.pop(maxScoreIndex)) # Removes max scoring snake and adds it to topSnakes
		self.topSnakes = topSnakes

		newSnakes = []
		for snake in topSnakes: # For every snake in topSnakes makes children
			newSnakes.append(snake)
			snakeCopy = snake
			for child in range(int(self.snakes_per_gen/5-1)):
				snake = snakeCopy
				snake.chgWeights(self.weight_rate)
				snake.chgBiases(self.bias_rate)
				newSnakes.append(snake)
		#print("newSnakes", len(newSnakes))
		self.snakeGen = newSnakes



	def train(self, generations):
		seedList = [i for i in range(2,generations+2)]
		for genNo in range(generations):
			print(genNo, "Avg Score: ", statistics.mean(self.snakeScores))
			self.runSet() # Changes self.snakeScores
			random.seed(seedList[genNo])
			self.passGenes()

		


set1 = trainSet(50,0.1,0.3)
set1.train(5)

showScreen = True
print("Highest Score:", set1.highestScore)
bestSession = snakeGame(food_limit)
bestSession.runGame(set1.highestSnake)




