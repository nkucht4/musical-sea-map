import pygame
from map import renderer
from fish.fish import load_and_place_fishes
from notes.audio import DynamicAudioEngine

# pygame.init()
# screen = pygame.display.set_mode((500,500))
# clock = pygame.time.Clock()
# running = True

# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     renderer.render()

#     pygame.display.flip()

#     clock.tick(60)

# pygame.quit()

pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Ocean Map & DNA Soundscapes")
clock = pygame.time.Clock()

audio_engine = DynamicAudioEngine()
placed_fishes = load_and_place_fishes("fish/fishes.csv", renderer.TILES)
fish_map = {f.position: f for f in placed_fishes}

running = True
active_fish_name = "None"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    renderer.render()

    mx, my = pygame.mouse.get_pos()
    map_w = renderer.GRID_SIZE[0] * renderer.TILE_SIZE
    map_h = renderer.GRID_SIZE[1] * renderer.TILE_SIZE
    ox = (screen.get_width() - map_w) // 2
    oy = (screen.get_height() - map_h) // 2

    gx = (mx - ox) // renderer.TILE_SIZE
    gy = (my - oy) // renderer.TILE_SIZE

    if 0 <= gx < renderer.GRID_SIZE[0] and 0 <= gy < renderer.GRID_SIZE[1]:
        current_tile = renderer.TILES[gy][gx]
        current_depth = current_tile.properties['depth']

        if (gx, gy) in fish_map:
            fish = fish_map[(gx, gy)]
            active_fish_name = fish.name
            audio_engine.play_fish_theme(fish.dna, current_depth)
        else:
            active_fish_name = f"Ambient ({current_tile.biome})"
            audio_engine.play_fish_theme(current_tile.biome * 4, current_depth)

    for pos, fish in fish_map.items():
        fx = ox + pos[0] * renderer.TILE_SIZE + renderer.TILE_SIZE // 2
        fy = oy + pos[1] * renderer.TILE_SIZE + renderer.TILE_SIZE // 2
        pygame.draw.circle(screen, (255, 215, 0), (fx, fy), 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()