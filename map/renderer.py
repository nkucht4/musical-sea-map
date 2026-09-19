from dataclasses import dataclass
import math
import random

import pygame

GRID_SIZE = (100, 100)
TILE_SIZE = 5
NOISE_SCALE = 0.055

BIOME_COLORS = {
    "polar": (64, 57, 198),
    "tropical": (42, 196, 213),
    "temperate": (28, 131, 227)
}


@dataclass(frozen=True)
class Tile:
    biome: str
    color: tuple[int, int, int]
    properties: dict[str, object]
    depth: int


def _build_map() -> list[list[Tile]]:
    randomizer = random.Random(7)
    biomes = ("polar", "temperate", "tropical")
    
    tile_data = []
    for y in range(GRID_SIZE[1]):
        for x in range(GRID_SIZE[0]):
            noise = _fractal_noise(x * NOISE_SCALE, y * NOISE_SCALE)
            tile_data.append((noise, x, y))
            
    tile_data.sort(key=lambda item: item[0])
    total_tiles = len(tile_data)

    grid_tiles = [[None for _ in range(GRID_SIZE[0])] for _ in range(GRID_SIZE[1])]
    
    for i, (noise, x, y) in enumerate(tile_data):
        if i < total_tiles // 3:
            biome = biomes[0]
        elif i < (total_tiles * 2) // 3:
            biome = biomes[1]
        else:
            biome = biomes[2]
            
        depth = int((i / (total_tiles - 1)) * 4000) if total_tiles > 1 else 0
        
        base_color = BIOME_COLORS[biome]
        depth_factor = 1.0 - (depth / 8000)
        color = tuple(max(0, min(255, int(c * depth_factor))) for c in base_color)
        
        grid_tiles[y][x] = Tile(
            biome=biome,
            color=color,
            properties={
                "position": (x, y),
                "depth": depth,
                "noise": round(noise, 3),
                "current": randomizer.choice(("north", "east", "south", "west")),
            },
            depth=depth
        )

    return grid_tiles


def _fade(value: float) -> float:
    return value * value * value * (value * (value * 6 - 15) + 10)


def _gradient(ix: int, iy: int) -> tuple[float, float]:
    angle = (ix * 127.1 + iy * 311.7) % (2 * math.pi)
    return math.cos(angle), math.sin(angle)


def _perlin_noise(x: float, y: float) -> float:
    x0, y0 = math.floor(x), math.floor(y)
    tx, ty = x - x0, y - y0

    def dot_gradient(ix: int, iy: int) -> float:
        gradient_x, gradient_y = _gradient(ix, iy)
        return gradient_x * (x - ix) + gradient_y * (y - iy)

    top = dot_gradient(x0, y0) * (1 - _fade(tx)) + dot_gradient(x0 + 1, y0) * _fade(tx)
    bottom = dot_gradient(x0, y0 + 1) * (1 - _fade(tx)) + dot_gradient(x0 + 1, y0 + 1) * _fade(tx)
    return bottom * _fade(ty) + top * (1 - _fade(ty))


def _fractal_noise(x: float, y: float) -> float:
    value = 0.0
    amplitude = 1.0
    amplitude_total = 0.0
    for _ in range(4):
        value += _perlin_noise(x, y) * amplitude
        amplitude_total += amplitude
        x *= 2
        y *= 2
        amplitude *= 0.5
    return max(0.0, min(0.999, 0.5 + value / (amplitude_total * 1.25)))


TILES = _build_map()


def draw_tile(surface: pygame.Surface, x: int, y: int, tile: Tile) -> None:
    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(surface, tile.color, rect)

def render() -> None:
    surface = pygame.display.get_surface()
    if surface is None:
        return
    surface.fill((0,0,0))
    map_width = GRID_SIZE[0] * TILE_SIZE
    map_height = GRID_SIZE[1] * TILE_SIZE
    offset_x = (surface.get_width() - map_width) // 2
    offset_y = (surface.get_height() - map_height) // 2
    for y, row in enumerate(TILES):
        for x, tile in enumerate(row):
            draw_tile(surface, x + offset_x // TILE_SIZE, y + offset_y // TILE_SIZE, tile)
