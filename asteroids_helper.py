import pygame
import os
import math

WORLD_WIDTH = 1200
WORLD_HEIGHT = 600

def render_centered(surface1, surface2, position):
    rect = surface1.get_rect()
    rect = rect.move(position[0] - rect.width // 2, position[1] - rect.height // 2)
    surface2.blit(surface1, rect)
	
def render_text(text, surface, position):
	font = pygame.font.Font('freesansbold.ttf', 24)
	textSurf = font.render(text, True, (255, 255, 255))
	textRect = textSurf.get_rect()
	textRect.center = (position[0], position[1] - 50)
	surface.blit(textSurf, textRect)
    
def load_sprite(filename):
    return pygame.image.load(os.path.join('images', filename)).convert_alpha()
    
def rotate_center(sprite, rect, angle):
    rotate_sprite = pygame.transform.rotate(sprite, angle)
    rotate_rect = rotate_sprite.get_rect(center=rect.center)
    return rotate_sprite, rotate_rect
    
def distance(p, q):
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)