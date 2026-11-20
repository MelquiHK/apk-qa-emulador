#!/usr/bin/env python3
"""Giro del mapa con dos dedos (rotación) pa la QA, con uiautomator2.

Uso: rotate.py [grados]
Dos punteros en lados opuestos del centro se mueven en arco en
sentidos contrarios: eso es el gesto de girar el mapa. Si la API
multipuntero no existe o falla, sale con error y el workflow
sigue (la brújula también se puede provocar con el modo seguir
con rumbo, pero el gesto es la prueba de verdad).
"""
import math
import sys
import time

import uiautomator2 as u2


def main():
    grados = float(sys.argv[1]) if len(sys.argv) > 1 else 50.0
    d = u2.connect()
    info = d.info
    w = int(info["displayWidth"])
    h = int(info["displayHeight"])
    cx, cy = w // 2, int(h * 0.45)
    r = int(min(w, h) * 0.30)
    pasos = 12
    mitad = math.radians(grados) / 2.0

    def punto(angulo):
        return (int(cx + r * math.cos(angulo)), int(cy + r * math.sin(angulo)))

    a0 = -mitad
    a1 = math.pi - mitad
    x0, y0 = punto(a0)
    x1, y1 = punto(a1)
    d.touch.down(x0, y0, pointer_id=0)
    d.touch.down(x1, y1, pointer_id=1)
    time.sleep(0.1)
    for i in range(1, pasos + 1):
        t = i / pasos
        xa, ya = punto(a0 + math.radians(grados) * t)
        xb, yb = punto(a1 + math.radians(grados) * t)
        d.touch.move(xa, ya, pointer_id=0)
        d.touch.move(xb, yb, pointer_id=1)
        time.sleep(0.03)
    d.touch.up(pointer_id=0)
    d.touch.up(pointer_id=1)
    print(f"rotados {grados} grados en {w}x{h}")


if __name__ == "__main__":
    main()
