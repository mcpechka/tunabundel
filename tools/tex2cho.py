"""Convert Tunabundel LaTeX song files (tunaChords.sty) to ChordPro.
Usage: python3 tools/tex2cho.py <songs_dir> <out_dir>
Prints only file names and counts, never song content."""
import re, os, sys, unicodedata

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

CHORD_RE = re.compile(r"^(?:[A-G]|Do|Re|Mi|Fa|Sol|La|Si)(?:#|b)?(?:m|maj|min|dim|aug|sus|add|°|\+|ø|\d|\(|\)|M)*(?:/(?:[A-G]|Do|Re|Mi|Fa|Sol|La|Si)(?:#|b)?)?$")
STYLE = {"paso_doble": "Paso doble", "vals": "Vals", "tango": "Tango", "bolero": "Bolero", "son": "Son", "copla": "Copla",
         "huayno": "Huayno", "joropo": "Joropo", "fado": "Fado", "takirari": "Takirari", "tropical": "Tropical"}

def braced(s, i):
    d = 0
    for j in range(i, len(s)):
        if s[j] == "{": d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0: return s[i + 1:j], j + 1
    return s[i + 1:], len(s)

def text(t):
    t = t.replace("!`", "¡").replace("?`", "¿")
    t = re.sub(r"\\'\{?\\i\}?", "í", t)
    t = re.sub(r"\\'\{?([aeiouAEIOU])\}?", lambda m: unicodedata.normalize("NFC", m.group(1) + "\u0301"), t)
    t = re.sub(r"\\~\{?n\}?", "ñ", t); t = re.sub(r"\\~\{?N\}?", "Ñ", t)
    t = re.sub(r'\\"\{?([uU])\}?', lambda m: "ü" if m.group(1) == "u" else "Ü", t)
    t = t.replace("\\textquestiondown", "¿").replace("\\ldots", "…")
    t = re.sub(r"\\(?:hspace|vspace|phantom)\*?\{[^{}]*\}", " ", t)
    t = re.sub(r"\\(?:textbf|textnormal|textit|emph|underline)\{([^{}]*)\}", r"\1", t)
    t = t.replace("\\_", " ").replace("$\\_$", " ").replace("``", "\"").replace("''", "\"")
    t = t.replace("$\\downarrow$", "↓").replace("$\\uparrow$", "↑").replace("$\\sharp$", "#").replace("$\\flat$", "b").replace("$\\circ$", "°")
    t = re.sub(r"\\nicefrac\{(\d+)\}\{(\d+)\}", r"\1/\2", t)
    t = re.sub(r"\$[^$]*\$", "", t)
    t = re.sub(r"\\[a-zA-Z]+\*?", "", t)
    t = t.replace("{", "").replace("}", "").replace("~", " ").replace("\\", "")
    return re.sub(r"[ \t]+", " ", t)

def chord_name(c):
    c = c.replace("$\\sharp$", "#").replace("\\sharp", "#").replace("$\\flat$", "b").replace("\\flat", "b")
    c = c.replace("$\\circ$", "°") if re.match(r"^\s*[A-G][#b]?\$\\circ\$\s*$", c) else c
    c = re.split(r"\$|;|\s", c.strip())[0].replace("\\", "").strip().lstrip("*")
    return c if c and CHORD_RE.match(c) else None

def chord_token(body, defines):
    """LaTeX \\chord body -> ChordPro token ('' for nothing)."""
    b = body.strip()
    fm = re.match(r"^\*?\s*([^:]+?)\s*:\s*([x\d][x\d\-\s]+)$", text(b).strip())
    if fm and chord_name(fm.group(1)):
        frets = [f for f in re.split(r"[-\s]+", fm.group(2).strip()) if f]
        if len(frets) in (4, 6):
            defines[chord_name(fm.group(1))] = " ".join(frets)
        return ""
    c = chord_name(b)
    if c: return "[" + c + "]"
    ann = text(b).strip().strip("_ ")
    ann = re.sub(r"\s+", " ", ann)
    return "[*" + ann.replace("]", ")") + "]" if ann else ""

def line_to_cho(line, defines):
    out, last, i = [], 0, 0
    pat = re.compile(r"\\chord\*?\{")
    while True:
        m = pat.search(line, last)
        if not m: break
        body, end = braced(line, m.end() - 1)
        out.append(text(line[last:m.start()]))
        out.append(chord_token(body, defines))
        last = end
    out.append(text(line[last:]))
    return re.sub(r"\s+", " ", "".join(out)).strip()

def measures(row):
    cells, last = [], 0
    pat = re.compile(r"\\measure\*?\{")
    while True:
        m = pat.search(row, last)
        if not m: break
        body, end = braced(row, m.end() - 1)
        rep = ""
        if end < len(row) and row[end] == "[":
            close = row.find("]", end)
            if close > 0: rep = row[end + 1:close]; end = close + 1
        c = chord_name(body)
        cell = c if c else (text(body).strip() if text(body).strip() and not re.match(r"^[\d\s]+$", text(body).strip()) else ".")
        if c: cell = "[" + c + "]"
        elif cell != ".": cell = "[*" + cell + "]"
        cells.append(cell + (" :" if rep.strip() == ":" else (" (" + rep.strip() + "x)" if rep.strip().isdigit() else "")))
        last = end
    return cells

def is_chorus(name):
    return bool(re.match(r"^(refrein|refrain|estribillo|coro|chorus)", name.strip(), re.I))

def convert(raw):
    raw = "\n".join(l for l in raw.split("\n") if not l.lstrip().startswith("%"))
    m = re.search(r"\\begin\{song\}\*?(?:\[([^\]]*)\])?\{", raw)
    if not m: return None
    title, _ = braced(raw, m.end() - 1)
    title = text(title).strip()
    if not title: return None
    style = (m.group(1) or "").strip()
    head = ["{title: " + title + "}"]
    km = re.search(r"\\rhythmandkey\*?(?:\[([^\]]*)\])?\{([^{}]*)\}\{", raw)
    if km:
        kb, _ = braced(raw, km.end() - 1)
        key = chord_name(re.sub(r"\\chord\*?\{([^{}]*)\}", r"\1", kb)) or text(kb).strip()
        if key: head.append("{key: " + key + "}")
        mt = re.search(r"nicefrac\{(\d+)\}\{(\d+)\}", km.group(1) or "")
        if mt: head.append("{time: " + mt.group(1) + "/" + mt.group(2) + "}")
        rhythm = text(km.group(2)).strip()
        if rhythm: head.append("{meta: rhythm " + rhythm + "}")
    elif style in STYLE:
        head.append("{meta: rhythm " + STYLE[style] + "}")
    head.append("{meta: source Tunabundel – Tuna Ciudad de Luz}")
    defines, body = {}, []
    song_part = raw.split("\\end{song}")[0]
    tr = re.search(r"\\begin\{translation\}(.*?)\\end\{translation\}", raw, re.S)
    rx = re.compile(r"\\begin\{(verse|instrumental|sidenote)\}(?:\{((?:[^{}]|\{[^{}]*\})*)\})?(?:\[[^\]]*\])?(.*?)\\end\{\1\}|\\repetition\{((?:[^{}]|\{[^{}]*\})*)\}", re.S)
    for b in rx.finditer(song_part):
        if b.group(4) is not None:
            name = text(b.group(4)).strip()
            body.append("{chorus: " + name + "}" if is_chorus(name) else "{comment: " + name + " (repetir)}")
            body.append("")
            continue
        kind, name, content = b.group(1), text(b.group(2) or "").strip(), b.group(3)
        if kind == "sidenote":
            note = re.sub(r"\s+", " ", text(content)).strip()
            if note: body.append("{comment: " + note + "}"); body.append("")
            continue
        if kind == "instrumental":
            rows = [measures(r) for r in re.split(r"\\\\|\n", content)]
            rows = [r for r in rows if r and any(c.startswith("[") for c in r)]
            if not rows: continue
            body.append("{comment: " + (name or "Instrumental") + "}")
            for r in rows: body.append("| " + " | ".join(r) + " |")
            body.append("")
            continue
        env = "chorus" if is_chorus(name) else "verse"
        body.append("{start_of_" + env + (": " + name if name else "") + "}")
        for row in re.split(r"\\\\", content):
            row = row.strip()
            if not row: continue
            l = line_to_cho(row.replace("\n", " "), defines)
            if l: body.append(l)
        body.append("{end_of_" + env + "}")
        body.append("")
    if tr:
        body.append("{start_of_verse: Vertaling (NL)}")
        for para in re.split(r"\\vspace\{\\wlskip\}", tr.group(1)):
            for row in re.split(r"\\\\", para):
                l = re.sub(r"\s+", " ", text(row)).strip()
                if l: body.append(l)
            body.append("")
        while body and body[-1] == "": body.pop()
        body.append("{end_of_verse}")
        body.append("")
    defs = ["{define: " + c + " base-fret 1 frets " + f + "}" for c, f in defines.items()]
    while body and body[-1] == "": body.pop()
    if not any("[" in l and not l.startswith("{") for l in body): return None
    return "\n".join(head + defs + [""] + body) + "\n"

done, skipped = [], []
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".tex"): continue
    cho = convert(open(os.path.join(SRC, f), encoding="utf-8", errors="replace").read())
    if cho:
        open(os.path.join(OUT, f[:-4] + ".cho"), "w", encoding="utf-8").write(cho); done.append(f)
    else: skipped.append(f)
print("converted", len(done), "| skipped", len(skipped), skipped)
