"""
Animation Video Pipeline Coordinator
Assembles the complete pipeline: Script Parsing -> Voice Synthesis (Edge Neural)
-> Word Alignment -> Scene & Sticker Asset Generation -> Final Composited MP4.
"""
import csv, os, re, shutil, subprocess
from typing import Callable, Dict, List, Optional
from voice_engine import generate_voice_takes
from art_engine import generate_scene_image, generate_sticker_badge

class VideoPipeline:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        os.makedirs(self.project_dir, exist_ok=True)
        self.takes_dir = os.path.join(self.project_dir, "takes")
        self.img_dir = os.path.join(self.project_dir, "img")
        self.elements_dir = os.path.join(self.project_dir, "elements", "cut")
        os.makedirs(self.takes_dir, exist_ok=True)
        os.makedirs(self.img_dir, exist_ok=True)
        os.makedirs(self.elements_dir, exist_ok=True)

    def prepare_script_lines(self, script_text: str, custom_title: str) -> List[Dict]:
        """
        Parses user script text into pacing lines (LINES.tsv).
        """
        raw_lines = [l.strip() for l in script_text.splitlines() if l.strip() and not l.startswith("#")]
        processed_lines = []
        for line in raw_lines:
            # Split long sentences into digestible 10-18 word clauses for punchy explainer pacing
            clauses = re.split(r'(?<=[.?!])\s+', line)
            for c in clauses:
                c = c.strip()
                if c:
                    processed_lines.append(c)

        lines_tsv = os.path.join(self.project_dir, "LINES.tsv")
        rows = []
        with open(lines_tsv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "text", "gap"], delimiter="\t")
            writer.writeheader()
            for idx, text in enumerate(processed_lines, start=1):
                row = {"id": str(idx), "text": text, "gap": "0.35"}
                writer.writerow(row)
                rows.append(row)
        return rows

    def generate_voiceover(self, voice_id: str, rate: str = "+0%", pitch: str = "+0Hz", callback: Optional[Callable] = None):
        lines_tsv = os.path.join(self.project_dir, "LINES.tsv")
        generate_voice_takes(lines_tsv, self.takes_dir, voice=voice_id, rate=rate, pitch=pitch, progress_callback=callback)

        # Run vo_join to concatenate takes into VO.wav & VO.tsv
        vo_join_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills", "vox-doc-sound", "scripts", "vo_join.py"))
        cmd = [
            "python", vo_join_script,
            "takes", "LINES.tsv"
        ]
        subprocess.run(cmd, cwd=self.project_dir, check=True)

        # Generate WORDS.tsv for forced word timing
        self._generate_words_tsv()

    def _generate_words_tsv(self):
        vo_tsv = os.path.join(self.project_dir, "VO.tsv")
        words_tsv = os.path.join(self.project_dir, "WORDS.tsv")
        with open(vo_tsv, "r", encoding="utf-8") as f:
            lines = list(csv.DictReader(f, delimiter="\t"))

        word_rows = []
        for row in lines:
            line_id = int(row["id"])
            start_t = float(row["start"])
            dur = float(row["dur"])
            text = row["text"].strip('"')
            tokens = [w for w in re.split(r'\s+', text) if w]
            if not tokens:
                continue
            w_dur = dur / len(tokens)
            for i, tok in enumerate(tokens):
                w_start = start_t + (i * w_dur)
                w_end = w_start + w_dur
                clean_w = re.sub(r'^[^\w]+|[^\w]+$', '', tok)
                word_rows.append({
                    "line": line_id,
                    "i": i,
                    "word": clean_w,
                    "start": round(w_start, 3),
                    "end": round(w_end, 3)
                })

        with open(words_tsv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["line", "i", "word", "start", "end"], delimiter="\t")
            writer.writeheader()
            writer.writerows(word_rows)

    def generate_visual_assets(self, title: str, format_type: str, style_name: str, callback: Optional[Callable] = None):
        lines_tsv = os.path.join(self.project_dir, "LINES.tsv")
        with open(lines_tsv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))

        total = len(rows)
        scene_rows = []

        for idx, r in enumerate(rows, start=1):
            lid = int(r["id"])
            text = r["text"]
            # Generate 16:9 scene illustration
            shot_name = f"s{lid:02d}.jpg"
            shot_path = os.path.join(self.img_dir, shot_name)
            generate_scene_image(lid, title, text, format_type, style_name, shot_path)

            # Generate overlay sticker badge
            elem_name = f"{lid}.png"
            elem_path = os.path.join(self.elements_dir, elem_name)
            first_word = text.split()[0] if text.split() else f"KEY{lid}"
            generate_sticker_badge(lid, first_word, elem_path)

            # Record scene schedule
            scene_rows.append({"cue": f"{lid}.0", "img": f"img/{shot_name}", "text": "", "pos": "", "extra": ""})
            scene_rows.append({"cue": f"+{lid}.4", "img": f"elements/cut/{elem_name}", "text": "", "pos": "0.8,0.3,0.35", "extra": "pop"})
            
            if callback:
                callback(idx, total, f"Generated visual scene {idx}/{total}")

        # Write SCENES.tsv
        scenes_tsv = os.path.join(self.project_dir, "SCENES.tsv")
        with open(scenes_tsv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["cue", "img", "text", "pos", "extra"], delimiter="\t")
            writer.writeheader()
            writer.writerows(scene_rows)

    def render_final_video(self) -> str:
        render_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills", "stickman-hybrid", "scripts", "render.py"))
        cmd = ["python", render_py]
        subprocess.run(cmd, cwd=self.project_dir, check=True)
        
        # Locate the produced mp4
        files = [f for f in os.listdir(self.project_dir) if f.endswith(".mp4")]
        if files:
            return os.path.join(self.project_dir, files[0])
        raise RuntimeError("Render completed but MP4 output was not found.")
