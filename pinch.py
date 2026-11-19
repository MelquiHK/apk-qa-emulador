#!/usr/bin/env python3
"""Pinch-in (alejar el mapa) con uiautomator2 pa la QA.

Uso: pinch.py [veces]
uiautomator2 v3 no tiene pinch_in ni gesture en el Device:
se intenta el toque multipuntero d.touch.down/move/up con
dos pointer_id. Si la API no existe o falla, sale con error
y el workflow sigue (la prueba del tope de zoom la cubre el
botón «−» de la navegación y la del borde, los swipes).
"""
import sys
import time

import uiautomator2 as u2


def pinch_una(d, w, h):
    cx, cy = w // 2, h // 2
    r_out = int(min(w, h) * 0.34)
    r_in = int(min(w, h) * 0.07)
    pasos = 10
    d.touch.down(cx - r_out, cy, pointer_id=0)
    d.touch.down(cx + r_out, cy, pointer_id=1)
    time.sleep(0.1)
    for i in range(1, pasos + 1):
        r = r_out + (r_in - r_out) * i // pasos
        d.touch.move(cx - r, cy, pointer_id=0)
        d.touch.move(cx + r, cy, pointer_id=1)
        time.sleep(0.03)
    d.touch.up(pointer_id=0)
    d.touch.up(pointer_id=1)


def main():
    veces = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    d = u2.connect()
    info = d.info
    w = int(info["displayWidth"])
    h = int(info["displayHeight"])
    for _ in range(veces):
        pinch_una(d, w, h)
        time.sleep(1.0)
    print("pinch ok x%d" % veces)


if __name__ == "__main__":
    main()
