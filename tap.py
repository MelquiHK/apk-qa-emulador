#!/usr/bin/env python3
"""Ayudante de toques por uiautomator para los workflows de QA.

Uso:
  tap.py text "Entrar" [idx]     toca el nodo con ese texto exacto
  tap.py textpart "Entregas"     toca el nodo cuyo texto CONTIENE eso
  tap.py desc "Actualizar"       toca por content-desc
  tap.py descpart "Menu"         toca el nodo cuyo content-desc CONTIENE eso
  tap.py result "Habana"         toca el 1er nodo con ese texto por debajo de y=500
  tap.py dump ui.xml             guarda el dump actual en el archivo dado
  tap.py texts lista.txt         escribe textos y descs visibles en el archivo
  tap.py clickables lista.txt    escribe nodos tocables (texto|desc|bounds)
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
            "checked": (re.search(r'checked="([^"]*)"', n) or [None, ""])[1],
            "cx": (a + c) // 2, "cy": (b + d) // 2,
            "x1": a, "x2": c, "y1": b, "y2": d,
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
    elif mode == "descpart":
        want = sys.argv[2]
        hits = [n for n in ns if want in n["desc"]]
        hits.sort(key=lambda n: n["cy"])
        if hits:
            tap(hits[0]["cx"], hits[0]["cy"])
        else:
            print("NO_ENCONTRADO descpart=" + want, flush=True)
    elif mode == "result":
        want = sys.argv[2]
        hits = [n for n in ns if want in n["text"] and n["cy"] > 500]
        hits.sort(key=lambda n: n["cy"])
        if hits:
            tap(hits[0]["cx"], hits[0]["cy"])
        else:
            print("NO_ENCONTRADO result=" + want, flush=True)
    elif mode == "dump":
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(xml)
        print("dump " + sys.argv[2], flush=True)
    elif mode == "texts":
        vals = sorted({n["text"] for n in ns if n["text"]} |
                      {n["desc"] for n in ns if n["desc"]})
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write("\n".join(vals))
        print("texts %d en %s" % (len(vals), sys.argv[2]), flush=True)
    elif mode == "clickables":
        rows = []
        for n in ns:
            if 'clickable="true"' in n["raw"]:
                rows.append("texto=%s | desc=%s | bounds=[%d,%d][%d,%d]" %
                            (n["text"], n["desc"], n["x1"], n["y1"],
                             n["x2"], n["y2"]))
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write("\n".join(rows))
        print("clickables %d en %s" % (len(rows), sys.argv[2]), flush=True)
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
            sw = hits[0]
            if sw["checked"] == "true":
                print("switch YA ENCENDIDO", flush=True)
            else:
                tap(sw["cx"], sw["cy"])
        else:
            rows = [n for n in ns if "repartiendo" in n["text"]]
            if rows:
                r = rows[0]
                width = max((n["x2"] for n in ns), default=1080)
                tap(int(width * 0.86), r["cy"])
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
