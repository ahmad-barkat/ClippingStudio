"""Extra styles added by Ahmad Dev: 16 caption looks, hook line formats, hook intros, and the streamer-stack and
logo layouts (the layouts themselves live in render.py next to the original ones).

Caption looks:
- Clipping: "Stack yellow" (2 words, current word yellow) and "Clean white".
- Nafay: the 7 caption looks of the Nafay 3D style library (fonts and colours of each style).
- Faceless: the caption rules of 7 faceless-shorts styles (keyword colour, typewriter, paper strip, dark bar, one
  word at a time...).
Hook intros (drawn in code, free to use): peak tease, flash punch, countdown, glitch.
"""
import re
import subprocess
from pathlib import Path

from .media import NO_WINDOW

W, H = 1080, 1920

P = lambda **k: k  # noqa: E731
PRESETS = {
    "stack-yellow": P(label="Stack yellow", font="Arial Black", size=76, col="#FFFFFF", hi="#FFE600", outl="#000000",
                      bord=6, shad=2, case="upper", words=2, mode="karaoke"),
    "clean-white": P(label="Clean white", font="CVE inter-800", size=72, col="#FFFFFF", hi="#FFFFFF", outl="#000000",
                     bord=5, shad=2, case="upper", words=3, mode="plain"),
    "creator-motion-graphics": P(label="Creator Motion", font="CVE inter-800", size=74, col="#f4f1ea", hi="#ffd60a",
                                 outl="#000000", bord=4, shad=3, case="upper", words=4, mode="karaoke"),
    "warm-canvas": P(label="Warm Canvas", font="CVE fraunces-600", size=80, col="#ffffff", hi="#4f9cf0", outl="#000000",
                     bord=4, shad=3, case="asis", words=4, mode="karaoke"),
    "clean-tech": P(label="Clean Tech", font="CVE inter-tight-800", size=74, col="#ffffff", hi="#7d9bff", outl="#0d0f14",
                    bord=4, shad=3, case="asis", words=4, mode="karaoke"),
    "software-walkthrough": P(label="Walkthrough", font="CVE dm-sans-700", size=72, col="#ffffff", hi="#9b9bff",
                              outl="#14161c", bord=4, shad=3, case="asis", words=4, mode="karaoke"),
    "data-story": P(label="Data Story", font="CVE archivo-800", size=74, col="#eef1f5", hi="#ff6b5b", outl="#0f141c",
                    bord=4, shad=3, case="asis", words=4, mode="karaoke"),
    "chalk-talk": P(label="Chalk Talk", font="CVE kalam-700", size=82, col="#f2efe6", hi="#f4d35e", outl="#24392f",
                    bord=4, shad=2, case="asis", words=4, mode="karaoke"),
    "pop-info": P(label="Pop Info", font="CVE fredoka-700", size=78, col="#ffffff", hi="#ffd86b", outl="#2f3e46",
                  bord=5, shad=0, case="asis", words=4, mode="karaoke"),
    "deep-dive": P(label="Deep Dive", font="CVE inter-800", size=96, col="#FFFFFF", hi="#FFD60A", outl="#111111",
                   bord=6, shad=3, case="sentence", words=3, mode="keyword"),
    "inside-out": P(label="Inside Out", font="CVE inter-800", size=128, col="#FFFFFF", hi="#FFD60A", outl="#14141e",
                    bord=11, shad=4, case="upper", words=2, mode="keyword"),
    "night-file": P(label="Night File", font="Courier New", size=74, col="#F2E8D5", hi="#E03131", outl="#000000",
                    bord=3, shad=2, case="sentence", words=4, mode="type", bold=1),
    "paper-atlas": P(label="Paper Atlas", font="CVE fraunces-700", size=70, col="#2B2118", hi="#A4161A", outl="#EADBC0",
                     bord=14, shad=3, case="sentence", words=4, mode="keyword", box=True),
    "scale-lab": P(label="Scale Lab", font="CVE inter-800", size=84, col="#FFFFFF", hi="#FFFFFF", outl="#1a1a1a",
                   bord=3, shad=4, case="sentence", words=3, mode="plain"),
    "stick-story": P(label="Stick Story", font="CVE inter-800", size=72, col="#FFFFFF", hi="#F5B700", outl="#1E1E24",
                     bord=16, shad=0, case="sentence", words=4, mode="keyword", box=True),
    "tall-tale": P(label="Tall Tale", font="CVE inter-800", size=118, col="#FFFFFF", hi="#FFFFFF", outl="#000000",
                   bord=7, shad=4, case="asis", words=1, mode="plain"),
}
FORMATS = {"auto": "Auto (from the clip)", "pov": "POV: ...", "wait": "Wait for it...", "end": "Watch till the end",
           "question": "Question"}
INTROS = {"none": "No intro", "tease": "Peak tease", "flash": "Flash punch", "countdown": "Countdown", "glitch": "Glitch"}
SPEECH = {"auto": "Auto", "hi": "Hindi", "ur": "Urdu"}
REACT = {"oh my god": 3, "no way": 3, "what the": 3, "holy": 3, "let's go": 3, "insane": 2.5, "crazy": 2, "bro": 1.5,
         "bruh": 2, "wait": 1.5, "wow": 2, "oh no": 2.5, "haha": 2.5, "lmao": 2.5, "damn": 2, "yaar": 1.5, "bhai": 1.5,
         "arre": 2, "wah": 2, "kya": 1.2, "pagal": 2}


def hook_text(fmt, hook):
    hook = (hook or "").strip().rstrip(".!?, ")
    return {"pov": f"POV: {hook}", "wait": "WAIT FOR IT...", "end": "WATCH TILL THE END",
            "question": f"{hook}?"}.get(fmt or "auto", hook)


def _color(hexcol, alpha=0):
    h = hexcol.lstrip("#")
    return f"&H{alpha:02X}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def _ts(t):
    cs = int(round(max(t, 0) * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def _esc(t):
    return t.replace("\\", "").replace("{", "(").replace("}", ")")


def _norm(w):
    return re.sub(r"[^\w']+", "", w.lower())


def _hits(g):
    toks = [_norm(w["w"]) for w in g]
    out = []
    for i, t in enumerate(toks):
        two = t + " " + toks[i + 1] if i + 1 < len(toks) else ""
        out.append(max(REACT.get(two, 0), REACT.get(t, 0)) + (1 if g[i]["w"].endswith("!") else 0))
    return out


def style_line(name, font, size, col, outl, bord, shad, box=False, bold=0):
    return (f"Style: {name},{font},{int(size)},{_color(col)},{_color(col)},{_color(outl)},{_color('#000000', 0x80)},"
            f"{bold},0,0,0,100,100,0,0,{3 if box else 1},{bord:.1f},{shad:.1f},5,60,60,0,1")


def caption_style(preset):
    p = PRESETS[preset]
    return style_line("C", p["font"], p["size"], p["col"], p["outl"], p["bord"], p["shad"], p.get("box", False),
                      p.get("bold", 0))


def _chunks(words, n, max_chars=22, gap=0.5):
    out, cur = [], []
    for w in words:
        if cur:
            chars = sum(len(x["w"]) + 1 for x in cur) + len(w["w"])
            if len(cur) >= n or chars > max_chars or w["s"] - cur[-1]["e"] > gap or cur[-1]["w"][-1:] in ".?!,":
                out.append(cur)
                cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    if n == 1:  # one word at a time, but tiny words pair with the next ("a single")
        merged = []
        for c in out:
            if merged and len(merged[-1]) == 1 and len(merged[-1][0]["w"]) <= 2 and c[0]["s"] - merged[-1][0]["e"] < 0.3:
                merged[-1] = merged[-1] + c
            else:
                merged.append(c)
        out = merged
    return out


def caption_events(words, dur, preset, cy):
    """words: [{w, s, e}] in clip time (already Roman letters for Hindi/Urdu)."""
    p = PRESETS[preset]
    hi, col = _color(p["hi"]), _color(p["col"])
    pos = f"\\pos({W // 2},{cy:.0f})"
    ev = []
    groups = _chunks(words, p["words"])
    for gi, g in enumerate(groups):
        texts = [_esc(w["w"].upper() if p["case"] == "upper" else w["w"]) for w in g]
        if p["case"] == "sentence" and texts:
            texts[0] = texts[0][:1].upper() + texts[0][1:]
        g_end = g[-1]["e"] + 0.35
        if gi + 1 < len(groups):
            g_end = min(g_end, groups[gi + 1][0]["s"])
        g_end = min(max(g_end, g[-1]["e"]), dur)
        hits = _hits(g)
        kw = max(range(len(g)), key=lambda j: (hits[j], len(g[j]["w"])))
        mark = lambda j, t: ("{\\c" + hi + "}" + t + "{\\c" + col + "}") if j == kw else t  # noqa: E731
        if p["mode"] == "karaoke":
            for i, w in enumerate(g):
                s = w["s"] if i else g[0]["s"]
                e = g[i + 1]["s"] if i + 1 < len(g) else g_end
                if e - s < 0.04:
                    continue
                parts = [("{\\c" + hi + "}" + t + "{\\c" + col + "}") if j == i else t for j, t in enumerate(texts)]
                ev.append(f"Dialogue: 1,{_ts(s)},{_ts(e)},C,,0,0,0,,{{{pos}}}" + " ".join(parts))
        elif p["mode"] == "keyword":
            parts = [mark(j, t) if len(g) > 1 or hits[0] > 0 else t for j, t in enumerate(texts)]
            ev.append(f"Dialogue: 1,{_ts(g[0]['s'])},{_ts(g_end)},C,,0,0,0,,{{{pos}\\fad(40,0)}}" + " ".join(parts))
        elif p["mode"] == "type":  # typewriter: letters appear, the hidden rest keeps the line centred
            full = " ".join(texts)
            span = max(min(g[-1]["e"] - g[0]["s"], len(full) * 0.045), 0.2)
            step = span / max(len(full), 1)
            for n in range(1, len(full) + 1):
                s = g[0]["s"] + (n - 1) * step
                e = g[0]["s"] + n * step if n < len(full) else g_end
                if e <= s:
                    continue
                shown, out, idx = full[:n], [], 0
                for j, t in enumerate(texts):
                    seg = shown[idx:idx + len(t)]
                    if seg:
                        out.append(mark(j, seg))
                    idx += len(t) + 1
                rest = full[n:]
                ev.append(f"Dialogue: 1,{_ts(s)},{_ts(e)},C,,0,0,0,,{{{pos}}}" + " ".join(out)
                          + ("{\\alpha&HFF&}" + rest if rest else ""))
        else:
            ev.append(f"Dialogue: 1,{_ts(g[0]['s'])},{_ts(g_end)},C,,0,0,0,,{{{pos}\\fad(40,0)}}" + " ".join(texts))
    return ev


# ---- hook intros ----------------------------------------------------------------------------------------------

def _run(cmd, cwd):
    p = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", creationflags=NO_WINDOW, timeout=600)
    if p.returncode:
        raise RuntimeError("intro failed: " + p.stderr[-600:])


def make_intro(kind, text, work: Path, name="intro"):
    """A 2 s intro drawn in code (flash / countdown / glitch), 1080x1920 with sound. Fonts are in work/f."""
    text = _esc(text or "WAIT FOR IT...").replace("\n", "\\N")
    cx, cy, d = W // 2, H // 2, 2.0
    if kind == "countdown":
        ev = [f"Dialogue: 0,{_ts(i * 0.62)},{_ts(i * 0.62 + 0.6)},N,,0,0,0,,{{\\pos({cx},{cy})\\fscx140\\fscy140"
              f"\\t(0,180,\\fscx100\\fscy100)\\fad(0,80)}}{n}" for i, n in enumerate("321")]
        v = f"color=c=0x101425:s={W}x{H}:d={d}:r=30,vignette"
        a = (f"sine=f=880:d={d}:r=48000,volume='if(lt(mod(t\\,0.62)\\,0.12)\\,0.5\\,0)':eval=frame,"
             "aformat=channel_layouts=stereo")
    elif kind == "glitch":
        ev = [f"Dialogue: 0,0:00:00.00,{_ts(d)},B,,0,0,0,,{{\\pos({cx},{cy})\\c&H00E6FF&"
              + "".join(f"\\t({i * 90},{i * 90 + 45},\\frz{(-3 if i % 2 else 3)})" for i in range(22)) + f"}}{text}"]
        v = f"color=c=0x202020:s={W}x{H}:d={d}:r=30,noise=alls=70:allf=t+u,rgbashift=rh=-12:bh=12,eq=contrast=1.3"
        a = f"anoisesrc=d={d}:c=white:r=48000:a=0.18,highpass=f=900,aformat=channel_layouts=stereo"
    else:  # flash
        ev = [f"Dialogue: 0,0:00:00.12,{_ts(d)},B,,0,0,0,,{{\\pos({cx},{cy})\\fscx260\\fscy260"
              f"\\t(0,220,\\fscx100\\fscy100)\\t(1500,1880,\\fscx112\\fscy112)}}{text}"]
        v = f"color=c=black:s={W}x{H}:d={d}:r=30,format=yuv420p,geq=lum='if(lt(T\\,0.12)\\,255\\,lum(X\\,Y))':cb=128:cr=128"
        a = f"anoisesrc=d={d}:c=pink:r=48000:a=0.5,lowpass=f=1800,volume='exp(-6*t)':eval=frame,aformat=channel_layouts=stereo"
    head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
            "MarginR, MarginV, Encoding\n"
            + style_line("B", "CVE inter-800", 150, "#FFFFFF", "#000000", 9, 4, bold=1) + "\n"
            + style_line("N", "CVE anton-400", 420, "#FFE600", "#000000", 14, 6) + "\n\n[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    (work / f"{name}.ass").write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
    _run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", v, "-f", "lavfi", "-i", a, "-vf",
          f"ass={name}.ass:fontsdir=f,format=yuv420p", "-t", f"{d}", "-c:v", "libx264", "-preset", "veryfast",
          "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", f"{name}.mp4"], work)
    return work / f"{name}.mp4"


def peak_time(src, start, end):
    """The loudest moment of a clip (seconds into the source), for the peak tease."""
    import numpy as np
    sr = 8000
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.2f}", "-t", f"{end - start:.2f}", "-i", str(src),
                        "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True,
                       creationflags=NO_WINDOW, timeout=300)
    x = np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32)
    n = sr // 2
    k = len(x) // n
    if k < 3:
        return (start + end) / 2
    rms = np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(1) + 1)
    return start + (int(np.argmax(rms[1:-1])) + 1) * 0.5 + 0.25


def join(intro: Path, clip: Path, out: Path):
    """intro + clip with a smooth audio join (short fades), re-encoded once."""
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(intro)],
                             capture_output=True, text=True, creationflags=NO_WINDOW).stdout.strip() or 2)
    fc = (f"[0:v]fps=30,scale={W}:{H},setsar=1,format=yuv420p[hv];[1:v]fps=30,scale={W}:{H},setsar=1,format=yuv420p[cv];"
          f"[0:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=out:st={max(d - 0.15, 0):.3f}:d=0.15[ha];"
          f"[1:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.08[ca];"
          f"[hv][ha][cv][ca]concat=n=2:v=1:a=1[v][a]")
    _run(["ffmpeg", "-y", "-v", "error", "-i", intro.name, "-i", clip.name, "-filter_complex", fc, "-map", "[v]",
          "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-c:a", "aac", "-b:a", "160k",
          "-movflags", "+faststart", out.name], out.parent)
