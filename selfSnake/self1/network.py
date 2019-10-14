import numpy as np
import struct

#Training Data
# with open("/Users/koya/Desktop/basicNetwork/trainingData/train-images-idx3-ubyte", mode='rb') as file: # b is important -> binary
#     numbers = struct.unpack(">iiii7840000B", file.read(7840016))[0:789]


np.random.seed(1) #Make randomly generated number same each time

data = np.random.uniform(0,1,4)
labels = np.random.uniform(0,1,4)


class NeuralNetwork:
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

		# for x in weights:
		# 	print(x,"\n")

	def sigmoid(self, x):
		return(1 / (1 + pow(2,-x)))

	def run(self, inputs):
		"""Simple feed forward"""

		self.aLs[0] = inputs

		for layerNo in range(0,self.networkLen-1):

			prevOut = self.aLs[layerNo]
			lW = self.weights[layerNo]
			print(lW)
			print(self.weights[layerNo])
			print("adga")
			lB = self.biases[layerNo]
			layerOut = self.sigmoid(np.add(np.dot(lW,prevOut),lB))

			self.aLs[layerNo+1] = layerOut

			#print(layerNo,"| Weights: ","\n", lW, "\n", "PrevOut: ",prevOut,"\n" , "LayerOut: ", layerOut, "\n")

		return(self.aLs[self.networkLen-1]) 

tst = NeuralNetwork(4,3,5,4)
tst.run(data)






