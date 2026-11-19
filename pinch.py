#!/usr/bin/env python3
"""Pinch-out (alejar) con uiautomator2 pa la QA del mapa.

Uso: pinch.py [veces]
Cada pinch_in junta los dedos = aleja el mapa. Si uiautomator2
no está o falla, sale con error y el workflow sigue con las
demás pruebas (queda anotado en checks.txt).
"""
import sys
import time

import uiautomator2 as u2


def main():
    veces = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    d = u2.connect()
    for _ in range(veces):
        d.pinch_in(percent=70, steps=12)
        time.sleep(1.2)
    print("pinch ok x%d" % veces)


if __name__ == "__main__":
    main()
