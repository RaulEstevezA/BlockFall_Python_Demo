"""Genera la música de fondo del juego (music/theme.ogg) desde cero.

La melodía es «Korobeiniki», canción popular rusa del siglo XIX y de dominio
público. El sonido se sintetiza aquí mismo (onda cuadrada para la melodía,
triangular para el bajo y ruido para la percusión), sin usar ninguna grabación
ni arreglo de terceros.

Uso:  python tool/generate_music.py      (necesita ffmpeg para pasar a OGG)
"""

import array
import math
import os
import random
import subprocess
import tempfile
import wave

SAMPLE_RATE = 44100
BPM = 150
BEAT = 60 / BPM  # duracion de una negra en segundos

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "music", "theme.ogg")

NOTE_INDEX = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
              "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def frequency(note):
    """'A4' -> 440 Hz; None es un silencio"""
    if note is None:
        return None
    name, octave = note[:-1], int(note[-1])
    midi = 12 * (octave + 1) + NOTE_INDEX[name]
    return 440 * 2 ** ((midi - 69) / 12)


# melodia: (nota, duracion en negras)
PART_A = [
    ("E5", 1), ("B4", .5), ("C5", .5), ("D5", 1), ("C5", .5), ("B4", .5),
    ("A4", 1), ("A4", .5), ("C5", .5), ("E5", 1), ("D5", .5), ("C5", .5),
    ("B4", 1.5), ("C5", .5), ("D5", 1), ("E5", 1),
    ("C5", 1), ("A4", 1), ("A4", 2),
    ("D5", 1.5), ("F5", .5), ("A5", 1), ("G5", .5), ("F5", .5),
    ("E5", 1.5), ("C5", .5), ("E5", 1), ("D5", .5), ("C5", .5),
    ("B4", 1), ("B4", .5), ("C5", .5), ("D5", 1), ("E5", 1),
    ("C5", 1), ("A4", 1), ("A4", 1), (None, 1),
]

PART_B = [
    ("E5", 2), ("C5", 2), ("D5", 2), ("B4", 2),
    ("C5", 2), ("A4", 2), ("G#4", 2), ("B4", 2),
    ("E5", 2), ("C5", 2), ("D5", 2), ("B4", 2),
    ("C5", 1), ("E5", 1), ("A5", 2), ("G#5", 3), (None, 1),
]

# acorde (nota grave) de cada media parte de compas, para el bajo
BASS_A = ["E2", "E2", "A2", "A2", "E2", "E2", "A2", "A2",
          "D2", "D2", "C2", "C2", "E2", "E2", "A2", "A2"]
BASS_B = ["A2", "A2", "E2", "E2", "A2", "A2", "E2", "E2",
          "A2", "A2", "E2", "E2", "A2", "A2", "E2", "E2"]

# estructura del tema: A A B A (se repite en bucle en el juego)
SONG = [(PART_A, BASS_A), (PART_A, BASS_A), (PART_B, BASS_B), (PART_A, BASS_A)]


def render():
    beats = sum(sum(d for _, d in melody) for melody, _ in SONG)
    total = int(beats * BEAT * SAMPLE_RATE)
    mix = [0.0] * total

    def add_note(freq, start_beat, length_beats, wave_fn, volume, gap=0.08):
        """suma una nota con ataque rapido y caida suave; gap separa notas repetidas"""
        if freq is None:
            return
        start = int(start_beat * BEAT * SAMPLE_RATE)
        length = int(length_beats * BEAT * SAMPLE_RATE * (1 - gap))
        attack = int(0.005 * SAMPLE_RATE)
        release = int(0.02 * SAMPLE_RATE)
        for i in range(length):
            t = i / SAMPLE_RATE
            env = min(1.0, i / attack) * (0.55 + 0.45 * math.exp(-t * 6))
            if i > length - release:
                env *= (length - i) / release
            mix[start + i] += volume * env * wave_fn(freq * t)

    def square(phase):  # cuadrada con ciclo del 25 %, sonido tipo consola antigua
        return 1.0 if phase % 1 < 0.25 else -1.0

    def triangle(phase):
        p = phase % 1
        return 4 * p - 1 if p < 0.5 else 3 - 4 * p

    rng = random.Random(1984)
    beat = 0.0
    for melody, bass in SONG:
        part_start = beat
        for note, duration in melody:
            add_note(frequency(note), beat, duration, square, 0.16)
            beat += duration

        # bajo en corcheas alternando la nota y su octava
        for half_bar, root in enumerate(bass):
            low = frequency(root)
            for step in range(4):
                freq = low if step % 2 == 0 else low * 2
                add_note(freq, part_start + half_bar * 2 + step * 0.5, 0.5, triangle, 0.22)

        # percusion: golpe corto de ruido en cada corchea, mas fuerte en los tiempos
        for step in range(int((beat - part_start) * 2)):
            start = int((part_start + step * 0.5) * BEAT * SAMPLE_RATE)
            volume = 0.06 if step % 2 == 0 else 0.03
            for i in range(int(0.03 * SAMPLE_RATE)):
                mix[start + i] += volume * math.exp(-i / 300) * rng.uniform(-1, 1)

    peak = max(abs(s) for s in mix)
    return array.array("h", (int(s / peak * 0.85 * 32767) for s in mix))


def main():
    samples = render()
    with tempfile.TemporaryDirectory() as tmp:
        wav_path = os.path.join(tmp, "theme.wav")
        with wave.open(wav_path, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(samples.tobytes())
        # el codificador vorbis nativo de ffmpeg es experimental, de ahi -strict -2
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav_path,
                        "-c:a", "vorbis", "-strict", "-2", "-ac", "2", "-b:a", "96k",
                        os.path.abspath(OUTPUT)], check=True)
    print(f"generado {os.path.abspath(OUTPUT)}")


if __name__ == "__main__":
    main()
