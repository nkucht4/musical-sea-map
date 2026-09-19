import csv
import random
from dataclasses import dataclass

@dataclass
class Fish:
    name: str
    dna: str
    biome: str
    height_min: float
    height_max: float
    position: tuple[int, int]

def load_and_place_fishes(csv_filepath: str, grid_tiles: list[list]) -> list[Fish]:
    fishes = []
    rand = random.Random(42)

    with open(csv_filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            biome = row['biome']
            h_min = float(row['height_min'])
            h_max = float(row['height_max'])
            dna = row['dna']
            name = row['name']

            candidates = []
            for y, r in enumerate(grid_tiles):
                for x, tile in enumerate(r):
                    t_biome = tile.biome
                    t_depth = float(tile.properties['depth'])
                    if (not biome or t_biome == biome) and (h_min <= t_depth <= h_max):
                        candidates.append((x, y))

            if candidates:
                pos = rand.choice(candidates)
                fishes.append(Fish(
                    name=name,
                    dna=dna,
                    biome=biome,
                    height_min=h_min,
                    height_max=h_max,
                    position=pos
                ))
    return fishes