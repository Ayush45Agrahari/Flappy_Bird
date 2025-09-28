import pygame
#initialize pygame
pygame.init()
#create screen 
screen=pygame.display.set_mode((1550,790)) 
#title and icon
pygame.display.set_caption("Hitman 45")
icon=pygame.image.load('rt.webp')
pygame.display.set_icon(icon)
#ground 
groundimg=pygame.image.load('match.webp')
groundx=0
groundy=0

def ground():
    screen.blit(groundimg, (groundx, groundy))

#game loop
running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    #RGB -Red, Green, Blue
    screen.fill((255,155,0))
    ground()
    pygame.display.update()