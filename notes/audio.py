import numpy as np
import pygame
import random

SAMPLE_RATE = 44100

def note_to_freq(note_name: str) -> float:
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    name = note_name[:-1]
    octave = int(note_name[-1])
    idx = notes.index(name)
    midi = (octave + 1) * 12 + idx
    return 440.0 * (2 ** ((midi - 69) / 12.0))

NUCLEOTIDE_CHORDS = {
    'A': ['C4', 'E4', 'G4', 'B4', 'D5'],   # Cmaj9
    'C': ['A3', 'C4', 'E4', 'G4', 'B4'],   # Am9
    'G': ['F3', 'A3', 'C4', 'E4', 'G4'],   # Fmaj7
    'T': ['D3', 'F3', 'A3', 'C4', 'E4']    # Dm9
}

PENTATONIC_SCALE = ['C', 'D', 'E', 'G', 'A']

def synthesize_epiano_chord(notes: list[str], duration: float = 2.0) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.zeros_like(t)
    for n in notes:
        f = note_to_freq(n)
        harmonics = np.sin(2 * np.pi * f * t) * 0.6 + \
                    np.sin(2 * np.pi * f * 2 * t) * 0.25 + \
                    np.sin(2 * np.pi * f * 3 * t) * 0.1
        wave += harmonics
    
    envelope = np.exp(-1.2 * t) * (1 - np.exp(-20 * t))
    wave *= envelope
    return wave / len(notes)

def synthesize_harp_note(note_name: str, duration: float = 1.0) -> np.ndarray:
    """Generates a plucked harp-like sound with fast decay."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    f = note_to_freq(note_name)
    wave = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2 * t)
    envelope = np.exp(-4.0 * t) * (1 - np.exp(-100 * t))
    return wave * envelope

class DynamicAudioEngine:
    def __init__(self):
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=1024)
        self.current_channel = pygame.mixer.Channel(0)
        self.next_channel = pygame.mixer.Channel(1)
        self.current_fish_dna = None

    def generate_theme_buffer(self, dna: str, depth: float) -> pygame.mixer.Sound:
        """Synthesizes a 4-bar background loop from 4 DNA base pairs with harp melody."""
        dna = dna.upper().replace('\n', '')[:4]
        if len(dna) < 4:
            dna = (dna + "ACGT")[:4]

        base_octave = 4 if depth < 300 else (3 if depth < 1000 else 2)
        chord_duration = 1.5
        total_duration = chord_duration * 4
        
        mix_buffer = np.zeros(int(SAMPLE_RATE * total_duration))

        for i, base in enumerate(dna):
            chord_notes = NUCLEOTIDE_CHORDS.get(base, NUCLEOTIDE_CHORDS['A'])
            chord_wave = synthesize_epiano_chord(chord_notes, duration=chord_duration * 1.5)
            
            start_idx = int(i * chord_duration * SAMPLE_RATE)
            end_idx = start_idx + len(chord_wave)
            if end_idx <= len(mix_buffer):
                mix_buffer[start_idx:end_idx] += chord_wave * 0.5
            else:
                remaining = len(mix_buffer) - start_idx
                mix_buffer[start_idx:] += chord_wave[:remaining] * 0.5

        harp_pattern = [0, 1, 2, 3, 4, 3, 2, 1] if depth < 500 else [4, 3, 2, 1, 0, 1, 2, 3]
        step_time = total_duration / len(harp_pattern)

        for i, step in enumerate(harp_pattern):
            note = f"{PENTATONIC_SCALE[step % len(PENTATONIC_SCALE)]}{base_octave + 1}"
            harp_wave = synthesize_harp_note(note, duration=1.2)
            start_idx = int(i * step_time * SAMPLE_RATE)
            end_idx = start_idx + len(harp_wave)
            if end_idx <= len(mix_buffer):
                mix_buffer[start_idx:end_idx] += harp_wave * 0.35
            else:
                remaining = len(mix_buffer) - start_idx
                mix_buffer[start_idx:] += harp_wave[:remaining] * 0.35

        max_val = np.max(np.abs(mix_buffer))
        if max_val > 0:
            mix_buffer = mix_buffer / max_val * 0.7

        stereo_wave = np.column_stack((mix_buffer, mix_buffer))
        audio_int16 = (stereo_wave * 32767).astype(np.int16)
        
        return pygame.sndarray.make_sound(audio_int16)

    def play_fish_theme(self, fish_dna: str, depth: float):
        if self.current_fish_dna == fish_dna:
            return

        self.current_fish_dna = fish_dna
        sound = self.generate_theme_buffer(fish_dna, depth)

        self.current_channel.fadeout(1200)
        self.next_channel.play(sound, loops=-1, fade_ms=1200)
        
        self.current_channel, self.next_channel = self.next_channel, self.current_channel