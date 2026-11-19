"""Builds the picture previews in web/brand/pv-*.jpg|mp4 with PeakCut's own renderer (added by Ahmad Dev).

Usage: python scripts/make_previews.py
The source video is drawn in code (a game frame with a webcam box), so the previews are free to ship.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from studio import config, render  # noqa: E402
from studio import styles_plus as plus  # noqa: E402

OUT = ROOT / "web" / "brand"
FONT = "studio/fonts/inter-800.ttf"
HOOK = "HE DID NOT SEE THAT COMING"
WORDS = [{"w": w, "s": 0.3 + i * 0.32, "e": 0.3 + i * 0.32 + 0.3}
         for i, w in enumerate("No way he actually did that bro this is insane".split())]


def ff(*a, cwd=ROOT):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *map(str, a)], check=True, cwd=cwd)


def still(mp4, t, dst, w=270):
    ff("-ss", t, "-i", mp4, "-frames:v", "1", "-vf", f"scale={w}:-2", "-q:v", "3", dst)


def main():
    render.install_fonts()
    work = Path(tempfile.mkdtemp(prefix="pv"))
    src, logo = work / "src.mp4", work / "logo.png"
    vf = ("drawbox=x=0:y=470:w=1280:h=250:color=0x2e7d32:t=fill,drawbox=x=560:y=300:w=160:h=200:color=0xc0392b:t=fill,"
          "drawbox=x=900:y=380:w=90:h=120:color=0xf1c40f:t=fill,"
          f"drawtext=fontfile={FONT}:text=GAMEPLAY:fontsize=60:fontcolor=white@0.85:x=(w-tw)/2:y=600,"
          "drawbox=x=0:y=0:w=384:h=216:color=0x34495e:t=fill,drawbox=x=150:y=40:w=84:h=84:color=0xf5cba7:t=fill,"
          "drawbox=x=120:y=130:w=144:h=86:color=0x5d6d7e:t=fill,"
          f"drawtext=fontfile={FONT}:text=FACECAM:fontsize=28:fontcolor=white:x=130:y=10,format=yuv420p")
    ff("-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x1e3c72:c1=0x7f53ac:x0=0:y0=0:x1=1280:y1=720:d=4:r=30",
       "-f", "lavfi", "-i", "sine=f=220:d=4", "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-t", "4", src)
    ff("-f", "lavfi", "-i", "color=c=0x00000000:s=600x200,format=rgba", "-vf",
       f"drawtext=fontfile={FONT}:text=YOUR LOGO:fontsize=96:fontcolor=0xFFD60A:x=(w-tw)/2:y=(h-th)/2:borderw=6",
       "-frames:v", "1", logo)
    clip = {"start": 0.0, "end": 3.9, "hook": HOOK, "style": "bounce", "facecam": [0, 0, 384, 216], "logo": str(logo)}
    for lay in render.LAYOUTS:
        out = render.render_clip(src, work, f"l_{lay}", dict(clip, layout=lay), WORDS, 1280, 720)
        still(work / out["file"], 1.7, OUT / f"pv-layout-{lay}.jpg")
        print("layout", lay)
    # caption looks, hook lines and intros: rendered the same way on a captionless crop frame
    bg = render.render_clip(src, work, "bg", dict(clip, layout="crop", hook="", captions=False), [], 1280, 720)
    for k in plus.PRESETS:
        r = render.render_clip(src, work, f"c_{k}", dict(clip, layout="crop", hook="", style=k), WORDS, 1280, 720)
        ff("-i", work / r["file"], "-ss", "1.0", "-frames:v", "1", "-vf", "crop=1080:420:0:1170,scale=360:-2", "-q:v", "3",
           OUT / f"pv-caption-{k}.jpg")
        print("caption", k)
    for k in plus.FORMATS:
        r = render.render_clip(src, work, f"f_{k}", dict(clip, layout="crop", captions=False, hook_format=k), [], 1280, 720)
        ff("-i", work / r["file"], "-ss", "1.0", "-frames:v", "1", "-vf", "crop=1080:420:0:90,scale=360:-2", "-q:v", "3",
           OUT / f"pv-format-{k}.jpg")
        print("format", k)
    for k in plus.INTROS:
        if k == "none":
            shutil.copyfile(OUT / "pv-layout-gameplay.jpg", OUT / "pv-intro-none.jpg")
            continue
        r = render.render_clip(src, work, f"i_{k}", dict(clip, layout="gameplay", hook_intro=k), WORDS, 1280, 720)
        ff("-i", work / r["file"], "-t", "3.6", "-vf", "scale=360:-2", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "28", "-c:a", "aac", "-b:a", "64k", OUT / f"pv-intro-{k}.mp4")
        still(work / r["file"], 0.3 if k == "countdown" else 1.0, OUT / f"pv-intro-{k}.jpg")
        print("intro", k)
    shutil.rmtree(work, ignore_errors=True)
    del bg


if __name__ == "__main__":
    main()
