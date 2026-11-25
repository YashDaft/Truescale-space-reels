"""Makes the renderer's Sun texture and sound effects with code.

Nothing is downloaded, so there are no licence questions:
- textures/sun.png is drawn from random noise (the Earth image is NASA's Blue Marble)
- sfx/*.wav are synthesised from sine waves and noise

Run from the renderer folder:  python3 scripts/make_assets.py
Needs numpy and Pillow.
"""

import wave
from pathlib import Path

import numpy as np
from PIL import Image

PUBLIC = Path(__file__).resolve().parent.parent / "public"
RATE = 44100
rng = np.random.default_rng(7)  # fixed seed, so the files are the same every run


# ---------- textures ----------

def smooth_noise(width, height, octaves=6):
    """Layered noise: big blobs plus smaller detail, values between 0 and 1."""
    total = np.zeros((height, width))
    for i in range(octaves):
        size = 2 ** (i + 2)
        small = rng.random((size, size * 2))
        layer = np.array(Image.fromarray((small * 255).astype(np.uint8)).resize((width, height), Image.BICUBIC)) / 255
        total += layer / (2 ** i)
    total -= total.min()
    return total / total.max()


def make_sun():
    w, h = 1024, 512
    n = smooth_noise(w, h, octaves=7)

    # Make the left and right edges match, so there's no seam where they meet
    edge = np.abs(np.linspace(-1, 1, w))[None, :]
    n = n * (1 - edge) + np.roll(n, w // 2, axis=1) * edge

    # Fade to an even colour near the poles, where the image squeezes into a point
    latitude = np.abs(np.linspace(-1, 1, h))[:, None]
    pole = np.clip((latitude - 0.55) / 0.35, 0, 1)
    n = n * (1 - pole) + n.mean() * pole

    dark = np.array([200, 70, 10]) / 255
    bright = np.array([255, 205, 90]) / 255
    img = dark + (bright - dark) * n[..., None]
    Image.fromarray((img * 255).astype(np.uint8)).save(PUBLIC / "textures" / "sun.png")


# ---------- sound effects ----------

def save_wav(name, samples):
    samples = samples / (np.abs(samples).max() + 1e-9) * 0.9
    data = (samples * 32767).astype(np.int16)
    with wave.open(str(PUBLIC / "sfx" / name), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(data.tobytes())


def low_pass(signal, strength):
    """Simple smoothing filter: higher strength means a darker sound."""
    out = np.zeros_like(signal)
    for i in range(1, len(signal)):
        out[i] = out[i - 1] + (signal[i] - out[i - 1]) / strength
    return out


def make_sfx():
    # whoosh: noise that swells and fades
    t = np.linspace(0, 1.2, int(RATE * 1.2))
    noise = rng.standard_normal(len(t))
    envelope = np.sin(np.pi * t / 1.2) ** 2
    save_wav("whoosh.wav", low_pass(noise, 6) * envelope)

    # boom: a deep falling tone with a soft hit at the start
    t = np.linspace(0, 2.5, int(RATE * 2.5))
    freq = 55 * np.exp(-t * 0.8) + 28
    tone = np.sin(2 * np.pi * np.cumsum(freq) / RATE) * np.exp(-t * 1.6)
    hit = low_pass(rng.standard_normal(len(t)), 12) * np.exp(-t * 12)
    save_wav("boom.wav", tone + hit * 0.6)

    # ping: a clear bell-like tone
    t = np.linspace(0, 1.5, int(RATE * 1.5))
    bell = (np.sin(2 * np.pi * 1318 * t) + 0.4 * np.sin(2 * np.pi * 2636 * t)) * np.exp(-t * 4)
    save_wav("ping.wav", bell)


def tone(freq, seconds, decay):
    """A plucked note: a sine plus one overtone, fading out."""
    t = np.linspace(0, seconds, int(RATE * seconds))
    return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)) * np.exp(-t * decay)


def place(track, sound, at_seconds):
    """Adds a sound into a longer track at a given time."""
    start = int(at_seconds * RATE)
    end = min(start + len(sound), len(track))
    track[start:end] += sound[: end - start]


def make_style_sfx():
    # --- cinematic: a dark drone, a slow swell and a shimmer ---
    seconds = 12
    t = np.linspace(0, seconds, int(RATE * seconds))
    drone = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((41.2, 55, 82.4, 110.2)))
    drone += 0.5 * low_pass(rng.standard_normal(len(t)), 40)
    drone *= np.clip(t / 3, 0, 1) * np.clip((seconds - t) / 2, 0, 1)
    save_wav("cine_drone.wav", drone)

    t = np.linspace(0, 6, int(RATE * 6))
    swell = low_pass(rng.standard_normal(len(t)), 8) * (t / 6) ** 3
    save_wav("cine_swell.wav", swell)

    shimmer = np.zeros(int(RATE * 4))
    for i, f in enumerate((1760, 2217, 2637, 3520)):
        place(shimmer, tone(f, 3.5, 1.5) * 0.5, i * 0.06)
    save_wav("cine_shimmer.wav", shimmer)

    # --- flat: pops, a fast run of ticks that speeds up, a chime, a plucky loop ---
    t = np.linspace(0, 0.25, int(RATE * 0.25))
    pop_freq = 900 * np.exp(-t * 18) + 250
    save_wav("pop.wav", np.sin(2 * np.pi * np.cumsum(pop_freq) / RATE) * np.exp(-t * 22))

    run = np.zeros(int(RATE * 4.2))
    times = 4.0 * (np.linspace(0, 1, 60) ** 0.6)  # ticks get closer together
    for i, at in enumerate(times):
        place(run, tone(700 + i * 18, 0.08, 60) * 0.6, at)
    save_wav("tick_run.wav", run)

    chime = np.zeros(int(RATE * 2.5))
    for i, f in enumerate((523.3, 659.3, 784.0, 1046.5)):
        place(chime, tone(f, 2.0, 2.5), i * 0.07)
    save_wav("chime.wav", chime)

    loop = np.zeros(int(RATE * 12))
    notes = (261.6, 329.6, 392.0, 440.0, 392.0, 329.6, 293.7, 329.6)  # C major pentatonic
    beat = 60 / 112 / 2
    for i in range(int(12 / beat)):
        place(loop, tone(notes[i % len(notes)], 0.4, 9) * 0.5, i * beat)
        if i % 4 == 0:
            place(loop, tone(65.4, 0.5, 6), i * beat)  # soft bass note on each bar
    save_wav("flat_loop.wav", loop)

    # --- line: a soft click and a quiet, clean drone ---
    t = np.linspace(0, 0.05, int(RATE * 0.05))
    save_wav("click.wav", np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 120))

    t = np.linspace(0, 12, int(RATE * 12))
    clean = sum(np.sin(2 * np.pi * f * t) for f in (220, 329.6, 440))
    clean *= (0.7 + 0.3 * np.sin(2 * np.pi * t / 6)) * np.clip(t / 2, 0, 1) * np.clip((12 - t) / 2, 0, 1)
    save_wav("line_drone.wav", clean)


if __name__ == "__main__":
    make_sun()
    make_sfx()
    make_style_sfx()
    print("Made textures and sound effects in", PUBLIC)
