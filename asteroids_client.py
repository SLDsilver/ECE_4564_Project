import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'

import sys
import pickle
import socket
import pygame
from gpiozero import InputDevice
from asteroids_helper import *

class Game(object):

	REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT+3)

	def __init__(self):
		pygame.init()

		self.width = WORLD_WIDTH
		self.height = WORLD_HEIGHT
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.bg_color = 0, 0, 0
		self.FPS = 60
		self.entities = []
		self.sprites = (load_sprite('spaceship-off.png'), load_sprite('rock-normal.png'), load_sprite('missile.png'))

		self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		pygame.time.set_timer(self.REFRESH, 1000 // self.FPS)

	def render(self):
		self.screen.fill(self.bg_color)
		for entity in self.entities:
			self.render_entity(self.screen, entity)
		pygame.display.flip()

	def render_entity(self, screen, entity):
		i = 2 if entity[0] == 'M' else 1 if entity[0] == 'A' else 0
		new_sprite, rect = rotate_center(self.sprites[i], self.sprites[i].get_rect(), entity[2])
		render_centered(new_sprite, screen, entity[1])
		if i == 0: render_text(entity[3], screen, entity[1])

	#def render_gameover():


	def run(self):
		running = True
		while running:
			event = pygame.event.wait()

			if event.type == pygame.QUIT:
				running = False

			elif event.type == Game.REFRESH:
				keys = pygame.key.get_pressed()
				keys_payload = ''

				if keys[pygame.K_RIGHT] or keys[pygame.K_d]: keys_payload += 'd'
				if keys[pygame.K_LEFT] or keys[pygame.K_a]: keys_payload += 'a'
				if keys[pygame.K_UP] or keys[pygame.K_w]: keys_payload += 'w'
				if keys[pygame.K_SPACE]: keys_payload += 's'

				keys_payload += '?'
				keys_payload += sys.argv[2]

				self.client.sendto(keys_payload.encode(), (sys.argv[1], 12000))
				data, addr = self.client.recvfrom(1024)
				if data: self.entities = pickle.loads(data)

			self.render()

Game().run()
pygame.quit()
sys.exit()
