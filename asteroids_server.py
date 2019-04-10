import pygame
import sys
import random
import socket
import pickle
from asteroids_helper import *
		
class Entity(object):

	def __init__(self, sprite, position, angle, speed):
		self.sprite = sprite
		self.position = list(position[:])
		self.angle = angle
		self.speed = speed
		self.direction = [0, 0]
		self.direction[0] = math.sin(-math.radians(self.angle))
		self.direction[1] = -math.cos(math.radians(self.angle))
		
	def render(self, screen):
		render_centered(self.sprite, screen, self.position)
		
	def update(self):
		self.position[0] += self.direction[0]*self.speed
		self.position[1] += self.direction[1]*self.speed
		if self.position[0] < 0 or self.position[0] > WORLD_WIDTH:
			self.position[0] %= WORLD_WIDTH
		if self.position[1] < 0 or self.position[1] > WORLD_HEIGHT:
			self.position[1] %= WORLD_HEIGHT
		
	def size(self):
		return max(self.sprite.get_height(), self.sprite.get_width())
		
	def radius(self):
		return self.sprite.get_width() / 2
	
	
class Player(Entity):
	
	def __init__(self, position):
		super(Player, self).__init__(load_sprite('spaceship-off.png'), position, 0, 0)
		self.cooldown = 0
		
	def render(self, screen):
		new_sprite, rect = rotate_center(self.sprite, self.sprite.get_rect(), self.angle)
		render_centered(new_sprite, screen, self.position)
		
	def update(self):
		self.direction[0] = math.sin(-math.radians(self.angle))
		self.direction[1] = -math.cos(math.radians(self.angle))
		super(Player, self).update()
		if self.cooldown > 0:
			self.cooldown -= 1
			
	def fire(self):
		if self.cooldown == 0:
			self.cooldown = 10
			return True
		return False
	

class Missile(Entity):

	def __init__(self, position, angle, speed):
		super(Missile, self).__init__(load_sprite('missile.png'), position, angle, speed + 15)
		self.sprite, rect = rotate_center(self.sprite, self.sprite.get_rect(), self.angle)
		self.position[0] += math.sin(-math.radians(self.angle))*50
		self.position[1] -= math.cos(math.radians(self.angle))*50
		self.lifetime = 15
	
	def update(self):
		super(Missile, self).update()
		self.lifetime -= 1
	
	
class Asteroid(Entity):
	
	def __init__(self, position):
		super(Asteroid, self).__init__(load_sprite('rock-normal.png'), position, random.randint(0, 360), random.uniform(2, 6))
		self.sprite, rect = rotate_center(self.sprite, self.sprite.get_rect(), self.angle)
		
	
class Game(object):

	REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT+3)
	
	def __init__(self):
		pygame.mixer.init()
		pygame.mixer.pre_init(44100, -16, 2, 2048)
		pygame.init()
		
		self.width = WORLD_WIDTH
		self.height = WORLD_HEIGHT
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.bg_color = 0, 0, 0
		self.FPS = 30
		self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server.bind(('localhost', 12000))
		self.connected = []
		self.dead = []
		
		pygame.time.set_timer(self.REFRESH, 1000 // self.FPS)
		
	def initialize(self):
		self.players = []
		self.asteroids = []
		self.missiles = []
		
		###################
		#self.players.append(Player((self.width//2, self.height//2)))
		self.asteroids.append(Asteroid((0, 0)))
		#self.asteroids.append(Asteroid((0, 0)))
		#self.asteroids.append(Asteroid((0, 0)))
		###################
		
	def update(self):
		for missile in self.missiles:
			missile.update()
			for asteroid in self.asteroids:
				if distance(missile.position, asteroid.position) < 50:
					self.asteroids.remove(asteroid)
					self.missiles.remove(missile)
			if missile.lifetime <= 0:
				self.missiles.remove(missile)
		for asteroid in self.asteroids:
			asteroid.update()
		for player in self.players:
			player.update()
			for asteroid in self.asteroids:
				if distance(player.position, asteroid.position) < 60:
					self.asteroids.remove(asteroid)
					#self.dead.append(self.connected[self.players.index(player)])
					del self.connected[self.players.index(player)]
					self.players.remove(player)
			for missile in self.missiles:
				if distance(player.position, missile.position) < 15:
					self.missiles.remove(missile)
					#self.dead.append(self.connected[self.players.index(player)])
					del self.connected[self.players.index(player)]
					self.players.remove(player)
		
	def render(self):
		self.screen.fill(self.bg_color)
		for missile in self.missiles:
			missile.render(self.screen)
		for asteroid in self.asteroids:
			asteroid.render(self.screen)
		for player in self.players:
			player.render(self.screen)
		pygame.display.flip()
		
	def payload(self):
		payload = []
		for player in self.players:
			payload.append(('P', player.position, player.angle))
		for asteroid in self.asteroids:
			payload.append(('A', asteroid.position, asteroid.angle))
		for missile in self.missiles:
			payload.append(('M', missile.position, missile.angle))
		return pickle.dumps(payload) 
		
	def run(self):
		self.initialize()
		running = True
		while running:
			event = pygame.event.wait()
		
			data, addr = self.server.recvfrom(1024)
			data = data.decode() if data else ''
			if addr and addr not in self.connected and addr not in self.dead:
				self.connected.append(addr)
				self.players.append(Player((self.width//2, self.height//2)))
			i = self.connected.index(addr) if addr else 0
			
			if event.type == pygame.QUIT:
				running = False
				
			elif event.type == Game.REFRESH:
				if 'd' in data:
					self.players[i].angle -= 10
					self.players[i].angle %= 360
				if 'a' in data:
					self.players[i].angle += 10
					self.players[i].angle %= 360
				if 'w' in data:
					if self.players[i].speed < 15:
						self.players[i].speed += 1
				else:
					if self.players[i].speed > 0:
						self.players[i].speed -= 1
				if 's' in data:
					if self.players[i].fire():
						self.missiles.append(Missile(self.players[i].position, self.players[i].angle, self.players[i].speed))
				
			self.update()
			self.render()
			self.server.sendto(self.payload(), addr)
			if len(self.players) == 0:
				running = False
		
		
Game().run()
pygame.quit()
sys.exit()