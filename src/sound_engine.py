"""
Retro 8-bit sound effects generated in Python as WAV audio.

Sounds are played via st.audio(autoplay=True) and hidden with CSS.
No external audio files needed — everything is synthesized.
"""

import struct
import math
import random
import streamlit as st

SR = 22050


def _wav(samples):
    """Convert [-1.0 … 1.0] float list to WAV bytes."""
    pcm = struct.pack(
        f"<{len(samples)}h",
        *(max(-32768, min(32767, int(s * 32767))) for s in samples),
    )
    hdr = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + len(pcm), b"WAVE",
        b"fmt ", 16, 1, 1, SR, SR * 2, 2, 16,
        b"data", len(pcm),
    )
    return hdr + pcm


def _sq(freq, dur, vol=0.15):
    """Square-wave tone with micro-jitter for uniqueness."""
    jit = random.uniform(-0.0002, 0.0002)
    return [
        (vol + jit) * (1 if math.sin(2 * math.pi * freq * i / SR) >= 0 else -1)
        for i in range(int(SR * dur))
    ]


def _sweep(f0, f1, dur, vol=0.15):
    """Square-wave frequency sweep with micro-jitter."""
    n = int(SR * dur)
    out, phase = [], 0.0
    jit = random.uniform(-0.0002, 0.0002)
    for i in range(n):
        t = i / SR
        freq = f0 + (f1 - f0) * (t / dur)
        phase += 2 * math.pi * freq / SR
        env = 1.0 - (t / dur) ** 2
        out.append((vol + jit) * env * (1 if math.sin(phase) >= 0 else -1))
    return out


def _noise(dur, vol=0.15):
    """White noise burst."""
    return [random.uniform(-vol, vol) for _ in range(int(SR * dur))]


def _fade(samples, fi=0.005, fo=0.02):
    """Fade in / fade out envelope."""
    n = len(samples)
    a = int(SR * fi)
    r = int(SR * fo)
    for i in range(min(a, n)):
        samples[i] *= i / max(a, 1)
    for i in range(min(r, n)):
        samples[n - 1 - i] *= i / max(r, 1)
    return samples


# ── Sound builders ──────────────────────────────────────────────────────

_BUILDERS = {
    "select": lambda: _wav(_fade(_sq(880, 0.05, 0.12))),

    "next": lambda: _wav(_fade(
        _sq(660, 0.05, 0.10) + _sq(990, 0.06, 0.10),
    )),

    "back": lambda: _wav(_fade(
        _sq(660, 0.05, 0.10) + _sq(440, 0.06, 0.10),
    )),

    "battle_start": lambda: _wav(_fade(
        _sweep(220, 880, 0.30, 0.16), fo=0.08,
    )),

    "attack": lambda: _wav(_fade(
        _sweep(300, 700, 0.10, 0.13), fo=0.03,
    )),

    "hit": lambda: _wav(_fade(
        _noise(0.07, 0.22), fi=0.002, fo=0.03,
    )),

    "miss": lambda: _wav(_fade(
        _noise(0.10, 0.06), fi=0.002, fo=0.05,
    )),

    "super_effective": lambda: _wav(_fade(
        _sq(523, 0.08, 0.14) + _sq(784, 0.10, 0.14),
    )),

    "not_effective": lambda: _wav(_fade(
        _sweep(350, 180, 0.15, 0.09),
    )),

    "faint": lambda: _wav(_fade(
        _sweep(440, 110, 0.50, 0.13), fo=0.10,
    )),

    "victory": lambda: _wav(_fade(
        _sq(523, 0.10, 0.13) + _sq(659, 0.10, 0.13)
        + _sq(784, 0.10, 0.13) + _sq(1047, 0.16, 0.13),
        fo=0.06,
    )),

    "draw": lambda: _wav(_fade(
        _sq(330, 0.15, 0.10) + _sq(262, 0.18, 0.10),
    )),
}


def _build(name: str) -> bytes | None:
    """Build a fresh WAV each call (micro-noise makes bytes unique)."""
    builder = _BUILDERS.get(name)
    if not builder:
        return None
    return builder()


def play(name: str, placeholder=None):
    """
    Play a named 8-bit sound effect.

    Uses st.audio(autoplay=True). Audio widgets are hidden by CSS.
    Pass an st.empty() *placeholder* during animation loops to avoid
    accumulating widgets in the DOM.
    """
    if not st.session_state.get("sound_enabled", True):
        return
    wav = _build(name)
    if not wav:
        return
    if placeholder is not None:
        with placeholder:
            st.audio(wav, format="audio/wav", autoplay=True)
    else:
        st.audio(wav, format="audio/wav", autoplay=True)
