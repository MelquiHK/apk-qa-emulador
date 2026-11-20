#!/usr/bin/env python3
"""Giro del mapa con dos dedos, versión adaptable.

La corrida 050 vio que la uiautomator2 del corredor ya no
acepta `pointer_id` en touch.down(). Este script:
1) imprime la API real disponible (firmas) en api.txt;
2) intenta el giro por la vía que exista:
   a) touch.down/move/up con parámetro de puntero (el nombre
      que tenga en esta versión);
   b) d.gesture(...) si el Device lo trae;
   c) eventos multitáctiles crudos con sendevent (slots MT).
Uso: rotate2.py [grados]
"""
import math
import subprocess
import sys
import time

GRADOS = float(sys.argv[1]) if len(sys.argv) > 1 else 55.0


def log_api(d):
    import inspect
    lines = []
    try:
        lines.append("touch.down: " + str(inspect.signature(d.touch.down)))
        lines.append("touch.move: " + str(inspect.signature(d.touch.move)))
        lines.append("touch.up: " + str(inspect.signature(d.touch.up)))
    except Exception as e:  # noqa: BLE001
        lines.append("touch firmas: ERROR " + str(e))
    names = [n for n in dir(d) if not n.startswith("_")]
    lines.append("device metodos: " + ",".join(names))
    tnames = [n for n in dir(d.touch) if not n.startswith("_")]
    lines.append("touch metodos: " + ",".join(tnames))
    lines.append("has gesture: " + str(hasattr(d, "gesture")))
    if hasattr(d, "gesture"):
        try:
            lines.append("gesture: " + str(inspect.signature(d.gesture)))
        except Exception as e:  # noqa: BLE001
            lines.append("gesture firma: ERROR " + str(e))
    with open("shots/api.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("\n".join(lines), flush=True)
    return lines


def via_pointer(d, w, h):
    import inspect
    sig = inspect.signature(d.touch.down)
    params = [p for p in sig.parameters if p not in ("self",)]
    if len(params) < 3:
        return False
    kw = params[2]
    cx, cy = w // 2, int(h * 0.45)
    r = int(min(w, h) * 0.30)
    pasos = 12
    mitad = math.radians(GRADOS) / 2.0

    def punto(a):
        return (int(cx + r * math.cos(a)), int(cy + r * math.sin(a)))

    a0, a1 = -mitad, math.pi - mitad
    x0, y0 = punto(a0)
    x1, y1 = punto(a1)
    d.touch.down(x0, y0, **{kw: 0})
    d.touch.down(x1, y1, **{kw: 1})
    time.sleep(0.1)
    for i in range(1, pasos + 1):
        t = i / pasos
        xa, ya = punto(a0 + math.radians(GRADOS) * t)
        xb, yb = punto(a1 + math.radians(GRADOS) * t)
        d.touch.move(xa, ya, **{kw: 0})
        d.touch.move(xb, yb, **{kw: 1})
        time.sleep(0.03)
    d.touch.up(**{kw: 0})
    d.touch.up(**{kw: 1})
    return True


def via_gesture(d, w, h):
    if not hasattr(d, "gesture"):
        return False
    cx, cy = w // 2, int(h * 0.45)
    r = int(min(w, h) * 0.30)
    mitad = math.radians(GRADOS) / 2.0

    def punto(a):
        return (int(cx + r * math.cos(a)), int(cy + r * math.sin(a)))

    s1 = punto(-mitad)
    s2 = punto(math.pi - mitad)
    e1 = punto(-mitad + math.radians(GRADOS))
    e2 = punto(math.pi - mitad + math.radians(GRADOS))
    try:
        d.gesture(s1, s2, e1, e2, steps=24)
    except TypeError:
        d.gesture(s1, e1, steps=24)
    return True


def find_mt_device():
    out = subprocess.run(
        ["adb", "shell", "getevent", "-p"],
        capture_output=True, text=True,
    ).stdout
    dev = None
    for block in out.split("add device"):
        if "ABS_MT_POSITION_X" in block or "0035" in block:
            for line in block.splitlines():
                line = line.strip()
                if line.startswith("/dev/input/event"):
                    dev = line.split()[0]
                    break
        if dev:
            break
    return dev


def sendevent(dev, etype, code, value):
    subprocess.run(
        ["adb", "shell", "sendevent", dev, str(etype), str(code), str(value)],
        capture_output=True,
    )


def via_sendevent(w, h):
    dev = find_mt_device()
    if not dev:
        print("sendevent: sin dispositivo MT", flush=True)
        return False
    print("sendevent dev:", dev, flush=True)
    EV_SYN, EV_ABS = 0, 3
    SYN_REPORT = 0
    ABS_MT_SLOT, ABS_MT_TRACKING_ID = 47, 57
    ABS_MT_POSITION_X, ABS_MT_POSITION_Y = 53, 54
    cx, cy = w // 2, int(h * 0.45)
    r = int(min(w, h) * 0.30)
    pasos = 14
    mitad = math.radians(GRADOS) / 2.0

    def punto(a):
        return (int(cx + r * math.cos(a)), int(cy + r * math.sin(a)))

    def frame(p0, p1, tid0=100, tid1=200, up=False):
        sendevent(dev, EV_ABS, ABS_MT_SLOT, 0)
        if up:
            sendevent(dev, EV_ABS, ABS_MT_TRACKING_ID, -1)
        else:
            sendevent(dev, EV_ABS, ABS_MT_TRACKING_ID, tid0)
            sendevent(dev, EV_ABS, ABS_MT_POSITION_X, p0[0])
            sendevent(dev, EV_ABS, ABS_MT_POSITION_Y, p0[1])
        sendevent(dev, EV_ABS, ABS_MT_SLOT, 1)
        if up:
            sendevent(dev, EV_ABS, ABS_MT_TRACKING_ID, -1)
        else:
            sendevent(dev, EV_ABS, ABS_MT_TRACKING_ID, tid1)
            sendevent(dev, EV_ABS, ABS_MT_POSITION_X, p1[0])
            sendevent(dev, EV_ABS, ABS_MT_POSITION_Y, p1[1])
        sendevent(dev, EV_SYN, SYN_REPORT, 0)

    a0, a1 = -mitad, math.pi - mitad
    frame(punto(a0), punto(a1))
    time.sleep(0.15)
    for i in range(1, pasos + 1):
        t = i / pasos
        frame(
            punto(a0 + math.radians(GRADOS) * t),
            punto(a1 + math.radians(GRADOS) * t),
        )
        time.sleep(0.04)
    frame((0, 0), (0, 0), up=True)
    return True


def main():
    import uiautomator2 as u2
    d = u2.connect()
    info = d.info
    w = int(info["displayWidth"])
    h = int(info["displayHeight"])
    log_api(d)
    for nombre, fn in (("pointer", via_pointer), ("gesture", via_gesture)):
        try:
            if fn(d, w, h):
                print("GIRO VIA", nombre, flush=True)
                return
        except Exception as e:  # noqa: BLE001
            print("via", nombre, "fallo:", e, flush=True)
    if via_sendevent(w, h):
        print("GIRO VIA sendevent", flush=True)
        return
    print("GIRO IMPOSIBLE", flush=True)
    sys.exit(3)


if __name__ == "__main__":
    main()
