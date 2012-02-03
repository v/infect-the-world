#Import Modules 
import sys, pygame, math, random 
from pygame.locals import * 

window_width = 1024
window_height = 768 

#defining some colors
dark_green = ( 115, 163, 24 )
blue = ( 32, 108, 115 )
blood_red = ( 214, 67, 46)
gray = ( 219, 219, 219 )
black = ( 0, 0, 0 )

NUM_ANTIBODIES = 5
NUM_CELLS = 3

def normalize(vector):
	length = math.sqrt(vector[0]**2 + vector[1]** 2)

	if length == 0:
		return vector

	vector[0] /= length
	vector[1] /= length

	return vector

def vec_length(vector):
	return math.sqrt(vector[0]**2 + vector[1]** 2)

class Ball(pygame.sprite.Sprite): 
	"""Ball class""" 
	def __init__(self, color, position=None): 
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer 

		self.color = color

		self.flung = False

		# Create the surface for the ball, and draw to that surface: 
		self.radius = 20 
		self.image = pygame.Surface((self.radius*2, self.radius*2)) 
		self.image = self.image.convert_alpha() 
		self.image.fill((0,0,0,0)); 
		pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius) 
		self.rect = self.image.get_rect() 

		self.locked = pygame.sprite.GroupSingle()

		# Set initial position 
		if position == None:
			position = [random.randint(50,590), random.randint(50,430)]  
		self._position = position
		self.rect.center = tuple(position)

		# Set initial velocity 
		self.velocity = [0, 0]
		self.dragged = False

		self.type = 'default'
		
	def set_radius(self, radius):
		self.radius = radius
		self.image = pygame.Surface((self.radius*2, self.radius*2)) 
		self.image = self.image.convert_alpha() 
		self.image.fill((0,0,0,0)); 
		pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius) 
		self.rect = self.image.get_rect() 


	def move_randomly(self):
		range = 2 
		self.velocity = [random.randint(-range*2, -range), random.randint(-range,range)]

	def move_horizontally(self):
		self.velocity = [ -2, 0 ]
	
	def oscillate(self):
		new_position = list(self._position)
		new_position[0] = window_width/3
		#new_position[1] = random.randint(window_height/4, 3*window_height/4)

		direction = [new_position[0] - self.x() , new_position[1] - self.y()]
		normalize(direction)

		MAGNITUDE = 3

		self.velocity = [direction[0]*MAGNITUDE, direction[1]*MAGNITUDE]

	def get_position(self):
		return list(self._position)

	def set_position(self, position):
		self._position = list(position)
		self.rect.center = tuple(self._position)
		return True

	def x(self):
		return self._position[0]

	def y(self):
		return self._position[1]
	

	def move_towards(self, position):
		
		direction = [position[0] - self.x() , position[1] - self.y()]
		normalize(direction)

		MAGNITUDE = 3

		self.velocity = [direction[0]*MAGNITUDE, direction[1]*MAGNITUDE]

		return None

  	def off_screen(self): 
		off_right_left = self.x() < 0 or self.x() > window_width 
		off_up_down = self.y() < 0 or self.y() > window_height 
		if off_right_left or off_up_down: 
			return True 
		else: 
			return False 

	def update(self): 
		# allsprites.update() runs this function 
		# allsprites.draw() will blit the self.image surface to the screen 

		self._position[0] += self.velocity[0]
		self._position[1] += self.velocity[1]

		if self.off_screen(): 
			self.kill() 
		else: 
			self.rect.center = tuple(self._position)

	def fling(self, start_pos, end_pos):
		if self.type == 'infection':
			return False
		if self.type == 'virus':
			return False
		if self.type == 'cell':
			self.kill()
			return False

		self.flung = True
		vel = [end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]]

		MAGNITUDE = 0.02

		self.velocity = [ self.velocity[0] + vel[0] * MAGNITUDE, self.velocity[1] + vel[1] * MAGNITUDE]

	def drag(self):
		if self.type == 'virus':
			return False
		if self.type == 'cell':
			self.kill()
			return False
		mpos = pygame.mouse.get_pos()
		self.set_position(mpos)

	def get_distance_to(self, point): 
		dx = point[0] - (self.x())
		dy = point[1] - (self.y())
		return math.sqrt(dx**2 + dy**2)  

	def mouse_over(self):  
		mpos = pygame.mouse.get_pos() 
		radius = self.radius
		if self.type == 'antibody':
			radius *= 2.5
		if self.get_distance_to(mpos) < radius:
			return True 
		else: 
			return False      

	def __str__(self):
		return "Type: %s position: %s " % (self.type, self.get_position())

	def make_virus(self):
		self.type = 'virus'

		self.image = pygame.Surface((self.radius*2, self.radius*2)) 
		self.image = self.image.convert_alpha() 
		self.image.fill((0,0,0,0)); 
		pygame.draw.circle(self.image, dark_green, (self.radius, self.radius), self.radius) 



# Returns the number of antibodies on screen.
def num_antibodies(allsprites):
	count = 0
	for sprite in allsprites:
		if sprite.type == 'antibody':
			count += 1

	return count

def antibodies_far_enough(allsprites, num_converted):
	widths = []
	for sprite in allsprites:
		# if the y position is 100 pixels away from the right of the screen.
		if sprite.type == 'antibody' and not sprite.flung:
			widths.append(window_width - sprite.x())
	if not widths:
		return True
	if min(widths) < window_width/max(num_converted, NUM_ANTIBODIES):
		return False
	return True

def num_cells(allsprites):
	count = 0
	for sprite in allsprites:
		if sprite.type == 'cell':
			count += 1

	return count


def cells_far_enough(allsprites):
	widths = []
	for sprite in allsprites:
		# if the y position is 100 pixels away from the right of the screen.
		if sprite.type == 'cell':
			widths.append(window_width - sprite.x())
	if not widths:
		return True
	if min(widths) < window_width/NUM_CELLS:
		return False
	return True

def find_eligible_cell(virus, allsprites):
	cells = []
	for sprite in allsprites:
		if sprite.type == 'cell' and sprite.locked.has(virus):
			return sprite
		if sprite.type == 'cell' and sprite.x() < 5 * window_width / 6 and len(sprite.locked.sprites()) == 0:
			cells.append(sprite)

	if not cells:
		return None

	closest = min(cells, key=lambda cell: cell.x())

	closest.locked.add(virus)

	return closest

def game_over():
	while 1:
		i = 1

def num_flung(viruses):
	count = 0
	for v in viruses:
		try:
			if v.flung_towards_infection or v.flung:
				count += 1
		except:
			pass
	return count

def main(): 
	"""this function is called when the program starts. 
	   it initializes everything it needs, then runs in 
	   a loop until the function returns.""" 
#Initialize Everything 
	pygame.init() 
	screen = pygame.display.set_mode((window_width, window_height)) 
	pygame.display.set_caption('Test Game') 

#Create The Backgound 
	background = pygame.Surface(screen.get_size()) 
	background = background.convert() 
	background.fill(blood_red) 

#Display The Background 
	screen.blit(background, (0, 0)) 
	pygame.display.flip() 

#Clock and object list 
	clock = pygame.time.Clock() 
	allsprites = pygame.sprite.RenderPlain() 

	viruses = pygame.sprite.RenderPlain()


	virus = Ball(dark_green, [50, window_height/2])
	virus.type = 'virus'

	viruses.add(virus)

	cells = pygame.sprite.RenderPlain()

	allsprites.add(virus)

	antibodies = pygame.sprite.RenderPlain()

	infection = Ball(black, [20, window_height/2])
	infection.set_radius(40)
	infection.type = 'infection'
	allsprites.add(infection)

	num_converted = 0

	score = 0

	font = pygame.font.Font(None, 30)

	big_font = pygame.font.Font(None, 50)

	difficulty = 0


#Main Loop 
	while 1: 
		clock.tick(60)  #  SAVES CPU! 

	#Handle Input Events 
		for event in pygame.event.get(): 
			if event.type == QUIT: 
				return 
			elif event.type == MOUSEBUTTONDOWN: 
				for sprite in allsprites: 
					if sprite.mouse_over(): 
						if not sprite.dragged:
							sprite.drag_start = pygame.mouse.get_pos()
						sprite.dragged = True
			elif event.type == MOUSEBUTTONUP:
				for sprite in allsprites:
					if sprite.dragged:
						sprite.fling(sprite.drag_start, pygame.mouse.get_pos())
						sprite.dragged = False

			if num_antibodies(allsprites) < max(difficulty, NUM_ANTIBODIES) and antibodies_far_enough(allsprites, num_converted):
				antibody = Ball(blue, [window_width - 20, random.randint(30, window_height-30)])
				antibody.type = 'antibody'
				antibody.move_randomly()
				antibodies.add(antibody)
				allsprites.add(antibody)

			if num_cells(allsprites) < NUM_CELLS and cells_far_enough(allsprites):
				cell = Ball(gray, [window_width - 20, random.randint(30, window_height-30)])
				cell.type = 'cell'
				cell.move_horizontally()
				allsprites.add(cell)
				cells.add(cell)

		for v in viruses:
			if v.color == black:
				continue	
			# find the cell to go to, and make virus go to cell.
			eligible_cell = find_eligible_cell(v, allsprites)
			if not eligible_cell:
				if len(viruses.sprites()) - num_flung(viruses) > 5:
					v.color = black
					v.set_radius(v.radius)
					v.flung_towards_infection = True
					v.move_towards(infection.get_position())
				elif not v.flung and (v.x() > window_width / 2 or v.x() < window_width / 5):
					v.oscillate()
					v.flung = False
			else:
				v.move_towards(eligible_cell.get_position())


		collisions =  pygame.sprite.groupcollide(cells, viruses, False, False)

		for cell in collisions.keys():
			cell.make_virus()
			viruses.add(cell)
			cells.remove(cell)
			difficulty += 1
			num_converted += 1

		collisions = pygame.sprite.groupcollide(antibodies, viruses, True, True)

		for antibody in collisions.keys():
			difficulty -= 1

		if num_converted > 5:
			collisions = pygame.sprite.spritecollide(infection, viruses, True)

			for virus in collisions:
				infection.set_radius(int(infection.radius*1.2))
				score += 1

		collisions = pygame.sprite.spritecollide(infection, antibodies, True)
		for antibody in collisions:
			infection.set_radius(int(infection.radius*10/12))
			score -= 1
		
		text = font.render("Score: %d" % (score), 1, black)
		textpos = text.get_rect(center = (50, 50))

		conv_text = font.render("Cells Infected: %d" % (num_converted), 1, black if num_converted < 10 else dark_green)
		conv_textpos = text.get_rect(center = (window_width-150, 50))
		background.fill(blood_red) 
		background.blit(text, textpos)
		background.blit(conv_text, conv_textpos)

		if score >= 5:
			text = big_font.render("You have successfully infected the host. Congratulations", 1, black)
			textpos = text.get_rect(center=(window_width/2, window_height/2))

			background.blit(text, textpos)
			screen.blit(background, (0, 0)) 
			allsprites.draw(screen) 
			pygame.display.flip() 
			game_over()


		elif len(viruses) <= 0 or score < 0:
			text = big_font.render("Your infection was wiped out. Restart the game to try again", 1, black)
			textpos = text.get_rect(center=(window_width/2, window_height/2))

			background.blit(text, textpos)
			screen.blit(background, (0, 0)) 
			allsprites.draw(screen) 
			pygame.display.flip() 
			game_over()






		allsprites.update() 

	#Draw Everything 
		screen.blit(background, (0, 0)) 
		allsprites.draw(screen) 
		pygame.display.flip() 

#Game Over 


#this calls the 'main' function when this script is executed 
if __name__ == '__main__': main()  
