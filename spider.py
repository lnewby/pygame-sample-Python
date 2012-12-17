#!/usr/bin/env python

#Import Modules
import os, time, pygame
from pygame.locals import *
from pygame.font import *
SCREENRECT     = Rect(0, 0, 640, 480)

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'


#functions to create our resources
def load_image(name, colorkey=None):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', fullname
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()
	
def load_bg_image(file):
	"loads an image, prepares it for play"
	file = os.path.join('data', file)
	try:
		surface = pygame.image.load(file)
	except pygame.error:
		raise SystemExit, 'Could not load image "%s" %s'%(file, pygame.get_error())
	return surface.convert()

def load_sound(name):
	class NoneSound:
		def play(self): pass
	if not pygame.mixer or not pygame.mixer.get_init():
		return NoneSound()
	fullname = os.path.join('data', name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print 'Cannot load sound:', fullname
		raise SystemExit, message
	return sound
		

#classes for our game objects
class Menu:
	def __init__(self, position):
		self.font = pygame.font.Font(None, 36)
		self.position = position
	
	def display(self):
		self.restart = self.font.render('Restart - Press (E)',1, (150,150,255), (26,62,30))
		self.restartpos = self.restart.get_rect(centerx=self.position, top=200)
		self.start = self.font.render('Start - Press (S)',1, (255,255,255), (26,62,30))
		self.startpos = self.start.get_rect(centerx=self.position, top=150)
		self.quit = self.font.render('Quit - Press (Q)',1, (150,150,255), (26,62,30))
		self.quitpos = self.quit.get_rect(centerx=self.position, top=250)

class MiniOnScreenMenu:
	def __init__(self, position):
		self.font = pygame.font.Font(None, 16)
		self.position = position
		
	def display(self):
		self.menu = self.font.render('(E) Restart    (Q) Quit',1, (255,255,255))
		self.menupos = self.menu.get_rect(left=465, top=465)

class PrintScore:
	def __init__(self, score):
		#call Print Score initializer
		self.font = pygame.font.Font(None, 30)
		self.b = 'Score: %d' % score
		self.text = self.font.render(self.b, 1, (255, 255, 255))
		self.textpos = self.text.get_rect(left=510)
	
	def update(self, score):
		self.b = 'Score: %d' % score
		self.text = self.font.render(self.b, 1, (255, 255, 255))
		self.textpos = self.text.get_rect(left=510)

class GameOverText:
	def __init__(self, position):
		self.font = pygame.font.Font(None, 60)
		self.position = position
		
	def display(self):
		self.text = self.font.render('GAME OVER',1, (255,242,0) ,(26,62,30))
		self.textpos = self.text.get_rect(centerx=self.position, top=100)
		
		
class GameOverMenu:
	def __init__(self, position):
		self.font = pygame.font.Font(None, 30)
		self.position = position
		
	def display(self, score):
		a = 'Score: %d' % score
		self.score = self.font.render(a,1, (150,150,255) ,(26,62,30))
		self.scorepos = self.score.get_rect(centerx=self.position, top=150)
		self.retry = self.font.render('Replay - Press (R)',1, (255,255,255), (26,62,30))
		self.retrypos = self.retry.get_rect(centerx=self.position, top=200)
		self.quit = self.font.render('Quit - Press (Q)',1, (150,150,255) ,(26,62,30))
		self.quitpos = self.quit.get_rect(centerx=self.position, top=250)
		
class CountDownTimer:
	def __init__(self, duration, current_time, position):
		#call CountDownTimer initializer
		self.d = duration
		self.t = current_time
		self.font = pygame.font.Font(None, 24)
		self.b = 'Time: %d' % duration
		self.text = self.font.render(self.b, 1, (10, 10, 10))
		self.textpos = self.text.get_rect(centerx=50)
		self.start = False
		self.position = position
	
	def update(self):
		_t = time.localtime()
		if _t[5] != self.t[5]:
			self.d = self.d - 1
			self.b = 'Time: %d' % self.d
			self.text = self.font.render(self.b, 1, (255, 255, 255))
			self.textpos = self.text.get_rect(centerx = self.position, top=10)
		self.t = _t
		
	def set(self, minutes):
		self.d = minutes
		if minutes == 0:
			self.start = False;
		else:
			self.start = True;
		
	def timeleft(self):
		return self.d
		

class Newspaper(pygame.sprite.Sprite):
	"""moves a clenched Newspaper on the screen, following the mouse"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = load_image('newspaper.bmp', -1)
		self.punching = 0

	def update(self):
		"move the Newspaper based on the mouse position"
		pos = pygame.mouse.get_pos()
		self.rect.midtop = pos
		if self.punching:
			self.rect.move_ip(5, 10)

	def punch(self, target):
		"returns true if the Newspaper collides with the target"
		if not self.punching:
			self.punching = 1
			hitbox = self.rect.inflate(-5, -5)
			return hitbox.colliderect(target.rect)

	def unpunch(self):
		"called to pull the Newspaper back"
		self.punching = 0
		

class BlackWidow(pygame.sprite.Sprite):
	"""moves a spider critter across the screen. it can spin the
	   spider when it is punched."""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.image, self.rect = load_image('black-widow.bmp', -1)
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rect.topleft = 250, 10
		self.move = 9
		self.dizzy = 0
		self.hits = 0
		self.score = 0;

	def update(self):
		"walk or spin, depending on the spider state"
		if self.dizzy:
			self._spin()
		else:
			self._walk()
	
	def update_score(self):
		self.score+=1
		if self.hits == 5:
			hits=0
		
	def _walk(self):
		"move the spider across the screen, and turn at the ends"
		newpos = self.rect.move((self.move, 0))
		if self.rect.left < self.area.left or \
			self.rect.right > self.area.right:
			self.move = -self.move
			newpos = self.rect.move((self.move, 0))
			self.image = pygame.transform.flip(self.image, 1, 0)
		self.rect = newpos

	def _spin(self):
		"spin the spider image"
		center = self.rect.center
		self.dizzy = self.dizzy + 12
		if self.dizzy >= 360:
			self.dizzy = 0
			self.image = self.original
		else:
			rotate = pygame.transform.rotate
			self.image = rotate(self.original, self.dizzy)
		self.rect = self.image.get_rect(center=center)
		
	def punched(self):
		"this will cause the spider to start spinning"
		if not self.dizzy:
			self.dizzy = 1
			self.original = self.image
			self.hits+=1
			self.update_score()
			

		
def main():
	"""this function is called when the program starts.
	   it initializes everything it needs, then runs in
	   a loop until the function returns."""
#Initialize Everything
	pygame.init()
	screen = pygame.display.set_mode((640, 480))
	pygame.display.set_caption('Orchid with Arachnophobia')
	pygame.mouse.set_visible(0)

#Create the background, tile the bgd image
	bg_tile = load_bg_image('orchid_face.bmp')
	background = pygame.Surface(SCREENRECT.size)
	for x in range(0, 640, bg_tile.get_width()):
		background.blit(bg_tile, (x, 0))

#Display Background
	screen.blit(background, (0,0))
	pygame.display.flip()
	
#Prepare Game Objects
	game_over = True
	clock = pygame.time.Clock()
	whiff_sound = load_sound('punch.wav')
	punch_sound = load_sound('smash.wav')
	spider = BlackWidow()
	newspaper = Newspaper()
	atimer = CountDownTimer(60, time.localtime(), background.get_width()/2)
	score = PrintScore(0)
	menu = Menu(background.get_width()/2)
	mini_on_screen_menu = MiniOnScreenMenu(background.get_width()/2)
	gameover = GameOverText(background.get_width()/2)
	game_over_menu = GameOverMenu(background.get_width()/2)
	allsprites = pygame.sprite.RenderPlain((newspaper, spider))

#Main Loop
	while 1:
		clock.tick(60)

	#Handle Input Events
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit();
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				pygame.quit();
			elif event.type == KEYDOWN and event.key == K_q:
				if atimer.start:
					atimer.set(0)
				else:
					pygame.quit();
			elif event.type == KEYDOWN and (event.key == K_s):
			   #start the game by pressing the 's' key
				if (not atimer.start) & (not game_over):
					atimer.set(31)
			elif event.type == KEYDOWN and (event.key == K_e):
			   #restart the game while playing by pressing the 'e' key
				if atimer.start & (not game_over):
					atimer.set(31)
			elif event.type == KEYDOWN and (event.key == K_r):
			   #retry once the current game ends by pressing the 'r' key
				if atimer.start & game_over:
					game_over = False
					atimer.set(31)
			elif event.type == MOUSEBUTTONDOWN:
				if newspaper.punch(spider):
					punch_sound.play() #punch
					spider.punched()
				else:
					whiff_sound.play() #miss
			elif event.type == MOUSEBUTTONUP:
				newspaper.unpunch()
		
		if atimer.start:
			game_over = False
			if atimer.timeleft() > 0:
			   #Setup the next game so user can play
				allsprites.clear(screen, background)
				allsprites.update()
				atimer.update()
				score.update(spider.score)
				mini_on_screen_menu.display()
			   #Draw Everything
				screen.blit(background, (0, 0))
				screen.blit(atimer.text, atimer.textpos)
				screen.blit(score.text, score.textpos)
				screen.blit(mini_on_screen_menu.menu, mini_on_screen_menu.menupos)
				allsprites.draw(screen)
				pygame.display.flip()
			else:
			   #Game Over. Time ran out. Display the score and menu options
				game_over = True
				spider.score = 0
				spider.hits = 0
				screen.blit(background, (0, 0))
				allsprites.clear(screen, background)
				gameover.display()
				game_over_menu.display(spider.score)
			   #Draw Menu Options
				screen.blit(gameover.text, gameover.textpos)
				screen.blit(game_over_menu.score, game_over_menu.scorepos)
				screen.blit(game_over_menu.retry, game_over_menu.retrypos)
				screen.blit(game_over_menu.quit, game_over_menu.quitpos)
				pygame.display.flip()
		else:
		   ##Display the Start menu at the start of the game
			game_over = False
			spider.score=0
			spider.hits=0
			atimer.start = False
			screen.blit(background, (0, 0))
			allsprites.clear(screen, background)
			menu.display()
		   #Draw Key Menu Options
			screen.blit(menu.start, menu.startpos)
			screen.blit(menu.restart, menu.restartpos)
			screen.blit(menu.quit, menu.quitpos)
			pygame.display.flip()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
