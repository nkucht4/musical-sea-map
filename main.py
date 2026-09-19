import pygame

from map import renderer

pygame.init()
screen = pygame.display.set_mode((500,500))
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    renderer.render()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()