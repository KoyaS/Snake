''' 
This file is meant to be run through the command line after a training session.
This file funs best saved snake brain in the simulation.

Run this file after commenting the designated lines in the bottom of selfSnake.py
'''

from selfSnakeCopy import snakeGame, NeuralNetwork
import pickle
showScreen=True
with open('bestSnake.pkl', 'rb') as input:
	snakeBrain = pickle.load(input)
	for i in range(10):
		bestSession = snakeGame(10)
		bestSession.showScreen = True
		bestSession.runGame(snakeBrain)