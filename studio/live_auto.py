"""Free, fully automatic live clipping without an AI key (added by Ahmad Dev).

Used by live.py when no AI is set up, or when the AI fails. It looks at the same moments the AI would be asked
about (a jump in loudness or chat, someone saying "clip", the regular check) and picks a clip from local signals:
loudness peaks and reaction words. Each clip is a complete arc: it starts at the beginning of a sentence with a
few seconds of setup, runs past the peak to the end of the payoff sentence, and ends 0.5-1.5 s after the last
word (longer while the audio is still loud), never cutting into the next word.
"""
import re

import numpy as np

REACT = {"oh my god": 3, "omg": 3, "no way": 3, "what the": 3, "holy": 3, "let's go": 3, "lets go": 3, "insane": 2.5,
         "crazy": 2, "bro": 1.5, "bruh": 2, "yo": 1.5, "wait": 1.5, "wow": 2, "oh no": 2.5, "haha": 2.5, "lmao": 2.5,
         "clip": 3, "chat": 1, "damn": 2, "nah": 1.5, "run": 1.2, "help": 1.5, "gg": 2, "shut up": 2,
         "yaar": 1.5, "bhai": 1.5, "arre": 2, "wah": 2, "kya": 1.2, "pagal": 2, "abe": 2}
END = ".?!"
WEAK = {"so", "and", "um", "uh", "but", "like", "because", "or", "then", "yeah", "okay", "ok"}


def _n(w):
    return re.sub(r"[^\w']+", "", w.lower())


def react(words):
    toks = [_n(w["w"]) for w in words]
    out = []
    for i, t in enumerate(toks):
        two = t + " " + toks[i + 1] if i + 1 < len(toks) else ""
        out.append(max(REACT.get(two, 0), REACT.get(t, 0)) + (1 if words[i]["w"].endswith("!") else 0))
    return out


def sentences(words, gap=0.6):
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and (w["s"] - words[i - 1]["e"] >= gap or words[i - 1]["w"][-1:] in END):
            out.append(cur)
            cur = []
        cur.append(i)
    if cur:
        out.append(cur)
    return [{"i0": c[0], "i1": c[-1], "s": words[c[0]]["s"], "e": words[c[-1]]["e"]} for c in out]


def hook_for(words):
    best, bs = None, -1.0
    for s in sentences(words):
        part = words[s["i0"]:s["i1"] + 1]
        if 2 <= len(part) <= 9:
            sc = sum(react(part)) + (1 if part[-1]["w"].endswith(("!", "?")) else 0)
            if sc > bs:
                best, bs = " ".join(w["w"] for w in part), sc
    best = best or " ".join(w["w"] for w in words[:7])
    return re.sub(r"[\"{}\\]", "", best).strip(" ,.;:-").upper()[:60]


def pick(words, db, ws, now, min_len, max_len, peak=None, need_signal=True):
    """One clip in [ws, now] (stream seconds) or None. db: loudness per second of the whole stream so far."""
    win = [w for w in words if ws - 30 <= w["s"] <= now]
    if len(win) < 8:
        return None
    db = np.asarray(db, dtype=np.float32)
    z = (db - np.median(db)) / (db.std() + 1e-6) if len(db) > 5 else np.zeros(len(db))
    lo, hi = max(0, int(ws)), min(len(z), int(now) + 1)
    if hi - lo < 5:
        return None
    hits = react(win)
    score = z[lo:hi].copy()
    for w, h in zip(win, hits):
        k = int(w["s"]) - lo
        if 0 <= k < len(score) and h:
            score[max(0, k - 1):k + 3] += h
    if peak is None:
        k = int(np.argmax(score))
        if need_signal and score[k] < 2.0:          # a calm stretch: nothing stood out, no clip
            return None
        peak = lo + k + 0.5
    sents = sentences(win)
    pk = next((i for i, s in enumerate(sents) if s["e"] >= peak), len(sents) - 1)
    first, setup = pk, min(max(0.35 * min_len, 5), 18)
    while first > 0 and peak - sents[first]["s"] < setup:
        first -= 1
    while first < pk and _n(win[sents[first]["i0"]]["w"]) in WEAK and peak - sents[first + 1]["s"] >= 3:
        first += 1
    s0 = sents[first]["s"]
    last = pk
    while last + 1 < len(sents) and sents[last + 1]["e"] <= now and (sents[last]["e"] < peak + 2 or sents[last]["e"] - s0 < min_len):
        if sents[last + 1]["e"] - s0 > max_len + 8:
            break
        last += 1
    while sents[last]["e"] - sents[first]["s"] > max_len + 8 and first < pk:
        first += 1
    i0, i1 = sents[first]["i0"], sents[last]["i1"]
    start, e = max(0.0, win[i0]["s"] - 0.12), win[i1]["e"]
    if e - start < min(min_len, 8):
        return None
    nxt = win[i1 + 1]["s"] if i1 + 1 < len(win) else e + 5
    loud_floor = float(np.percentile(db, 60)) if len(db) else -30
    tail = 0.5
    for t in range(int(e) + 1, min(len(db), int(e) + 2)):
        if db[t] > loud_floor:
            tail = 1.5
    end = min(e + max(0.15, min(tail, nxt - e - 0.08)), now)
    part = win[i0:i1 + 1]
    hook = hook_for(part)
    return {"start": round(start, 2), "end": round(end, 2), "score": int(min(99, 50 + 10 * float(score.max()))),
            "category": "other", "hook": hook, "title": hook.title()[:90], "description": "", "hashtags": [],
            "highlight_words": [w["w"] for w, h in zip(part, react(part)) if h >= 2][:4]}
