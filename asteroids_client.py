import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'

import sys
import pickle
import socket
import pygame
#from gpiozero import InputDevice
from asteroids_helper import *

class Game(object):

	REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT+3)

	def __init__(self, ip, name):
		pygame.init()
		self.ip = ip
		self.name = name

		self.width = WORLD_WIDTH
		self.height = WORLD_HEIGHT
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.bg_color = 0, 0, 0
		self.FPS = 30
		self.entities = []
		self.sprites = (load_sprite('spaceship-off.png'), load_sprite('rock-normal.png'), load_sprite('missile.png'))
		self.is_alive = True

		self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		pygame.time.set_timer(self.REFRESH, 1000 // self.FPS)

	def render_game_over(self):
		self.screen.fill(self.bg_color)
		for entity in self.entities:
			self.render_entity(self.screen, entity)

		text = pygame.font.Font(None, 36).render("You Were Eliminated!", True, (255, 255, 255))
		text_rect = text.get_rect()
		text_x = self.screen.get_width() / 2 - text_rect.width / 2
		text_y = self.screen.get_height() / 2 - text_rect.height / 2
		self.screen.blit(text, [text_x, text_y])

		pygame.display.flip()

	def render(self):
		self.screen.fill(self.bg_color)
		for entity in self.entities:
			self.render_entity(self.screen, entity)
		pygame.display.flip()

	def render_entity(self, screen, entity):
		i = 2 if entity[0] == 'M' else 1 if entity[0] == 'A' else 0

		if i == 0:
			if entity[3] == self.name:
				self.is_alive = entity[4]
			if entity[4]:
				render_text(entity[3], screen, entity[1])
				new_sprite, rect = rotate_center(self.sprites[i], self.sprites[i].get_rect(), entity[2])
				render_centered(new_sprite, screen, entity[1])
			return

		new_sprite, rect = rotate_center(self.sprites[i], self.sprites[i].get_rect(), entity[2])
		render_centered(new_sprite, screen, entity[1])


	def run(self):
#		UP = InputDevice(17)
#		RIGHT = InputDevice(27)
#		LEFT = InputDevice(22)
#		BUTTON = InputDevice(23)
		running = True
		while running:
			event = pygame.event.wait()

			if event.type == pygame.QUIT:
				running = False

			elif event.type == Game.REFRESH:
				if self.is_alive:
					keys = pygame.key.get_pressed()
					keys_payload = ''

					if keys[pygame.K_RIGHT] or keys[pygame.K_d]: keys_payload += 'd'
					if keys[pygame.K_LEFT] or keys[pygame.K_a]: keys_payload += 'a'
					if keys[pygame.K_UP] or keys[pygame.K_w]: keys_payload += 'w'
					if keys[pygame.K_SPACE]: keys_payload += 's'

					keys_payload += '?'
					keys_payload += self.name

					self.client.sendto(keys_payload.encode(), (self.ip, 12000))
					data, addr = self.client.recvfrom(1024)
					if data: self.entities = pickle.loads(data)

					self.render()
					continue
				self.render_game_over()

if __name__ == "__main__":
	try:
		ip = sys.argv[1]
		user = sys.argv[2]

		asteroids_game = Game(sys.argv[1],sys.argv[2])
		asteroids_game.run()
	except KeyboardInterrupt:
		pygame.quit()
		sys.exit()
	except IndexError:
		print("\n\n Error:  Please provide arguments: server IP and username")
		sys.exit()
	except:
		raise

	pygame.quit()
	sys.exit()
