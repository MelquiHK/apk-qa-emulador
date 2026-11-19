#!/usr/bin/env python3
"""Pinch-in (alejar el mapa) con uiautomator2 pa la QA.

Uso: pinch.py [veces]
En uiautomator2 v3 el Device ya no tiene pinch_in: se usa el
gesto de dos dedos d.gesture(p1, p2, p3, p4). Si eso falla,
se intenta el pinch sobre la vista del mapa (SurfaceView).
Si todo falla, sale con error y el workflow lo anota.
"""
import sys
import time

import uiautomator2 as u2


def main():
    veces = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    d = u2.connect()
    info = d.info
    w = int(info["displayWidth"])
    h = int(info["displayHeight"])
    cx, cy = w // 2, h // 2
    r_out = int(min(w, h) * 0.34)
    r_in = int(min(w, h) * 0.07)
    for _ in range(veces):
        try:
            # Dedos alejados -> dedos juntos: aleja el mapa.
            d.gesture(
                (cx - r_out, cy), (cx + r_out, cy),
                (cx - r_in, cy), (cx + r_in, cy),
                steps=24,
            )
        except Exception:
            vista = d(className="android.view.SurfaceView")
            if not vista.exists:
                vista = d(className="android.opengl.GLSurfaceView")
            vista.pinch_in(percent=70, steps=15)
        time.sleep(1.2)
    print("pinch ok x%d" % veces)


if __name__ == "__main__":
    main()
