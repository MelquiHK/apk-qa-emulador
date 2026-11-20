#!/usr/bin/env python3
"""Giro con dos dedos usando la consola del emulador
(`adb emu finger press/release <id> <x> <y>`), que sí
soporta varios dedos a la vez. Uso: rotate3.py [grados]"""
import math
import subprocess
import sys
import time

GRADOS = float(sys.argv[1]) if len(sys.argv) > 1 else 55.0
W, H = 1080, 2400


def emu(*args):
    subprocess.run(
        ["adb", "emu", "finger"] + [str(a) for a in args],
        capture_output=True, text=True,
    )


def main():
    cx, cy = W // 2, int(H * 0.45)
    r = int(min(W, H) * 0.30)
    mitad = math.radians(GRADOS) / 2.0

    def punto(a):
        return (int(cx + r * math.cos(a)), int(cy + r * math.sin(a)))

    a0, a1 = -mitad, math.pi - mitad
    x0, y0 = punto(a0)
    x1, y1 = punto(a1)
    emu("press", 0, x0, y0)
    time.sleep(0.08)
    emu("press", 1, x1, y1)
    time.sleep(0.15)
    pasos = 12
    for i in range(1, pasos + 1):
        t = i / pasos
        xa, ya = punto(a0 + math.radians(GRADOS) * t)
        xb, yb = punto(a1 + math.radians(GRADOS) * t)
        emu("press", 0, xa, ya)
        emu("press", 1, xb, yb)
        time.sleep(0.06)
    time.sleep(0.1)
    emu("release", 0)
    emu("release", 1)
    print("GIRO FINGER OK", flush=True)


if __name__ == "__main__":
    main()
