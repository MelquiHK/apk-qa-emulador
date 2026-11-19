#!/usr/bin/env python3
"""Ayudante de toques por uiautomator para los workflows de QA.

Uso:
  tap.py text "Entrar" [idx]     toca el nodo con ese texto exacto
  tap.py textpart "Entregas"     toca el nodo cuyo texto CONTIENE eso
  tap.py desc "Actualizar"       toca por content-desc
  tap.py edit IDX                toca el EditText nº IDX (orden visual)
  tap.py switch                  toca el Switch (o estima su posición)
  tap.py type "texto con espacios"
  tap.py has "Texto"             imprime SI/NO según esté en pantalla
  tap.py shot nombre.png         captura de pantalla
"""
import re
import subprocess
import sys


def dump():
    subprocess.run(["adb", "shell", "uiautomator", "dump", "/sdcard/ui.xml"],
                   capture_output=True)
    subprocess.run(["adb", "pull", "/sdcard/ui.xml", "ui.xml"],
                   capture_output=True)
    try:
        return open("ui.xml", encoding="utf-8").read()
    except Exception:
        return ""


def nodes(xml):
    out = []
    for n in re.findall(r"<node[^>]*>", xml):
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', n)
        if not m:
            continue
        a, b, c, d = map(int, m.groups())
        out.append({
            "raw": n,
            "text": (re.search(r'text="([^"]*)"', n) or [None, ""])[1],
            "desc": (re.search(r'content-desc="([^"]*)"', n) or [None, ""])[1],
            "cls": (re.search(r'class="([^"]*)"', n) or [None, ""])[1],
            "cx": (a + c) // 2, "cy": (b + d) // 2,
            "x2": c, "y1": b, "y2": d,
        })
    return out


def tap(x, y):
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])
    print(f"tap {x},{y}", flush=True)


def main():
    mode = sys.argv[1]
    xml = dump()
    ns = nodes(xml)
    if mode == "text":
        want = sys.argv[2]
        idx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        hits = [n for n in ns if n["text"] == want]
        hits.sort(key=lambda n: n["cy"])
        if len(hits) > idx:
            tap(hits[idx]["cx"], hits[idx]["cy"])
        else:
            print("NO_ENCONTRADO text=" + want, flush=True)
    elif mode == "textpart":
        want = sys.argv[2]
        hits = [n for n in ns if want in n["text"]]
        hits.sort(key=lambda n: n["cy"])
        if hits:
            tap(hits[0]["cx"], hits[0]["cy"])
        else:
            print("NO_ENCONTRADO textpart=" + want, flush=True)
    elif mode == "desc":
        want = sys.argv[2]
        hits = [n for n in ns if n["desc"] == want]
        if hits:
            tap(hits[0]["cx"], hits[0]["cy"])
        else:
            print("NO_ENCONTRADO desc=" + want, flush=True)
    elif mode == "edit":
        idx = int(sys.argv[2])
        hits = [n for n in ns if n["cls"] == "android.widget.EditText"]
        hits.sort(key=lambda n: n["cy"])
        if len(hits) > idx:
            tap(hits[idx]["cx"], hits[idx]["cy"])
        else:
            print("NO_ENCONTRADO edit " + str(idx), flush=True)
    elif mode == "switch":
        hits = [n for n in ns if n["cls"] == "android.widget.Switch"]
        if hits:
            tap(hits[0]["cx"], hits[0]["cy"])
        else:
            rows = [n for n in ns if "repartiendo" in n["text"]]
            if rows:
                r = rows[0]
                tap(max(r["x2"] - 70, 0), r["cy"])
            else:
                print("NO_ENCONTRADO switch", flush=True)
    elif mode == "type":
        subprocess.run(["adb", "shell", "input", "text",
                        sys.argv[2].replace(" ", "%s")])
        print("type ok", flush=True)
    elif mode == "has":
        want = sys.argv[2]
        print(("SI " if want in xml else "NO ") + want, flush=True)
    elif mode == "shot":
        with open(sys.argv[2], "wb") as f:
            subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=f)
        print("shot " + sys.argv[2], flush=True)


if __name__ == "__main__":
    main()
