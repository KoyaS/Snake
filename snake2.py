#Written using pygame 1.9.4
import pygame
import random

#Constants
snake_length = 3

RED = (255,0,0)
BLACK = (0,0,0)
ORANGE = (255,165,0)

screen_width = 500
screen_height = 500

food_limit = 10

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

#Snake Movement
direction = "right"
def moveSnake(direction):

	first = True
	for link in snake_list:
		if link.rect.x > screen_width-20:
			link.rect.x = 0
		elif link.rect.x < 0:
			link.rect.x += screen_width


		if link.rect.y > screen_height-20:
			link.rect.y = 0
		elif link.rect.y < 0:
			link.rect.y += screen_height

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

def snakeCollide():
	"""Checks if segments of the snake have hit each other, if yes returns True"""
	first = True
	snakeHit=[]
	for link in snake_list:
		if first:
			snakeHit = pygame.sprite.spritecollide(link, snake_list, False)
			print(snakeHit)
			first = False
	if len(snakeHit)>1:
		return(True)

#Creating food
food = Block(ORANGE,20,20) #Sets color,width,height
global food_eaten
food_eaten=0
food.rect.x = random.randrange(screen_width)
food.rect.y = random.randrange(screen_height)
all_sprites_list.add(food)

def checkFood():
	"""Checks if the snake is colliding with food. If snake is touching,
		moves food, returns True"""
	foodHit = pygame.sprite.spritecollide(food, snake_list, False)
	if len(foodHit)>0:
		global food_eaten
		food_eaten+=1
		food.rect.x = random.randrange(0,screen_width,20)
		food.rect.y = random.randrange(0,screen_height,20)
		print(food_eaten)
		return(True)

#Main loop
running = True
while running:

	#Check if player clicks the X
	for event in pygame.event.get(): 
		if event.type == pygame.QUIT: 
			running = False
		elif food_eaten == food_limit:
			running = False

	#Clear Screen
	screen.fill(BLACK)

	keys = pygame.key.get_pressed() # up[273] down[274] right[275] left[276]

	if keys[273]==1 and direction != "down":
		direction="up"
	elif keys[274]==1 and direction != "up":
		direction="down"
	elif keys[275]==1 and direction != "left":
		direction="right"
	elif keys[276]==1 and direction != "right":
		direction="left"

	prevX,prevY = moveSnake(direction)
	
	if checkFood():
		#Extends Snake
		block = Block(BLACK,20,20)
		block.rect.x = prevX
		block.rect.y = prevY
		snake_list.add(block)
		all_sprites_list.add(block)

	if snakeCollide():
		running=False

	all_sprites_list.draw(screen) # Draws all sprites to screen
	pygame.display.flip() # Updates screen with drawn sprites
	clock.tick(10) # Moves time forward

