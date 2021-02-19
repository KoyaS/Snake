'''
Run this file through the command line in order to create a generation of snake brains
to train.

*50 brains per generation*

The next file to run after this one is selfSnake.py
'''

from selfSnakeCopy import NeuralNetwork, set

import pickle
import numpy as np

# class NeuralNetwork: #---------------------------------------------------------------------

# 	def __init__(self, inputs, hidden, hiddenLen, outputs):
# 		networkLen = hidden+2
# 		layerLens = [inputs]
# 		layerLens += [hiddenLen for i in range(0,hidden)]
# 		layerLens.append(outputs)

# 		weights = []
# 		for layerNo in range(1,networkLen):
# 			weights.append(np.random.uniform(0,1,(layerLens[layerNo],layerLens[layerNo-1])))

# 		biases = []
# 		for layerNo in range(1,networkLen):
# 			biases.append(np.random.uniform(0,1,(layerLens[layerNo])))

# 		aLs = []
# 		aLs.append(np.zeros(inputs))
# 		for layerNo in range(1,networkLen):
# 			aLs.append(np.zeros(layerLens[layerNo]))

# 		self.networkLen = networkLen
# 		self.layerLens = layerLens
# 		self.weights = weights
# 		self.biases = biases
# 		self.aLs = aLs

# 	def sigmoid(self, x):
# 		return(1 / (1 + pow(2,-x)))

# 	def chgWeights(self, change_rate):
# 		newWeights = []
# 		for layer in self.weights:
# 			newLayer = []
# 			for weights in layer:
# 					neuronChanges = np.random.uniform(-change_rate, change_rate,len(weights))
# 					weights += neuronChanges
# 					newLayer.append(weights)
# 			newWeights.append(newLayer)
# 		self.weights = newWeights

# 	def chgBiases(self, change_rate):
# 		newBiases = []
# 		for layer in self.biases:
# 			neuronChanges = np.random.uniform(-change_rate, change_rate, len(layer))
# 			layer += neuronChanges
# 			newBiases.append(layer)
# 		self.biases = newBiases

# 	def run(self, inputs):
# 		"""Simple feed forward"""
# 		self.aLs[0] = inputs

# 		for layerNo in range(0,self.networkLen-1):

# 			prevOut = self.aLs[layerNo]
# 			lW = self.weights[layerNo]
# 			lB = self.biases[layerNo]
# 			layerOut = self.sigmoid(np.add(np.dot(lW,prevOut),lB))

# 			self.aLs[layerNo+1] = layerOut

# 		return(self.aLs[self.networkLen-1])

# class set():

# 	def __init__(self, wRate, bRate):
# 		self.wRate = wRate
# 		self.bRate = bRate
# 		self.highestScore = 0
# 		self.highestSnake = 0
# 		self.snakeScores = [0 for i in range (50)]
# 		self.snakeGen = [NeuralNetwork(INPUTS,HIDDEN,HIDDENLEN,OUTPUTS) for i in range(50)]

# 	def train(self, generations):
# 		for generation in range(generations):
# 			self.runSnakes()
# 			if generation%50 == 0:
# 				print(generation, mean(self.snakeScores), max(self.snakeScores))
# 			self.passGenes()

# 	def runSnakes(self):
# 		newScores = []
# 		for snake in self.snakeGen:
# 			sessionAvgs = []
# 			for sessionNo in range(3):
# 				session = snakeGame(10)
# 				score = session.runGame(snake)
# 				sessionAvgs.append(score)
# 				if score > self.highestScore: # Keeping track of best ever snake
# 					self.highestScore = score
# 					self.highestSnake = copy.deepcopy(snake)
# 				del(session)
# 			newScores.append(mean(sessionAvgs))
# 		self.snakeScores = newScores

# 	def passGenes(self):
# 		topSnakes = []
# 		topScores = []
# 		for i in range(10):
# 			topIndex = self.snakeScores.index(max(self.snakeScores))

# 			topSnake = copy.deepcopy(self.snakeGen[topIndex])
# 			topScore = self.snakeScores[topIndex]
# 			self.snakeGen.pop(topIndex)
# 			self.snakeScores.pop(topIndex)
# 			topSnakes.append(topSnake)
# 			topScores.append(topScore)

# 		newSnakes = []
# 		for snake in topSnakes:
# 			snakeCopy = copy.deepcopy(snake)
# 			newSnakes.append(snakeCopy)
# 			for childNo in range(4):
# 				child = copy.deepcopy(snakeCopy)
# 				child.chgWeights(self.wRate)
# 				child.chgBiases(self.bRate)
# 				newSnakes.append(child)

# 		for clss in self.snakeGen:
# 			del(clss)
# 		self.snakeGen = newSnakes


# WRATE, BRATE = 0.01, 0.01
INPUTS = 6
HIDDEN = 50
HIDDENLEN = 10
OUTPUTS = 4

print("CREATING SNAKE GENERATION")
snakeGen = [NeuralNetwork(INPUTS,HIDDEN,HIDDENLEN,OUTPUTS) for i in range(75)]

with open('generationHolder.pkl', 'wb') as output:
	print("Writing to generationHolder.pkl")
	pickle.dump(snakeGen, output, pickle.HIGHEST_PROTOCOL)
