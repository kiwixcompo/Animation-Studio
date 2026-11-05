"""takes/NN.wav + LINES.tsv -> VO.wav + VO.tsv, with the approved pace and pauses applied automatically

    python scripts/vo_join.py takes LINES.tsv --out VO              # preset chosen from the script
    python scripts/vo_join.py parler_out/takes LINES.tsv --out VO   # Hindi/Indian: same command

Presets, approved by ear by the reviewer (2026-10-20). The script's text picks one:
  indian   (any Indian script: Hindi, Bengali, Tamil, ...; voiced with Indic Parler, `natural` description)
           tempo 1.0 (the voice's own speed), every gap +0.3 s
  foreign  (English and every other language; Kokoro speed 1.0)
           tempo 1.0, every gap +0.35 s                ->  about 3.0 words/s with clear breathing room
The long final gap (>= 1.0 s) is never extended. Override with --preset, --tempo or --pause-add.

Why: Hindi used to be sped up 1.10x, and any line under 2.8 words/s up to 1.25x. Every first Hindi
film then sounded rushed and robotic, line by line. What the reviewer approved instead: no speed-up
at all, a relaxed conversational Parler description (make_parler_job.py `natural`) and longer pauses.
A line that drags or sounds flat is RE-MADE (new seed), never sped up. Kokoro at speed 1.1 sounded
too fast in English; speed 1.0 with the longer pauses was approved.

The joined VO is levelled to -16 LUFS (true peak -1.5 dB), whatever level the speaker came out at.

LINES.tsv columns: id, text, gap (the BASE pause after the line: 0.2 inside a thought, 0.3-0.5 at a
full stop or question, 1.2 after the last line). Each take is trimmed of its leading and trailing
silence first, so the gaps (plus the preset) are the only pauses.
"""
import argparse, csv, os, subprocess, tempfile
import numpy as np, soundfile as sf

SR = 44100
FLOOR = 0.004          # below this |amplitude| counts as silence


def trim(a):
    loud = np.abs(a) > FLOOR
    if not loud.any():
        return a[:0]
    return a[np.argmax(loud):len(a) - np.argmax(loud[::-1])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("takes", help="folder with one wav per line, named by id (01.wav ...)")
    ap.add_argument("lines", help="LINES.tsv: id, text, gap")
    ap.add_argument("--out", default="VO", help="writes <out>.wav and <out>.tsv")
    ap.add_argument("--preset", choices=["auto", "indian", "foreign", "none"], default="auto")
    ap.add_argument("--tempo", type=float, help="override the preset's speed (pitch kept)")
    ap.add_argument("--pause-add", type=float, help="override the preset's extra seconds per gap")
    a = ap.parse_args()
    with open(a.lines, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="	"))
    preset = a.preset
    if preset == "auto":
        preset = "indian" if any(ord(c) > 0x900 for r in rows for c in r["text"]) else "foreign"
    tempo0, add0 = {"indian": (1.0, 0.3), "foreign": (1.0, 0.35), "none": (1.0, 0.0)}[preset]
    a.tempo = a.tempo if a.tempo is not None else tempo0
    add = a.pause_add if a.pause_add is not None else add0
    print(f"preset {preset}: tempo {a.tempo}, pauses +{add}s")
    takes = a.takes
    if abs(a.tempo - 1) > 1e-3:
        tmp = tempfile.mkdtemp(prefix="vo_tempo_")
        for f in os.listdir(a.takes):
            if f.endswith(".wav"):
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(a.takes, f),
                                "-af", f"atempo={a.tempo}", os.path.join(tmp, f)], check=True)
        takes = tmp
    with open(a.lines, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    track, out, t = [], [], 0.0
    for r in rows:
        x, sr = sf.read(f"{takes}/{r['id']}.wav", dtype="float32")
        if x.ndim > 1:
            x = x.mean(axis=1)
        if sr != SR:
            n = int(len(x) * SR / sr)
            x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
        x = trim(x)
        gap = float(r.get("gap") or 0.4)
        gap = gap if gap >= 1.0 else gap + add
        out.append((r["id"], round(t, 3), round(len(x) / SR, 3), r["text"]))
        track += [x, np.zeros(int(gap * SR), np.float32)]
        t += len(x) / SR + int(gap * SR) / SR
    # Parler speakers come out at very different levels (Divya -32.6 LUFS, Aman -17.5): bring every VO to
    # -16 LUFS so it can be heard on its own. Same length, so VO.tsv timings stay exact.
    raw = os.path.join(tempfile.mkdtemp(prefix="vo_join_"), "raw.wav")
    sf.write(raw, np.concatenate(track), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", str(SR), "-ac", "1", f"{a.out}.wav"], check=True)
    with open(f"{a.out}.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["id", "start", "dur", "text"])
        w.writerows(out)
    speech = sum(o[2] for o in out)
    words = sum(len(o[3].split()) for o in out)
    pace = words / speech if speech else 0
    print(f"wrote {a.out}.wav ({t:.2f}s, {len(out)} lines) and {a.out}.tsv; pace {pace:.2f} words/s")
    # A take far slower than the film's own pace is a Parler glitch (stretched words), not a style.
    # Speeding it up is what made Hindi robotic, so name it for a re-make instead.
    for i, _, d, text in out:
        p = len(text.split()) / d if d else 0
        if pace and 0 < p < 0.7 * pace:
            print(f"RE-MAKE line {i}: {p:.2f} words/s against {pace:.2f} for the film - it drags. "
                  f"Voice only this id again with another seed; do not speed it up.")


if __name__ == "__main__":
    z = np.zeros(10, np.float32)
    assert len(trim(np.concatenate([z, np.ones(5, np.float32), z]))) == 5
    main()
