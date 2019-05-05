import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'

import pygame
import sys
import random
import socket
import pickle
from upload_data import send_game
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

	def __init__(self, position, name):
		super(Player, self).__init__(load_sprite('spaceship-off.png'), position, 0, 0)
		self.cooldown = 0
		self.name = name

		self.shots = 0
		self.elims = 0
		self.destroys = 0
		self.place = 0

		self.alive = True

	def render(self, screen):
		new_sprite, rect = rotate_center(self.sprite, self.sprite.get_rect(), self.angle)
		render_centered(new_sprite, screen, self.position)
		render_text(self.name, screen, self.position)

	def update(self):
		self.direction[0] = math.sin(-math.radians(self.angle))
		self.direction[1] = -math.cos(math.radians(self.angle))
		super(Player, self).update()
		if self.cooldown > 0:
			self.cooldown -= 1

	def fire(self):
		if self.cooldown == 0:
			self.shots += 1
			self.cooldown = 10
			return True
		return False


class Missile(Entity):

	def __init__(self, position, angle, speed, name):
		super(Missile, self).__init__(load_sprite('missile.png'), position, angle, speed + 20)
		self.sprite, rect = rotate_center(self.sprite, self.sprite.get_rect(), self.angle)
		self.position[0] += math.sin(-math.radians(self.angle))*50
		self.position[1] -= math.cos(math.radians(self.angle))*50
		self.lifetime = 25
		self.name = name

	def update(self):
		super(Missile, self).update()
		self.lifetime -= 1


class Asteroid(Entity):

	def __init__(self, position, size):
		file = 'rock-normal.png'
		super(Asteroid, self).__init__(load_sprite(file), position, random.randint(0, 360), random.uniform(4, 8))
		self.sprite, self.rect = rotate_center(self.sprite, self.sprite.get_rect(), self.angle)

class Game(object):

	REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT+3)

	def __init__(self,webserver):
		pygame.init()

		self.webserver = webserver

		self.width = WORLD_WIDTH
		self.height = WORLD_HEIGHT
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.bg_color = 0, 0, 0
		self.FPS = 30
		self.connected = []
		self.dead = []

		self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server.bind(('0.0.0.0', 12000))

		pygame.time.set_timer(self.REFRESH, 1000 // self.FPS)

	def initialize(self):
		self.players = []
		self.asteroids = []
		self.missiles = []

	def get_player(self, name):
		for player in self.players:
			if player.name == name:
				return player

	def kill_player(self, player, killed_by):
		#Send Data to Webserver
		data = dict()
		data['player'] = player.name
		data['Shots_Fired'] = player.shots
		data['Eliminations'] = player.elims
		data['Asteroids_Destroyed'] = player.destroys
		data['Place'] = player.place
		data['Eliminated_By'] = killed_by
		send_game(self.webserver,data)
		#Kill player
		self.dead.append(self.connected[self.players.index(player)])
		player.alive = False


	def update(self):
		for missile in self.missiles:
			missile.update()
			for asteroid in self.asteroids:
				if distance(missile.position, asteroid.position) < 60:
					self.get_player(missile.name).destroys += 1
					self.asteroids.remove(asteroid)
					try: self.missiles.remove(missile)
					except: continue
			if missile.lifetime <= 0:
				try: self.missiles.remove(missile)
				except: continue
		if len(self.asteroids) < 5:
			for i in range(5 - len(self.asteroids)):
				self.asteroids.append(Asteroid((0, 0), 2))
		for asteroid in self.asteroids:
			asteroid.update()
		for player in self.players:
			if not player.alive:
				continue

			player.update()
			player.place = len(self.players)
			for asteroid in self.asteroids:
				if distance(player.position, asteroid.position) < 60:
					self.asteroids.remove(asteroid)
					self.kill_player(player,"Asteroid")
					return

			for missile in self.missiles:
				if distance(player.position, missile.position) < 20:
					self.get_player(missile.name).elims += 1
					self.missiles.remove(missile)
					self.kill_player(player,missle.name)
					return

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
				payload.append(('P', player.position, player.angle, player.name, player.alive))
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
			data = data.decode().split('?') if data else ('', '')
			if addr and addr not in self.connected and addr not in self.dead:
				self.connected.append(addr)
				self.players.append(Player((self.width/2, self.height/2), data[1]))

			if addr and addr not in self.dead:
				i = self.connected.index(addr) if addr else 0

				if event.type == pygame.QUIT:
					running = False

				elif event.type == Game.REFRESH:
					if 'd' in data[0]:
						self.players[i].angle -= 10
						self.players[i].angle %= 360
					if 'a' in data[0]:
						self.players[i].angle += 10
						self.players[i].angle %= 360
					if 'w' in data[0]:
						if self.players[i].speed < 15:
							self.players[i].speed += 1
					else:
						if self.players[i].speed > 0:
							self.players[i].speed -= 1
					if 's' in data[0]:
						if self.players[i].fire():
							self.missiles.append(Missile(self.players[i].position, self.players[i].angle, self.players[i].speed, self.players[i].name))

			self.update()
			#self.render()
			self.server.sendto(self.payload(), addr)
			if len(self.players) == 0:
				running = False


if __name__ == "__main__":
	try:
		ip = sys.argv[1]

		Game(ip).run()
	except KeyboardInterrupt:
		pygame.quit()
		sys.exit()
	except IndexError:
		print("\n\n Error:  Please provide arguments: webserver IP")
		sys.exit()
	except:
		raise
		sys.exit()

	pygame.quit()
	sys.exit()
