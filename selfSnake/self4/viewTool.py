from selfSnakeCopy import snakeGame, NeuralNetwork
import pickle
showScreen=True
with open('bestSnake.pkl', 'rb') as input:
	snakeBrain = pickle.load(input)
	for i in range(10):
		bestSession = snakeGame(10)
		bestSession.showScreen = True
		bestSession.runGame(snakeBrain)
