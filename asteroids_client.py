import sys
import pickle
import socket
import pygame
from gpiozero import InputDevice
from asteroids_helper import *


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
        self.entities = []
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sprites = (load_sprite('spaceship-off.png'), load_sprite('rock-normal.png'), load_sprite('missile.png'))
        
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
        
    def run(self):
        #UP = InputDevice(17)
        #RIGHT = InputDevice(27)
        #LEFT = InputDevice(22)
        #BUTTON = InputDevice(23)
        
        running = True
        while running:
            event = pygame.event.wait()
            
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == Game.REFRESH:
                keys = pygame.key.get_pressed()
                keys_payload = ''
                #if RIGHT.is_active: keys_payload += 'd'
                #if LEFT.is_active: keys_payload += 'a'
                #if UP.is_active: keys_payload += 'w'
                #if BUTTON.is_active: keys_payload += 's'
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: keys_payload += 'd'
                if keys[pygame.K_LEFT] or keys[pygame.K_a]: keys_payload += 'a'
                if keys[pygame.K_UP] or keys[pygame.K_w]: keys_payload += 'w'
                if keys[pygame.K_SPACE]: keys_payload += 's'
                
                self.client.sendto(keys_payload.encode(), (sys.argv[1], 12000))
                data, addr = self.client.recvfrom(1024)
                if data: self.entities = pickle.loads(data)
            
            self.render()
    
Game().run()
pygame.quit()
sys.exit()   